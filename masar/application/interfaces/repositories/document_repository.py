"""Document repository abstraction interface."""

from abc import ABC, abstractmethod
from typing import Optional

from masar.domain.models.document import Document


class DocumentRepository(ABC):
    """Abstract interface defining persistence operations for Document entities."""

    @abstractmethod
    def add(self, document: Document) -> Document:
        """Persist a new Document and return it with an allocated ID."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, document_id: int) -> Optional[Document]:
        """Retrieve a Document by unique ID or return None."""
        raise NotImplementedError

    @abstractmethod
    def list_by_user_id(self, user_id: int) -> list[Document]:
        """List all documents belonging to a user, ordered by creation date."""
        raise NotImplementedError

    @abstractmethod
    def update(self, document: Document) -> Document:
        """Update an existing Document's metadata or summary."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, document_id: int) -> bool:
        """Delete a Document by unique ID. Returns True if deleted, False otherwise."""
        raise NotImplementedError
