"""Base domain exceptions for Masar."""


class DomainError(Exception):
    """Base domain exception."""


class ValidationError(DomainError):
    """Raised when business validation rules fail."""


class EmptyFieldError(ValidationError):
    """Raised when a required string field is empty or contains only whitespace."""


class FieldLengthError(ValidationError):
    """Raised when a field exceeds the maximum allowed character length."""


class InvalidIdError(ValidationError):
    """Raised when an identifier or foreign key is invalid (e.g. non-positive)."""


class EntityNotFoundError(DomainError):
    """Raised when an entity is not found."""


class AccessDeniedError(DomainError):
    """Raised when an authenticated user attempts to access a resource owned by another user."""
