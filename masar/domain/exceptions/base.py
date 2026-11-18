"""Base domain exceptions for Masar."""


class DomainError(Exception):
    """Base domain exception."""


class ValidationError(DomainError):
    """Raised when business validation rules fail."""


class EntityNotFoundError(DomainError):
    """Raised when an entity is not found."""
