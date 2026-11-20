"""Document application service managing document uploads, extraction, and AI analysis."""

from typing import Optional

from masar.application.interfaces.repositories.document_repository import (
    DocumentRepository,
)
from masar.application.services.ai_service import AIService
from masar.application.services.document_extractor import (
    detect_file_type,
    extract_text_from_bytes,
)
from masar.domain.exceptions.base import InvalidIdError
from masar.domain.exceptions.document import (
    DocumentAccessDeniedError,
    DocumentNotFoundError,
)
from masar.domain.models.ai import ChatMessage
from masar.domain.models.document import Document


class DocumentService:
    """Service handling document uploads, text extraction, ownership validation, and AI summaries."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        ai_service: Optional[AIService] = None,
    ) -> None:
        self._repo = document_repository
        self._ai = ai_service

    def upload_document(
        self,
        user_id: int,
        filename: str,
        content_bytes: bytes,
        mime_type: Optional[str] = None,
    ) -> Document:
        """Process, extract text from, and persist an uploaded learning document."""
        if user_id <= 0:
            raise InvalidIdError("User ID must be a positive integer.")

        file_type, extracted_text = extract_text_from_bytes(content_bytes, filename)

        document = Document(
            user_id=user_id,
            filename=filename,
            file_type=file_type,
            file_size_bytes=len(content_bytes),
            extracted_text=extracted_text,
        )
        return self._repo.add(document)

    def get_document(self, document_id: int, user_id: int) -> Document:
        """Retrieve a specific document by ID, enforcing user ownership."""
        if document_id <= 0:
            raise InvalidIdError("Document ID must be a positive integer.")
        if user_id <= 0:
            raise InvalidIdError("User ID must be a positive integer.")

        doc = self._repo.get_by_id(document_id)
        if doc is None:
            raise DocumentNotFoundError(f"Document with ID {document_id} was not found.")

        if doc.user_id != user_id:
            raise DocumentAccessDeniedError(
                f"User {user_id} does not have access to document {document_id}."
            )
        return doc

    def list_user_documents(self, user_id: int) -> list[Document]:
        """List all documents uploaded by a specific user ordered by latest activity."""
        if user_id <= 0:
            raise InvalidIdError("User ID must be a positive integer.")
        return self._repo.list_by_user_id(user_id)

    def delete_document(self, document_id: int, user_id: int) -> bool:
        """Delete an uploaded document after verifying ownership."""
        self.get_document(document_id, user_id)
        return self._repo.delete(document_id)

    def summarize_document(self, document_id: int, user_id: int) -> str:
        """Generate or retrieve an AI analysis and executive technical summary of the document."""
        doc = self.get_document(document_id, user_id)

        # Return cached summary if already generated
        if doc.summary and doc.summary.strip():
            return doc.summary

        if self._ai is None:
            raise RuntimeError("AIService is not configured for document summarization.")

        # Truncate text to fit context budget (~8,000 characters)
        preview_text = doc.extracted_text[:8000]
        if len(doc.extracted_text) > 8000:
            preview_text += "\n\n[Content truncated for length...]"

        prompt = (
            f"Analyze the following technical document ('{doc.filename}'). "
            "Provide an executive summary, identify key technical skills, experience level, "
            "and recommend high-value learning topics or gaps based on its content:\n\n"
            f"{preview_text}"
        )

        response = self._ai.chat(
            messages=[
                ChatMessage(
                    role="system",
                    content=(
                        "You are an expert technical resume and document analyzer for Masar. "
                        "Produce structured, insightful summaries highlighting engineering skills, "
                        "experience depth, and recommended learning pathways."
                    ),
                ),
                ChatMessage(role="user", content=prompt),
            ]
        )

        summary = response.content.strip()
        doc.update_summary(summary)
        self._repo.update(doc)
        return summary
