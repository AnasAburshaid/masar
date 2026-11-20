"""SQLAlchemy implementation of DocumentRepository."""

from typing import Optional
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from masar.application.interfaces.repositories.document_repository import (
    DocumentRepository,
)
from masar.domain.models.document import Document
from masar.infrastructure.database.models import DocumentModel


class SqlDocumentRepository(DocumentRepository):
    """SQLAlchemy implementation for Document persistence."""

    def __init__(self, session: Session) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: DocumentModel) -> Document:
        return Document(
            id=model.id,
            user_id=model.user_id,
            filename=model.filename,
            file_type=model.file_type,
            file_size_bytes=model.file_size_bytes,
            extracted_text=model.extracted_text,
            summary=model.summary,
            created_at=model.created_at,
        )

    def add(self, document: Document) -> Document:
        model = DocumentModel(
            user_id=document.user_id,
            filename=document.filename,
            file_type=document.file_type,
            file_size_bytes=document.file_size_bytes,
            extracted_text=document.extracted_text,
            summary=document.summary,
            created_at=document.created_at,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, document_id: int) -> Optional[Document]:
        model = self._session.get(DocumentModel, document_id)
        return self._to_entity(model) if model else None

    def list_by_user_id(self, user_id: int) -> list[Document]:
        stmt = (
            select(DocumentModel)
            .where(DocumentModel.user_id == user_id)
            .order_by(desc(DocumentModel.created_at), desc(DocumentModel.id))
        )
        models = self._session.scalars(stmt).all()
        return [self._to_entity(m) for m in models]

    def update(self, document: Document) -> Document:
        if document.id is None:
            raise ValueError("Cannot update a Document without an allocated ID.")
        model = self._session.get(DocumentModel, document.id)
        if model is None:
            raise ValueError(f"Document {document.id} was not found.")
        model.filename = document.filename
        model.file_type = document.file_type
        model.file_size_bytes = document.file_size_bytes
        model.extracted_text = document.extracted_text
        model.summary = document.summary
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def delete(self, document_id: int) -> bool:
        model = self._session.get(DocumentModel, document_id)
        if model is not None:
            self._session.delete(model)
            self._session.commit()
            return True
        return False
