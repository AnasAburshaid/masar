"""Action service coordinating proposal validation, human approval, and controlled tool execution."""

import re
from typing import Any, Optional

from masar.application.interfaces.repositories.action_proposal_repository import (
    ActionProposalRepository,
)
from masar.application.services.tool_registry import ServicesBundle, ToolRegistry
from masar.domain.exceptions.action import (
    ActionProposalAccessDeniedError,
    ActionProposalAlreadyResolvedError,
    ActionProposalNotFoundError,
    InvalidActionParametersError,
)
from masar.domain.exceptions.base import InvalidIdError
from masar.domain.models.action import ActionProposal, ActionResult, ProposedAction


class ActionService:
    """Manages AI action proposal life cycle and dispatches approved tool executions."""

    def __init__(
        self,
        proposal_repository: ActionProposalRepository,
        tool_registry: ToolRegistry,
        services_bundle: ServicesBundle,
    ) -> None:
        self._repo = proposal_repository
        self._registry = tool_registry
        self._services = services_bundle

    def create_proposal(
        self,
        conversation_id: int,
        user_id: int,
        title: str,
        actions: list[ProposedAction],
    ) -> ActionProposal:
        """Validate proposed actions and persist a pending action proposal."""
        if conversation_id <= 0:
            raise InvalidIdError("Conversation ID must be a positive integer.")
        if user_id <= 0:
            raise InvalidIdError("User ID must be a positive integer.")

        # Validate that each proposed tool exists and mark destructive status
        enriched_actions: list[ProposedAction] = []
        for action in actions:
            tool = self._registry.get_tool(action.tool)
            # Enforce is_destructive from tool definition if not already flagged
            is_dest = action.is_destructive or tool.is_destructive
            enriched_actions.append(
                ProposedAction(
                    tool=action.tool,
                    parameters=action.parameters,
                    description=action.description or tool.description,
                    is_destructive=is_dest,
                )
            )

        proposal = ActionProposal(
            conversation_id=conversation_id,
            user_id=user_id,
            title=title,
            actions=enriched_actions,
            status="pending",
        )
        return self._repo.add_proposal(proposal)

    def get_proposal(self, proposal_id: int, user_id: int) -> ActionProposal:
        """Retrieve an action proposal verifying user ownership."""
        return self._verify_ownership(proposal_id, user_id)

    def list_proposals(self, conversation_id: int, user_id: int) -> list[ActionProposal]:
        """List all proposals for a conversation, filtering for user ownership."""
        proposals = self._repo.get_proposals_by_conversation_id(conversation_id)
        return [p for p in proposals if p.user_id == user_id]

    def reject_proposal(self, proposal_id: int, user_id: int) -> ActionProposal:
        """Reject a pending proposal upon user request."""
        proposal = self._verify_ownership(proposal_id, user_id)
        if proposal.status != "pending":
            raise ActionProposalAlreadyResolvedError(
                f"Cannot reject proposal {proposal_id} because its status is already '{proposal.status}'."
            )
        proposal.reject()
        return self._repo.update_proposal(proposal)

    def approve_and_execute_proposal(
        self, proposal_id: int, user_id: int
    ) -> tuple[ActionProposal, list[ActionResult]]:
        """Approve and execute a proposal's actions sequentially via application services."""
        proposal = self._verify_ownership(proposal_id, user_id)
        if proposal.status != "pending":
            raise ActionProposalAlreadyResolvedError(
                f"Cannot execute proposal {proposal_id} because its status is already '{proposal.status}'."
            )

        proposal.approve()
        results: list[ActionResult] = []
        execution_context: dict[int, dict[str, Any]] = {}

        for idx, action in enumerate(proposal.actions):
            try:
                # 1. Resolve dynamic parameter references (e.g. $0.journey.id, $prev.id)
                resolved_params = self._resolve_parameter_references(
                    action.parameters, idx, execution_context
                )

                # 2. Execute tool through application services
                output = self._registry.execute(
                    tool_name=action.tool,
                    parameters=resolved_params,
                    user_id=user_id,
                    services=self._services,
                )

                res = ActionResult(
                    action_index=idx,
                    tool=action.tool,
                    status="success",
                    data=output,
                )
                results.append(res)
                execution_context[idx] = output

            except Exception as exc:
                res = ActionResult(
                    action_index=idx,
                    tool=action.tool,
                    status="failure",
                    error=str(exc),
                )
                results.append(res)
                # Halt sequential execution on failure
                proposal.mark_failed(results)
                self._repo.update_proposal(proposal)
                return proposal, results

        # All proposed actions succeeded
        proposal.mark_executed(results)
        updated = self._repo.update_proposal(proposal)
        return updated, results

    def _resolve_parameter_references(
        self,
        parameters: dict[str, Any],
        current_index: int,
        context: dict[int, dict[str, Any]],
    ) -> dict[str, Any]:
        """Resolve dynamic references to outputs of earlier steps in the proposal sequence."""
        resolved: dict[str, Any] = {}
        for key, val in parameters.items():
            if isinstance(val, str) and val.startswith("$"):
                resolved[key] = self._resolve_single_reference(val, current_index, context)
            else:
                resolved[key] = val
        return resolved

    def _resolve_single_reference(
        self, ref_str: str, current_index: int, context: dict[int, dict[str, Any]]
    ) -> Any:
        """Resolve a reference string like '$0.id', '$0.journey.id', or '$prev.id'."""
        pattern = r"^\$([a-zA-Z0-9_]+)(\.(.+))?$"
        match = re.match(pattern, ref_str)
        if not match:
            return ref_str

        target_step_str = match.group(1)
        path = match.group(3) or ""

        target_idx: int
        if target_step_str == "prev":
            target_idx = current_index - 1
        elif target_step_str.isdigit():
            target_idx = int(target_step_str)
        else:
            return ref_str

        if target_idx not in context:
            raise InvalidActionParametersError(
                f"Cannot resolve reference '{ref_str}': Step {target_idx} has not executed yet."
            )

        data = context[target_idx]

        # Extract value along dotted path
        tokens = [t for t in path.split(".") if t]
        curr: Any = data
        for token in tokens:
            if isinstance(curr, dict) and token in curr:
                curr = curr[token]
            else:
                # Direct check if token is 'id' and curr is a dict with an entity
                # e.g., data is {"journey": {"id": 1}} and ref was "$0.id"
                found = False
                if isinstance(curr, dict):
                    for sub_k, sub_v in curr.items():
                        if isinstance(sub_v, dict) and token in sub_v:
                            curr = sub_v[token]
                            found = True
                            break
                if not found:
                    raise InvalidActionParametersError(
                        f"Cannot resolve reference '{ref_str}': attribute '{token}' not found in step {target_idx} output."
                    )
        return curr

    def _verify_ownership(self, proposal_id: int, user_id: int) -> ActionProposal:
        """Verify proposal existence and ownership."""
        if proposal_id <= 0:
            raise InvalidIdError("Proposal ID must be a positive integer.")
        if user_id <= 0:
            raise InvalidIdError("User ID must be a positive integer.")

        proposal = self._repo.get_proposal_by_id(proposal_id)
        if proposal is None:
            raise ActionProposalNotFoundError(f"Action proposal {proposal_id} not found.")
        if proposal.user_id != user_id:
            raise ActionProposalAccessDeniedError(
                f"User {user_id} does not have access to proposal {proposal_id}."
            )
        return proposal
