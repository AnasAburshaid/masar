"""JSON document repository implementation."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from masar.application.interfaces.repositories.document_repository import (
    DocumentRepository,
)
from masar.domain.models.document import Document
from masar.infrastructure.storage.json_storage import JsonStorage


class JsonDocumentRepository(DocumentRepository):
    """JSON file persistence storage implementation for Document entities."""

    def __init__(self, storage: JsonStorage | str | Path | None = None) -> None:
        if isinstance(storage, JsonStorage):
            self._storage = storage
        elif storage is not None:
            self._storage = JsonStorage(storage)
        else:
            self._storage = JsonStorage("masar_data.json")

    def _to_entity(self, item: dict[str, Any]) -> Document:
        created_at = item.get("created_at")
        if isinstance(created_at, str):
            try:
                created_dt = datetime.fromisoformat(created_at)
            except ValueError:
                created_dt = datetime.now(timezone.utc)
        elif isinstance(created_at, datetime):
            created_dt = created_at
        else:
            created_dt = datetime.now(timezone.utc)

        return Document(
            id=item["id"],
            user_id=item["user_id"],
            filename=item["filename"],
            file_type=item["file_type"],
            file_size_bytes=item["file_size_bytes"],
            extracted_text=item["extracted_text"],
            summary=item.get("summary"),
            created_at=created_dt,
        )

    def _to_dict(self, doc: Document) -> dict[str, Any]:
        return {
            "id": doc.id,
            "user_id": doc.user_id,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "file_size_bytes": doc.file_size_bytes,
            "extracted_text": doc.extracted_text,
            "summary": doc.summary,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
        }

    def add(self, document: Document) -> Document:
        data = self._storage.load()
        documents = data.get("documents", [])

        if document.id is None:
            max_id = max((d["id"] for d in documents), default=0)
            document.id = max_id + 1

        documents.append(self._to_dict(document))
        data["documents"] = documents
        self._storage.save(data)
        return document

    def get_by_id(self, document_id: int) -> Optional[Document]:
        data = self._storage.load()
        documents = data.get("documents", [])
        for item in documents:
            if item.get("id") == document_id:
                return self._to_entity(item)
        return None

    def list_by_user_id(self, user_id: int) -> list[Document]:
        data = self._storage.load()
        documents = data.get("documents", [])
        user_docs = [
            self._to_entity(item)
            for item in documents
            if item.get("user_id") == user_id
        ]
        return sorted(user_docs, key=lambda d: (d.created_at, d.id or 0), reverse=True)

    def update(self, document: Document) -> Document:
        if document.id is None:
            raise ValueError("Cannot update a Document without an allocated ID.")
        data = self._storage.load()
        documents = data.get("documents", [])
        for i, item in enumerate(documents):
            if item.get("id") == document.id:
                documents[i] = self._to_dict(document)
                data["documents"] = documents
                self._storage.save(data)
                return document
        raise ValueError(f"Document {document.id} was not found.")

    def delete(self, document_id: int) -> bool:
        data = self._storage.load()
        documents = data.get("documents", [])
        filtered = [item for item in documents if item.get("id") != document_id]
        if len(filtered) < len(documents):
            data["documents"] = filtered
            self._storage.save(data)
            return True
        return False
