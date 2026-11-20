"""In-memory implementation of DocumentRepository for rapid testing."""

from typing import Optional

from masar.application.interfaces.repositories.document_repository import (
    DocumentRepository,
)
from masar.domain.models.document import Document


class InMemoryDocumentRepository(DocumentRepository):
    """In-memory storage implementation for Document entities."""

    def __init__(self) -> None:
        self._documents: dict[int, Document] = {}
        self._next_id: int = 1

    def add(self, document: Document) -> Document:
        if document.id is None:
            document.id = self._next_id
            self._next_id += 1
        self._documents[document.id] = document
        return document

    def get_by_id(self, document_id: int) -> Optional[Document]:
        return self._documents.get(document_id)

    def list_by_user_id(self, user_id: int) -> list[Document]:
        docs = [d for d in self._documents.values() if d.user_id == user_id]
        return sorted(docs, key=lambda d: (d.created_at, d.id or 0), reverse=True)

    def update(self, document: Document) -> Document:
        if document.id is None or document.id not in self._documents:
            raise ValueError(f"Document {document.id} was not found.")
        self._documents[document.id] = document
        return document

    def delete(self, document_id: int) -> bool:
        if document_id in self._documents:
            del self._documents[document_id]
            return True
        return False
