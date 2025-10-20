import unittest
import pygame
from mainloop.environment import Environment
from mainloop.screens import Screen, Screens, Window, ExitMainLoop
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
    def __init__(self, env, interval):
        super().__init__(env, interval)
        self.ticked = False
        self.last_events = []

    def tick(self, events):
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
        self.screens = Screens(self.env)
        self.screen1 = DummyScreen(self.env, 100)
        self.screen2 = DummyScreen(self.env, 200)

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
        self.screens.tick([])
        self.assertTrue(self.screen1.ticked)
        self.assertEqual(self.screens.get_interval(), 100)

    def test_screen_tick_not_implemented(self):
        class EmptyScreen(Screen):
            pass

        screen = EmptyScreen(self.env, 100)
        screen.tick([])

    def test_set_active_screen_invalid(self):
        with self.assertRaises(ValueError):
            self.screens.set_active_screen("nonexistent")

    def test_get_screen_invalid(self):
        with self.assertRaises(ValueError):
            self.screens.get_screen("nonexistent")

    def test_tick_without_active_screen(self):
        with self.assertRaises(RuntimeError):
            self.screens.tick([])

    def test_get_interval_without_active_screen(self):
        with self.assertRaises(RuntimeError):
            self.screens.get_interval()


# ---------- MainLoop Tests ----------


class CountingScreen(Screen):
    def __init__(self, env, interval, max_ticks=2):
        super().__init__(env, interval)
        self.tick_count = 0
        self.max_ticks = max_ticks

    def tick(self, events):
        self.tick_count += 1
        if self.tick_count >= self.max_ticks:
            raise ExitMainLoop()


class TestMainLoop(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.display = pygame.display.set_mode((100, 100))
        self.env = Environment(self.display)

    def test_mainloop_exit_polling(self):
        screens = Screens(self.env)
        screen = CountingScreen(self.env, interval=10, max_ticks=2)
        screens.add_screen("polling", screen, make_active=True)
        loop = MainLoop(self.env, screens, frequency=1000, use_timer=False)
        try:
            loop.run()
        except Exception as e:
            self.fail(
                f"MainLoop.run() raised unexpected exception in polling mode: {e}"
            )
        self.assertEqual(screen.tick_count, 2)

    def test_mainloop_exit_timer(self):
        screens = Screens(self.env)
        screen = CountingScreen(self.env, interval=10, max_ticks=2)
        screens.add_screen("timer", screen, make_active=True)
        loop = MainLoop(self.env, screens, frequency=1000, use_timer=True)
        try:
            loop.run()
        except Exception as e:
            self.fail(f"MainLoop.run() raised unexpected exception in timer mode: {e}")
        self.assertEqual(screen.tick_count, 2)


# ---------- Window Tests ----------


class DummyWindow(Window):
    def __init__(self, env):
        super().__init__(env)
        self.ticked = False

    def tick(self, events):
        self.ticked = True


class DummyScreenWithWindows(Screen):
    def __init__(self, env, interval):
        super().__init__(env, interval)


class TestWindowIntegration(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.display = pygame.display.set_mode((100, 100))
        self.env = Environment(self.display)
        self.screen = DummyScreenWithWindows(self.env, 100)

    def test_add_window_priority_order(self):
        w1 = DummyWindow(self.env)
        w2 = DummyWindow(self.env)
        w1.set_rect(pygame.Rect(0, 0, 10, 10))
        w2.set_rect(pygame.Rect(10, 10, 10, 10))
        self.screen.add_window(5, w1)
        self.screen.add_window(0, w2)
        windows = self.screen.get_windows()
        self.assertEqual(windows[0][1], w2)
        self.assertEqual(windows[1][1], w1)

    def test_tick_delegation_to_windows(self):
        w1 = DummyWindow(self.env)
        self.screen.add_window(0, w1)
        self.screen.tick([])
        self.assertTrue(w1.ticked)

    def test_convert_rect_between_windows(self):
        w1 = DummyWindow(self.env)
        w2 = DummyWindow(self.env)
        w1.set_rect(pygame.Rect(10, 10, 20, 20))
        w2.set_rect(pygame.Rect(30, 40, 20, 20))
        rect = pygame.Rect(15, 15, 5, 5)
        converted = self.screen.convert_rect(w1, w2, rect)
        self.assertEqual(converted.topleft, (-5, -15))
        self.assertEqual(converted.size, (5, 5))

    def test_convert_point_between_windows(self):
        w1 = DummyWindow(self.env)
        w2 = DummyWindow(self.env)
        w1.set_rect(pygame.Rect(10, 10, 20, 20))
        w2.set_rect(pygame.Rect(30, 40, 20, 20))
        point = (15, 15)
        converted = self.screen.convert_point(w1, w2, point)
        self.assertEqual(converted, (-5, -15))

    def test_window_tick_not_implemented(self):
        class IncompleteWindow(Window):
            def __init__(self, env):
                super().__init__(env)

        w = IncompleteWindow(self.env)
        w.set_rect(pygame.Rect(0, 0, 10, 10))
        with self.assertRaises(NotImplementedError):
            w.tick([])


# ---------- Window Geometry Tests ----------


class GeometryWindow(Window):
    def __init__(self, env):
        super().__init__(env)

    def tick(self, events):
        pass  # Not needed for geometry tests


class TestWindowGeometry(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.display = pygame.display.set_mode((100, 100))
        self.env = Environment(self.display)
        self.rect = pygame.Rect(10, 20, 30, 40)
        self.window = GeometryWindow(self.env)
        self.window.set_rect(self.rect)

    def test_set_rect(self):
        new_rect = pygame.Rect(50, 60, 70, 80)
        self.window.set_rect(new_rect)
        self.assertEqual(self.window.get_rect(), new_rect)

    def test_to_screen_coords(self):
        local_point = (5, 7)
        screen_point = self.window.to_screen_coords(local_point)
        self.assertEqual(screen_point, (15, 27))  # 10+5, 20+7

    def test_to_local_coords(self):
        screen_point = (25, 35)
        local_point = self.window.to_local_coords(screen_point)
        self.assertEqual(local_point, (15, 15))  # 25-10, 35-20
