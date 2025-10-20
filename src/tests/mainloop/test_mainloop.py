import unittest
import pygame
from mainloop.environment import Environment
from mainloop.screens import Screen, Screens, ExitMainLoop
from mainloop.mainloop import MainLoop

# ---------- Environment Tests ----------


class TestEnvironment(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.display = pygame.display.set_mode((100, 100))
        self.env = Environment(self.display)

    def test_display_and_clock(self):
        self.assertIsInstance(self.env.display, pygame.Surface)
        self.assertIsInstance(self.env.clock, pygame.time.Clock)

    def test_event_id_allocation(self):
        id1 = self.env.allocate_event_id("tick")
        id2 = self.env.allocate_event_id("tick")
        id3 = self.env.allocate_event_id("custom")
        self.assertEqual(id1, id2)
        self.assertNotEqual(id1, id3)


# ---------- Screens Tests ----------


class DummyScreen(Screen):
    def __init__(self, interval):
        super().__init__(interval)
        self.ticked = False
        self.last_events = []

    def tick(self, env, screens, events):
        self.ticked = True
        self.last_events = events
        for event in events:
            if event.type == pygame.QUIT:
                raise ExitMainLoop()


class TestScreens(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.display = pygame.display.set_mode((100, 100))
        self.env = Environment(self.display)
        self.screens = Screens()
        self.screen1 = DummyScreen(100)
        self.screen2 = DummyScreen(200)

    def test_add_and_get_screen(self):
        self.screens.add_screen("main", self.screen1, make_active=True)
        self.assertEqual(self.screens.get_active_screen_name(), "main")
        self.assertIs(self.screens.get_screen("main"), self.screen1)

    def test_set_active_screen_valid(self):
        self.screens.add_screen("main", self.screen1)
        self.screens.add_screen("settings", self.screen2)
        self.screens.set_active_screen("settings")
        self.assertEqual(self.screens.get_active_screen_name(), "settings")

    def test_tick_and_interval(self):
        self.screens.add_screen("main", self.screen1, make_active=True)
        self.screens.tick(self.env, [])
        self.assertTrue(self.screen1.ticked)
        self.assertEqual(self.screens.get_interval(), 100)

    def test_screen_tick_not_implemented(self):
        class EmptyScreen(Screen):
            pass

        screen = EmptyScreen(100)
        with self.assertRaises(NotImplementedError):
            screen.tick(self.env, self.screens, [])

    def test_set_active_screen_invalid(self):
        with self.assertRaises(ValueError):
            self.screens.set_active_screen("nonexistent")

    def test_get_screen_invalid(self):
        with self.assertRaises(ValueError):
            self.screens.get_screen("nonexistent")

    def test_tick_without_active_screen(self):
        with self.assertRaises(RuntimeError):
            self.screens.tick(self.env, [])

    def test_get_interval_without_active_screen(self):
        with self.assertRaises(RuntimeError):
            self.screens.get_interval()


# ---------- MainLoop Tests ----------


class CountingScreen(Screen):
    def __init__(self, interval, max_ticks=2):
        super().__init__(interval)
        self.tick_count = 0
        self.max_ticks = max_ticks

    def tick(self, env, screens, events):
        self.tick_count += 1
        if self.tick_count >= self.max_ticks:
            raise ExitMainLoop()


class TestMainLoop(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.display = pygame.display.set_mode((100, 100))

    def test_mainloop_exit_polling(self):
        screens = Screens()
        screen = CountingScreen(interval=10, max_ticks=2)
        screens.add_screen("polling", screen, make_active=True)
        loop = MainLoop(screens, self.display, frequency=1000, use_timer=False)
        try:
            loop.run()
        except Exception as e:
            self.fail(
                f"MainLoop.run() raised unexpected exception in polling mode: {e}"
            )
        self.assertEqual(screen.tick_count, 2)

    def test_mainloop_exit_timer(self):
        screens = Screens()
        screen = CountingScreen(interval=10, max_ticks=2)
        screens.add_screen("timer", screen, make_active=True)
        loop = MainLoop(screens, self.display, frequency=1000, use_timer=True)
        try:
            loop.run()
        except Exception as e:
            self.fail(f"MainLoop.run() raised unexpected exception in timer mode: {e}")
        self.assertEqual(screen.tick_count, 2)
