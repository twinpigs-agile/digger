import unittest
import pygame
from mainloop.environment import Environment
from mainloop.screens import Screen, Screens, Window, ExitMainLoop, View
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


# ---------- View Tests ----------


class TestView(unittest.TestCase):
    """Tests for the View base class."""

    def setUp(self):
        pygame.init()
        self.display = pygame.display.set_mode((100, 100))
        self.env = Environment(self.display)

    def test_view_type_attribute(self):
        """Test that View has a view_type attribute."""
        view = View()
        self.assertEqual(view.view_type, "base")

    def test_view_custom_type(self):
        """Test custom view types in subclasses."""

        class PlayerView(View):
            view_type = "player"

        view = PlayerView()
        self.assertEqual(view.view_type, "player")

    def test_view_tick_not_implemented(self):
        """Test that tick() raises NotImplementedError in base View."""
        view = View()
        with self.assertRaises(NotImplementedError):
            view.tick()

    def test_view_tick_implemented_in_subclass(self):
        """Test that subclass can implement tick()."""

        class TickingView(View):
            def __init__(self):
                super().__init__()
                self.ticked = False

            def tick(self):
                self.ticked = True

        view = TickingView()
        view.tick()
        self.assertTrue(view.ticked)

    def test_view_window_association_with_window(self):
        """Test that view correctly associates with window."""

        class SimpleWindow(Window):
            def tick(self, events):
                pass

        class SimpleView(View):
            def tick(self):
                pass

        window = SimpleWindow(self.env)
        view = SimpleView()

        # Initially, view has no window
        self.assertIsNone(view.get_window())

        # Add view to window
        window.add_view(0, view)
        self.assertIs(view.get_window(), window)

    def test_view_weak_reference_cleanup(self):
        """Test that weak reference is cleared when window is destroyed."""

        class SimpleWindow(Window):
            def tick(self, events):
                pass

        class SimpleView(View):
            def tick(self):
                pass

        view = SimpleView()
        window = SimpleWindow(self.env)
        window.add_view(0, view)

        # Verify window is associated
        self.assertIs(view.get_window(), window)

        # Remove view from window
        window.remove_view(view)

        # Weak reference should be None now
        self.assertIsNone(view.get_window())

    def test_view_weak_reference_after_window_deletion(self):
        """Test that weak reference becomes None when window is garbage collected."""

        class SimpleWindow(Window):
            def tick(self, events):
                pass

        class SimpleView(View):
            def tick(self):
                pass

        view = SimpleView()

        # Create window in limited scope and associate view
        window = SimpleWindow(self.env)
        window.add_view(0, view)
        # window_id = id(window)

        # Verify association
        self.assertIsNotNone(view.get_window())

        # Delete window
        del window

        # After garbage collection, weak reference should return None
        self.assertIsNone(view.get_window())


# ---------- Window with Views Tests ----------


class SimpleView(View):
    """Simple test view implementation."""

    view_type = "simple"

    def __init__(self):
        super().__init__()
        self.tick_count = 0

    def tick(self):
        self.tick_count += 1


class ViewManagingWindow(Window):
    """Window for testing view management."""

    def tick(self, events):
        # Tick all views
        for _, view in self._views:
            view.tick()


class TestWindowViewManagement(unittest.TestCase):
    """Tests for Window's view management capabilities."""

    def setUp(self):
        pygame.init()
        self.display = pygame.display.set_mode((100, 100))
        self.env = Environment(self.display)
        self.window = ViewManagingWindow(self.env)

    def test_add_view_to_window(self):
        """Test adding a view to window."""
        view = SimpleView()
        self.window.add_view(5, view)

        views = self.window.get_views()
        self.assertEqual(len(views), 1)
        self.assertEqual(views[0], (5, view))

    def test_add_multiple_views_priority_order(self):
        """Test that views are sorted by priority."""
        view1 = SimpleView()
        view2 = SimpleView()
        view3 = SimpleView()

        self.window.add_view(10, view1)
        self.window.add_view(0, view2)
        self.window.add_view(5, view3)

        views = self.window.get_views()
        self.assertEqual(len(views), 3)
        self.assertEqual(views[0][1], view2)  # priority 0
        self.assertEqual(views[1][1], view3)  # priority 5
        self.assertEqual(views[2][1], view1)  # priority 10

    def test_add_views_same_priority(self):
        """Test that views with same priority maintain insertion order."""
        view1 = SimpleView()
        view2 = SimpleView()
        view3 = SimpleView()

        self.window.add_view(5, view1)
        self.window.add_view(5, view2)
        self.window.add_view(5, view3)

        views = self.window.get_views()
        self.assertEqual(len(views), 3)
        # All have same priority, maintain insertion order
        self.assertEqual(views[0][1], view1)
        self.assertEqual(views[1][1], view2)
        self.assertEqual(views[2][1], view3)

    def test_remove_view_from_window(self):
        """Test removing a view from window."""
        view1 = SimpleView()
        view2 = SimpleView()

        self.window.add_view(0, view1)
        self.window.add_view(1, view2)

        self.assertEqual(len(self.window.get_views()), 2)

        self.window.remove_view(view1)
        views = self.window.get_views()
        self.assertEqual(len(views), 1)
        self.assertEqual(views[0][1], view2)

        # view1 should no longer be associated with window
        self.assertIsNone(view1.get_window())

    def test_remove_nonexistent_view(self):
        """Test removing a view that's not in the window."""
        view1 = SimpleView()
        view2 = SimpleView()

        self.window.add_view(0, view1)

        # Should not raise error when removing view that's not there
        self.window.remove_view(view2)

        # view1 should still be in window
        self.assertEqual(len(self.window.get_views()), 1)

    def test_window_tick_delegates_to_views(self):
        """Test that window.tick() calls tick on all views."""
        view1 = SimpleView()
        view2 = SimpleView()

        self.window.add_view(0, view1)
        self.window.add_view(1, view2)

        self.window.tick([])

        self.assertEqual(view1.tick_count, 1)
        self.assertEqual(view2.tick_count, 1)

    def test_window_tick_calls_views_in_priority_order(self):
        """Test that window.tick() calls views in priority order."""
        view_calls = []

        class TrackingView(View):
            def __init__(self, name):
                super().__init__()
                self.name = name

            view_type = "tracking"

            def tick(self):
                view_calls.append(self.name)

        window = ViewManagingWindow(self.env)
        view1 = TrackingView("high_priority")
        view2 = TrackingView("low_priority")

        window.add_view(0, view1)
        window.add_view(10, view2)

        window.tick([])

        # Views should be ticked in priority order (0 first)
        self.assertEqual(view_calls, ["high_priority", "low_priority"])

    def test_get_views_returns_copy(self):
        """Test that get_views() returns a copy, not the internal list."""
        view = SimpleView()
        self.window.add_view(0, view)

        views1 = self.window.get_views()
        views2 = self.window.get_views()

        # Should be equal but not the same object
        self.assertEqual(views1, views2)
        self.assertIsNot(views1, views2)
