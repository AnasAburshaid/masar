"""In-memory implementation of ActionProposalRepository for fast automated testing."""

from masar.application.interfaces.repositories.action_proposal_repository import (
    ActionProposalRepository,
)
from masar.domain.models.action import ActionProposal


class InMemoryActionProposalRepository(ActionProposalRepository):
    """In-memory storage adapter for action proposals."""

    def __init__(self) -> None:
        self._proposals: dict[int, ActionProposal] = {}
        self._next_id: int = 1

    def add_proposal(self, proposal: ActionProposal) -> ActionProposal:
        proposal_id = self._next_id
        self._next_id += 1
        persisted = ActionProposal(
            id=proposal_id,
            conversation_id=proposal.conversation_id,
            user_id=proposal.user_id,
            title=proposal.title,
            status=proposal.status,
            actions=list(proposal.actions),
            results=list(proposal.results),
            created_at=proposal.created_at,
            resolved_at=proposal.resolved_at,
        )
        self._proposals[proposal_id] = persisted
        return persisted

    def get_proposal_by_id(self, proposal_id: int) -> ActionProposal | None:
        return self._proposals.get(proposal_id)

    def get_proposals_by_conversation_id(
        self, conversation_id: int
    ) -> list[ActionProposal]:
        return [
            p
            for p in self._proposals.values()
            if p.conversation_id == conversation_id
        ]

    def update_proposal(self, proposal: ActionProposal) -> ActionProposal:
        if proposal.id is None or proposal.id not in self._proposals:
            return self.add_proposal(proposal)

        persisted = ActionProposal(
            id=proposal.id,
            conversation_id=proposal.conversation_id,
            user_id=proposal.user_id,
            title=proposal.title,
            status=proposal.status,
            actions=list(proposal.actions),
            results=list(proposal.results),
            created_at=proposal.created_at,
            resolved_at=proposal.resolved_at,
        )
        self._proposals[proposal.id] = persisted
        return persisted
