"""Domain exceptions for adaptive learning recommendations."""

from masar.domain.exceptions.base import DomainError


class RecommendationError(DomainError):
    """Base domain exception for recommendation processing failures."""

    pass
