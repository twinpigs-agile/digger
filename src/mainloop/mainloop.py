import pygame
from mainloop.environment import Environment
from mainloop.screens import Screens, ExitMainLoop


class MainLoop:
    def __init__(
        self,
        env: Environment,
        screens: Screens,
        frequency: int = 1000,
        use_timer: bool = False,
    ) -> None:
        self.env = env
        self.screens = screens
        self.frequency = frequency
        self.use_timer = use_timer

    def run(self) -> None:
        if self.use_timer:
            event_id = self.env.allocate_event_id("tick")
            pygame.time.set_timer(event_id, self.screens.get_interval())

        last_tick = pygame.time.get_ticks()

        try:
            while True:
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        raise ExitMainLoop()  # pragma: no cover

                if self.use_timer:
                    self.screens.tick(events)
                else:
                    now = pygame.time.get_ticks()
                    if now - last_tick >= self.screens.get_interval():
                        last_tick = now
                        self.screens.tick(events)

                self.env.clock.tick(self.frequency)
        except ExitMainLoop:
            pass
