from typing import Dict, Optional
from mainloop.environment import Environment
import pygame


class ExitMainLoop(Exception):
    """
    Raised by a screen to signal that the main loop should exit.
    """

    pass


class Screen:
    """
    Base class for a game screen.
    Each screen defines its own tick behavior and update interval.
    """

    def __init__(self, interval: int) -> None:
        self.interval = interval

    def tick(
        self, env: Environment, screens: "Screens", events: list[pygame.event.Event]
    ) -> None:
        raise NotImplementedError("tick must be implemented by subclasses")


class Screens:
    """
    Container for all game screens.
    Manages switching between screens and delegates ticking.
    """

    def __init__(self) -> None:
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

    def tick(self, env: Environment, events: list[pygame.event.Event]) -> None:
        if self._active_screen_name is None:
            raise RuntimeError("No active screen set")
        screen = self._screens[self._active_screen_name]
        screen.tick(env, self, events)

    def get_interval(self) -> int:
        if self._active_screen_name is None:
            raise RuntimeError("No active screen set")
        return self._screens[self._active_screen_name].interval
