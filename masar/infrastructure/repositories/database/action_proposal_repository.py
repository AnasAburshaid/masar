"""SQLAlchemy implementation of ActionProposalRepository."""

import json
from sqlalchemy import select
from sqlalchemy.orm import Session

from masar.application.interfaces.repositories.action_proposal_repository import (
    ActionProposalRepository,
)
from masar.domain.models.action import ActionProposal, ActionResult, ProposedAction
from masar.infrastructure.database.models import ActionProposalModel


class SqlActionProposalRepository(ActionProposalRepository):
    """SQLAlchemy persistence adapter for Action Proposals."""

    def __init__(self, session: Session) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: ActionProposalModel) -> ActionProposal:
        raw_actions = json.loads(model.actions_json) if model.actions_json else []
        raw_results = json.loads(model.results_json) if model.results_json else []

        actions = [
            ProposedAction(
                tool=a["tool"],
                parameters=a.get("parameters", {}),
                description=a.get("description", ""),
                is_destructive=bool(a.get("is_destructive", False)),
            )
            for a in raw_actions
        ]

        results = [
            ActionResult(
                action_index=r["action_index"],
                tool=r["tool"],
                status=r["status"],
                data=r.get("data"),
                error=r.get("error"),
            )
            for r in raw_results
        ]

        return ActionProposal(
            id=model.id,
            conversation_id=model.conversation_id,
            user_id=model.user_id,
            title=model.title,
            status=model.status,
            actions=actions,
            results=results,
            created_at=model.created_at,
            resolved_at=model.resolved_at,
        )

    @staticmethod
    def _to_actions_json(actions: list[ProposedAction]) -> str:
        return json.dumps(
            [
                {
                    "tool": a.tool,
                    "parameters": a.parameters,
                    "description": a.description,
                    "is_destructive": a.is_destructive,
                }
                for a in actions
            ]
        )

    @staticmethod
    def _to_results_json(results: list[ActionResult]) -> str:
        return json.dumps(
            [
                {
                    "action_index": r.action_index,
                    "tool": r.tool,
                    "status": r.status,
                    "data": r.data,
                    "error": r.error,
                }
                for r in results
            ]
        )

    def add_proposal(self, proposal: ActionProposal) -> ActionProposal:
        model = ActionProposalModel(
            conversation_id=proposal.conversation_id,
            user_id=proposal.user_id,
            title=proposal.title,
            status=proposal.status,
            actions_json=self._to_actions_json(proposal.actions),
            results_json=self._to_results_json(proposal.results),
            created_at=proposal.created_at,
            resolved_at=proposal.resolved_at,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def get_proposal_by_id(self, proposal_id: int) -> ActionProposal | None:
        stmt = select(ActionProposalModel).where(ActionProposalModel.id == proposal_id)
        model = self._session.execute(stmt).scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    def get_proposals_by_conversation_id(
        self, conversation_id: int
    ) -> list[ActionProposal]:
        stmt = (
            select(ActionProposalModel)
            .where(ActionProposalModel.conversation_id == conversation_id)
            .order_by(ActionProposalModel.created_at.asc())
        )
        models = self._session.execute(stmt).scalars().all()
        return [self._to_entity(m) for m in models]

    def update_proposal(self, proposal: ActionProposal) -> ActionProposal:
        stmt = select(ActionProposalModel).where(ActionProposalModel.id == proposal.id)
        model = self._session.execute(stmt).scalar_one_or_none()
        if model is None:
            return self.add_proposal(proposal)

        model.status = proposal.status
        model.actions_json = self._to_actions_json(proposal.actions)
        model.results_json = self._to_results_json(proposal.results)
        model.resolved_at = proposal.resolved_at
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)
