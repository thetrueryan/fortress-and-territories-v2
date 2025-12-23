"""
Event log service.
"""

from typing import List


class EventLog:
    """
    Fixed-size buffer for textual game events.

    Maintains a circular buffer of game events for display in UI.
    """

    def __init__(self, capacity: int = 20) -> None:
        """
        Initialize event log.

        Args:
            capacity: Maximum number of events to store
        """
        self.capacity = capacity
        self._events: List[str] = []

    def add(self, message: str) -> None:
        """
        Add a single event message.

        Args:
            message: Event message to add
        """
        self._events.append(message)
        if len(self._events) > self.capacity:
            self._events.pop(0)

    def extend(self, messages: List[str]) -> None:
        """
        Add multiple event messages.

        Args:
            messages: List of event messages to add
        """
        for msg in messages:
            self.add(msg)

    def clear(self) -> None:
        """Clear all events."""
        self._events.clear()

    def latest(self) -> List[str]:
        """
        Get all current events.

        Returns:
            List of event messages (oldest first)
        """
        return list(self._events)
