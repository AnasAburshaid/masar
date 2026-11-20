"""Pydantic v2 schemas for document data transfer and API responses."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, computed_field


class DocumentResponseSchema(BaseModel):
    """Public summary metadata for an uploaded document."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique document ID")
    user_id: int = Field(..., description="ID of the document owner")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File format category ('pdf', 'text', 'markdown')")
    file_size_bytes: int = Field(..., description="File size in bytes")
    summary: Optional[str] = Field(default=None, description="AI-generated summary if available")
    created_at: datetime = Field(..., description="Upload timestamp")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def file_size_display(self) -> str:
        """Human-readable file size representation (e.g. '120 KB', '2.4 MB')."""
        kb = self.file_size_bytes / 1024
        if kb < 1024:
            return f"{kb:.1f} KB"
        mb = kb / 1024
        return f"{mb:.2f} MB"


class DocumentDetailSchema(DocumentResponseSchema):
    """Detailed view of an uploaded document including full extracted text."""

    extracted_text: str = Field(..., description="Extracted plain text content")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def char_count(self) -> int:
        """Total character length of the extracted text."""
        return len(self.extracted_text)


class DocumentSummarizeResponseSchema(BaseModel):
    """Response containing AI-generated document analysis and summary."""

    id: int
    filename: str
    summary: str
