"""Common domain type aliases and typing utilities."""

from datetime import datetime
from typing import Any, TypeAlias

# Basic primitive domain entity identifiers
EntityId: TypeAlias = int
JourneyId: TypeAlias = int
SectionId: TypeAlias = int
TopicId: TypeAlias = int
NoteId: TypeAlias = int

# Timestamp type alias
Timestamp: TypeAlias = datetime

# Serialized data dictionary alias
SerializedData: TypeAlias = dict[str, Any]
