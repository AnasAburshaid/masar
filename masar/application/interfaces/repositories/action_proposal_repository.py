"""Abstract repository interface for ActionProposal persistence."""

from abc import ABC, abstractmethod

from masar.domain.models.action import ActionProposal


class ActionProposalRepository(ABC):
    """Contract for storing and retrieving AI Action Proposals."""

    @abstractmethod
    def add_proposal(self, proposal: ActionProposal) -> ActionProposal:
        """Persist a new action proposal."""

    @abstractmethod
    def get_proposal_by_id(self, proposal_id: int) -> ActionProposal | None:
        """Retrieve an action proposal by ID."""

    @abstractmethod
    def get_proposals_by_conversation_id(
        self, conversation_id: int
    ) -> list[ActionProposal]:
        """Retrieve all proposals associated with a specific conversation."""

    @abstractmethod
    def update_proposal(self, proposal: ActionProposal) -> ActionProposal:
        """Update an existing action proposal's status, results, or timestamps."""
