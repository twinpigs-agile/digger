from typing import Dict, Optional, Tuple, List
import pygame
from mainloop.environment import Environment


class ExitMainLoop(Exception):
    """Raised by a screen to signal that the main loop should exit."""

    pass


class Window:
    """
    Base class for a window within a screen.
    Receives Environment in constructor and sets its rect to full display size.
    Subclasses must implement tick().
    """

    def __init__(self, env: Environment) -> None:
        self.env = env
        self._rect: pygame.Rect = self.env.display.get_rect()

    def tick(self, events: list[pygame.event.Event]) -> None:
        raise NotImplementedError("tick must be implemented by Window subclasses")

    def get_rect(self) -> pygame.Rect:
        return self._rect

    def set_rect(self, rect: pygame.Rect) -> None:
        self._rect = rect

    def to_screen_coords(self, local: Tuple[int, int]) -> Tuple[int, int]:
        return (self._rect.left + local[0], self._rect.top + local[1])

    def to_local_coords(self, screen: Tuple[int, int]) -> Tuple[int, int]:
        return (screen[0] - self._rect.left, screen[1] - self._rect.top)


class Screen:
    """
    Base class for a game screen.
    Receives Environment in constructor.
    Manages a list of windows with priority.
    """

    def __init__(self, env: Environment, interval: int) -> None:
        self.env = env
        self.interval = interval
        self._windows: List[Tuple[int, Window]] = []

    def tick(self, events: list[pygame.event.Event]) -> None:
        for _, window in self._windows:
            window.tick(events)

    def add_window(self, priority: int, window: Window) -> None:
        self._windows.append((priority, window))
        self._windows.sort(key=lambda pair: pair[0])  # 0 = highest priority

    def get_windows(self) -> List[Tuple[int, Window]]:
        return self._windows.copy()

    def convert_rect(
        self,
        from_window: Window,
        to_window: Window,
        rect: pygame.Rect,
    ) -> pygame.Rect:
        from_offset = from_window.get_rect().topleft
        to_offset = to_window.get_rect().topleft
        dx = from_offset[0] - to_offset[0]
        dy = from_offset[1] - to_offset[1]
        return pygame.Rect(rect.left + dx, rect.top + dy, rect.width, rect.height)

    def convert_point(
        self,
        from_window: Window,
        to_window: Window,
        point: Tuple[int, int],
    ) -> Tuple[int, int]:
        from_offset = from_window.get_rect().topleft
        to_offset = to_window.get_rect().topleft
        dx = from_offset[0] - to_offset[0]
        dy = from_offset[1] - to_offset[1]
        return (point[0] + dx, point[1] + dy)


class Screens:
    """
    Container for all game screens.
    Receives Environment in constructor.
    Manages switching between screens and delegates ticking.
    """

    def __init__(self, env: Environment) -> None:
        self.env = env
        self._screens: Dict[str, Screen] = {}
        self._active_screen_name: Optional[str] = None

    def add_screen(self, name: str, screen: Screen, make_active: bool = False) -> None:
        self._screens[name] = screen
        if make_active or self._active_screen_name is None:
            self._active_screen_name = name

    def set_active_screen(self, name: str) -> None:
        if name not in self._screens:
            raise ValueError(f"Screen '{name}' not found")
        self._active_screen_name = name

    def get_active_screen_name(self) -> Optional[str]:
        return self._active_screen_name

    def get_screen(self, name: str) -> Screen:
        if name not in self._screens:
            raise ValueError(f"Screen '{name}' not found")
        return self._screens[name]

    def tick(self, events: list[pygame.event.Event]) -> None:
        if self._active_screen_name is None:
            raise RuntimeError("No active screen set")
        screen = self._screens[self._active_screen_name]
        screen.tick(events)

    def get_interval(self) -> int:
        if self._active_screen_name is None:
            raise RuntimeError("No active screen set")
        return self._screens[self._active_screen_name].interval
