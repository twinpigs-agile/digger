# Game Loop Architecture Specification

## Overview

This architecture defines a modular game loop system using Pygame. It is structured around four core components:

- `Environment`: Provides global resources such as the display surface and clock.
- `MainLoop`: Controls the main game loop.
- `Screens`: Manages multiple game screens.
- `Screen`: Represents a single screen and manages multiple windows.
- `Window`: Represents a rectangular UI or game element within a screen.

All components receive a shared `Environment` instance via their constructors and retain it for internal use.

---

## Modules

### environment.py

- `Environment`:
  - Holds global resources:
    - `display`: the main Pygame display surface.
    - `clock`: a `pygame.time.Clock` instance.
  - Method:
    - `allocate_event_id(name: str) -> int`: Assigns a unique event ID for a given name. Reuses the same ID for repeated names.

---

### screens.py

- `ExitMainLoop`: Exception used to signal termination of the main loop.

- `Window`:
  - Base class for all windows.
  - Constructor: `Window(env: Environment)`
    - Stores the environment.
    - Initializes `self._rect` to the full display size (`env.display.get_rect()`).
  - Methods:
    - `tick(events: list[pygame.event.Event])`: Must be implemented by subclasses.
    - `get_rect() -> pygame.Rect`: Returns the current rectangle of the window.
    - `set_rect(rect: pygame.Rect)`: Sets the window's rectangle.
    - `to_screen_coords(local: Tuple[int, int]) -> Tuple[int, int]`: Converts local coordinates to screen coordinates.
    - `to_local_coords(screen: Tuple[int, int]) -> Tuple[int, int]`: Converts screen coordinates to local coordinates.

- `Screen`:
  - Constructor: `Screen(env: Environment, interval: int)`
    - Stores the environment and update interval.
  - Methods:
    - `tick(events: list[pygame.event.Event])`: Delegates event handling to all windows in priority order.
    - `add_window(priority: int, window: Window)`: Adds a window with a given priority (0 = highest).
    - `get_windows() -> List[Tuple[int, Window]]`: Returns a copy of the window list.
    - `convert_rect(from_window, to_window, rect) -> pygame.Rect`: Converts a rectangle from one window's coordinate system to another.
    - `convert_point(from_window, to_window, point) -> Tuple[int, int]`: Converts a point from one window's coordinate system to another.

- `Screens`:
  - Constructor: `Screens(env: Environment)`
    - Stores the environment.
  - Methods:
    - `add_screen(name: str, screen: Screen, make_active: bool = False)`: Adds a screen and optionally makes it active.
    - `set_active_screen(name: str)`: Sets the active screen by name.
    - `get_active_screen_name() -> Optional[str]`: Returns the name of the active screen.
    - `get_screen(name: str) -> Screen`: Retrieves a screen by name.
    - `tick(events: list[pygame.event.Event])`: Delegates event handling to the active screen.
    - `get_interval() -> int`: Returns the interval of the active screen.

---

### mainloop.py

- `MainLoop`:
  - Constructor: `MainLoop(env: Environment, screens: Screens, display: pygame.Surface, frequency: int = 1000, use_timer: bool = False)`
    - Stores the environment, screens, display surface, target frequency, and timer mode.
  - Method:
    - `run()`: Executes the main loop until `ExitMainLoop` is raised.
      - If `use_timer` is `True`, uses `pygame.time.set_timer` with an event ID from `Environment`.
      - Otherwise, uses `pygame.time.get_ticks()` to manage timing manually.
      - Collects events via `pygame.event.get()` and passes them to `Screens.tick()`.
      - Handles `pygame.QUIT` by raising `ExitMainLoop`.

---

## Event Handling

- All Pygame events are collected in the main loop and passed to `Screens.tick()`.
- `Screens.tick()` forwards events to the active `Screen`.
- `Screen.tick()` forwards events to its windows in ascending priority order (higher priority windows tick later and appear on top).
- Only `pygame.QUIT` is handled directly in `MainLoop`.

---

## Testing

- `test_environment.py`: Verifies `Environment` initialization and event ID allocation.
- `test_screens.py`: Tests screen and window management, coordinate conversions, and tick delegation.
- `test_mainloop.py`: Tests loop execution in both timer and polling modes, and proper exit behavior.
- All abstract methods that must be overridden (e.g. `Window.tick`) raise `NotImplementedError` by default and are tested accordingly.

---
