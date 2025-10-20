import pygame
from typing import Final


class Environment:
    """
    Holds global resources such as display surface and clock.
    Provides event ID allocator by name.
    """

    def __init__(self, display: pygame.Surface) -> None:
        self.display: Final[pygame.Surface] = display
        self.clock: Final[pygame.time.Clock] = pygame.time.Clock()
        self._event_ids: dict[str, int] = {}
        self._next_event_id: int = pygame.USEREVENT + 1

    def allocate_event_id(self, name: str) -> int:
        """
        Returns a unique event ID for the given name.
        If the name was already allocated, returns the same ID.
        """
        if name in self._event_ids:
            return self._event_ids[name]
        event_id = self._next_event_id
        self._event_ids[name] = event_id
        self._next_event_id += 1
        return event_id
