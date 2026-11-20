"""Document domain model representing uploaded learning resources and materials."""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from masar.domain.exceptions.base import (
    EmptyFieldError,
    FieldLengthError,
    InvalidIdError,
    ValidationError,
)
from masar.domain.exceptions.document import FileTooLargeError, UnsupportedFileTypeError

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit
ALLOWED_FILE_TYPES = {"pdf", "text", "markdown"}


@dataclass
class Document:
    """Represents a user-uploaded document in Masar."""

    user_id: int
    filename: str
    file_type: str
    file_size_bytes: int
    extracted_text: str
    id: int | None = None
    summary: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    MAX_FILENAME_LENGTH: int = 255

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Validate document invariants."""
        if self.id is not None and self.id <= 0:
            raise InvalidIdError("Document ID must be a positive integer.")

        if self.user_id <= 0:
            raise InvalidIdError("User ID must be a positive integer.")

        if not self.filename or not self.filename.strip():
            raise EmptyFieldError("Document filename cannot be empty.")

        clean_name = self.filename.strip()
        if len(clean_name) > self.MAX_FILENAME_LENGTH:
            raise FieldLengthError(
                f"Filename cannot exceed {self.MAX_FILENAME_LENGTH} characters."
            )
        self.filename = clean_name

        clean_type = self.file_type.strip().lower()
        if clean_type not in ALLOWED_FILE_TYPES:
            raise UnsupportedFileTypeError(
                f"Unsupported file type '{self.file_type}'. Allowed types: {', '.join(sorted(ALLOWED_FILE_TYPES))}."
            )
        self.file_type = clean_type

        if self.file_size_bytes <= 0:
            raise ValidationError("File size must be greater than 0 bytes.")

        if self.file_size_bytes > MAX_FILE_SIZE_BYTES:
            raise FileTooLargeError(
                f"File size ({self.file_size_bytes} bytes) exceeds maximum limit of {MAX_FILE_SIZE_BYTES} bytes."
            )

    def update_summary(self, summary: str) -> None:
        """Update the AI generated summary for the document."""
        self.summary = summary.strip() if summary else None
