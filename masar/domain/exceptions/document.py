"""Domain exceptions for Document entity and processing operations."""

from masar.domain.exceptions.base import (
    AccessDeniedError,
    DomainError,
    EntityNotFoundError,
)


class DocumentError(DomainError):
    """Base exception for all document operations."""


class DocumentNotFoundError(EntityNotFoundError, DocumentError):
    """Raised when a requested document cannot be found."""


class DocumentAccessDeniedError(AccessDeniedError, DocumentError):
    """Raised when a user attempts to access a document they do not own."""


class UnsupportedFileTypeError(DocumentError):
    """Raised when an uploaded file is not an allowed format (pdf, txt, md)."""


class FileTooLargeError(DocumentError):
    """Raised when an uploaded file exceeds the maximum allowed file size."""


class EmptyDocumentError(DocumentError):
    """Raised when an uploaded document contains no text or extractable content."""


class DocumentExtractionError(DocumentError):
    """Raised when text extraction from an uploaded file fails or the file is corrupted."""
