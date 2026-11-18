"""Domain exceptions for Masar."""


class DomainError(Exception):
    """Base domain exception."""


class ValidationError(DomainError):
    """Raised when business validation rules fail."""


class EntityNotFoundError(DomainError):
    """Raised when an entity is not found."""


class JourneyNotFoundError(EntityNotFoundError):
    """Raised when a specific journey is not found."""


class SectionNotFoundError(EntityNotFoundError):
    """Raised when a specific section is not found."""


class TopicNotFoundError(EntityNotFoundError):
    """Raised when a specific topic is not found."""
