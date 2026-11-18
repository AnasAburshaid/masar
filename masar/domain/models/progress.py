"""Progress domain value object."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Progress:
    """Represents completion progress for learning topics."""

    completed_topics: int
    total_topics: int

    def __post_init__(self) -> None:
        if self.completed_topics < 0:
            raise ValueError("Completed topics count cannot be negative.")
        if self.total_topics < 0:
            raise ValueError("Total topics count cannot be negative.")
        if self.completed_topics > self.total_topics:
            raise ValueError("Completed topics cannot exceed total topics.")

    @property
    def percentage(self) -> float:
        """Return completion percentage rounded to one decimal place."""
        if self.total_topics == 0:
            return 0.0
        return round((self.completed_topics / self.total_topics) * 100.0, 1)

    @property
    def formatted(self) -> str:
        """Return formatted progress string."""
        return f"{self.percentage:.1f}% ({self.completed_topics}/{self.total_topics} topics)"

    def progress_bar(self, width: int = 10) -> str:
        """Return an ASCII progress bar."""
        if self.total_topics == 0:
            return "[" + " " * width + "]"
        filled = int(round((self.completed_topics / self.total_topics) * width))
        filled = min(width, max(0, filled))
        bar = "=" * filled + " " * (width - filled)
        return f"[{bar}]"
