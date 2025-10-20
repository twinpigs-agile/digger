import pygame
from mainloop.environment import Environment
from mainloop.screens import Screens, ExitMainLoop

DEFAULT_MAINLOOP_FREQUENCY = 240  # Hz


class MainLoop:
    """
    Main game loop controller.
    Can use either timer events or clock polling.
    """

    def __init__(
        self,
        screens: Screens,
        display: pygame.Surface,
        frequency: int = DEFAULT_MAINLOOP_FREQUENCY,
        use_timer: bool = False,
    ) -> None:
        self.screens = screens
        self.env = Environment(display)
        self.frequency = frequency
        self.use_timer = use_timer

    def run(self) -> None:
        """
        Runs the main loop until ExitMainLoop is raised.
        """
        tick_event = None
        if self.use_timer:
            tick_event = self.env.allocate_event_id("tick")
            pygame.time.set_timer(tick_event, self.screens.get_interval())

        last_tick_time = pygame.time.get_ticks()

        try:
            while True:
                events = pygame.event.get()

                if self.use_timer:
                    for event in events:
                        if event.type == pygame.QUIT:  # pragma: no cover
                            raise ExitMainLoop()
                        elif event.type == tick_event:
                            self.screens.tick(self.env, events)
                            pygame.time.set_timer(
                                tick_event, self.screens.get_interval()
                            )
                else:
                    now = pygame.time.get_ticks()
                    interval = self.screens.get_interval()
                    if now - last_tick_time >= interval:
                        self.screens.tick(self.env, events)
                        last_tick_time = now

                    for event in events:
                        if event.type == pygame.QUIT:  # pragma: no cover
                            raise ExitMainLoop()

                self.env.clock.tick(self.frequency)
        except ExitMainLoop:
            pass
