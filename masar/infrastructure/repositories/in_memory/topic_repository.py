"""In-memory topic repository implementation."""

from masar.application.interfaces.repositories.topic_repository import TopicRepository
from masar.domain.exceptions import TopicNotFoundError
from masar.domain.models import Topic


class InMemoryTopicRepository(TopicRepository):
    """In-memory storage implementation for topics."""

    def __init__(self) -> None:
        self._topics: dict[int, Topic] = {}
        self._next_id: int = 1

    def add(self, topic: Topic) -> Topic:
        if topic.id is None:
            topic.id = self._next_id
            self._next_id += 1
        self._topics[topic.id] = topic
        return topic

    def get_by_id(self, topic_id: int) -> Topic | None:
        return self._topics.get(topic_id)

    def get_by_section_id(self, section_id: int) -> list[Topic]:
        return [t for t in self._topics.values() if t.section_id == section_id]

    def update(self, topic: Topic) -> Topic:
        if topic.id is None or topic.id not in self._topics:
            raise TopicNotFoundError(f"Topic with ID {topic.id} was not found.")
        self._topics[topic.id] = topic
        return topic

    def delete(self, topic_id: int) -> bool:
        if topic_id in self._topics:
            del self._topics[topic_id]
            return True
        return False

    def delete_by_section_id(self, section_id: int) -> int:
        to_delete = [t_id for t_id, t in self._topics.items() if t.section_id == section_id]
        for t_id in to_delete:
            del self._topics[t_id]
        return len(to_delete)
