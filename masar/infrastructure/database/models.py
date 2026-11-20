"""SQLAlchemy ORM models representing database persistence entities."""

from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from masar.infrastructure.database.session import Base


class JourneyModel(Base):
    """Database model for learning journeys."""

    __tablename__ = "journeys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    sections: Mapped[list["SectionModel"]] = relationship(
        "SectionModel",
        back_populates="journey",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class SectionModel(Base):
    """Database model for learning sections."""

    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    journey_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("journeys.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    journey: Mapped[JourneyModel] = relationship("JourneyModel", back_populates="sections")
    topics: Mapped[list["TopicModel"]] = relationship(
        "TopicModel",
        back_populates="section",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class TopicModel(Base):
    """Database model for learning topics."""

    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    section_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    section: Mapped[SectionModel] = relationship("SectionModel", back_populates="topics")
    notes: Mapped[list["NoteModel"]] = relationship(
        "NoteModel",
        back_populates="topic",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class NoteModel(Base):
    """Database model for topic notes."""

    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(String(5000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    topic: Mapped[TopicModel] = relationship("TopicModel", back_populates="notes")
