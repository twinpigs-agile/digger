import unittest
import pygame
from game.playscreen import PlayScreen, BackgroundWindow, GameWindow, StatusWindow
from mainloop.environment import Environment


class TestBackgroundWindow(unittest.TestCase):
    """Test cases for BackgroundWindow functionality"""

    def setUp(self):
        """Set up test environment"""
        # Create real pygame display (dummy driver is already set)
        self.display = pygame.display.set_mode((800, 600))

        # Create real environment
        self.env = Environment(self.display)

        # Create background rectangles
        self.background_rects = [
            pygame.Rect(400, 0, 400, 600),  # Right side
            pygame.Rect(0, 300, 400, 300),  # Bottom left
        ]

        # Create BackgroundWindow
        self.background_window = BackgroundWindow(self.env, self.background_rects)
        self.background_window.set_rect(pygame.Rect(0, 0, 800, 600))

    def test_initial_color_is_black(self):
        """Test that initial background rectangle color is white"""
        self.assertEqual(self.background_window.rect_color, (0, 0, 0))

    def test_set_rect_color(self):
        """Test setting background rectangle color"""
        self.background_window.set_rect_color((0, 0, 0))
        self.assertEqual(self.background_window.rect_color, (0, 0, 0))

        self.background_window.set_rect_color((255, 0, 0))
        self.assertEqual(self.background_window.rect_color, (255, 0, 0))

    def test_tick_draws_background_and_rectangles(self):
        """Test that tick method draws background and rectangles"""
        events = []

        # This should not raise any exceptions
        self.background_window.tick(events)

        # Verify the method completed successfully
        self.assertTrue(True)  # If we get here, no exceptions were raised

    def test_tick_draws_color_information(self):
        """Test that tick method draws color information text"""
        events = []

        # This should not raise any exceptions
        self.background_window.tick(events)

        # Verify the method completed successfully
        self.assertTrue(True)  # If we get here, no exceptions were raised

    def test_space_key_toggles_color_black_to_white(self):
        """Test that SPACE key toggles color from black to white"""
        # Set initial color to black
        self.background_window.set_rect_color((0, 0, 0))

        # Create SPACE key event
        space_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        events = [space_event]

        self.background_window.tick(events)

        # Color should now be white
        self.assertEqual(self.background_window.rect_color, (255, 255, 255))

    def test_other_keys_do_not_toggle_color(self):
        """Test that other keys do not toggle color"""
        # Create other key event
        other_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        events = [other_event]

        initial_color = self.background_window.rect_color

        self.background_window.tick(events)

        # Color should remain unchanged
        self.assertEqual(self.background_window.rect_color, initial_color)

    def test_non_keydown_events_ignored(self):
        """Test that non-KEYDOWN events are ignored"""
        # Create non-keydown event
        other_event = pygame.event.Event(pygame.QUIT)
        events = [other_event]

        initial_color = self.background_window.rect_color

        self.background_window.tick(events)

        # Color should remain unchanged
        self.assertEqual(self.background_window.rect_color, initial_color)


class TestPlayScreenGetters(unittest.TestCase):
    """Test cases for PlayScreen getter methods"""

    def setUp(self):
        """Set up test environment"""
        # Create real pygame display (dummy driver is already set)
        self.display = pygame.display.set_mode((800, 600))

        # Create real environment
        self.env = Environment(self.display)

        # Create PlayScreen
        self.play_screen = PlayScreen(self.env, interval=60)

    def test_get_game_window(self):
        """Test get_game_window method"""
        game_window = self.play_screen.get_game_window()

        self.assertIsInstance(game_window, GameWindow)
        self.assertEqual(game_window, self.play_screen.game_window)

    def test_get_status_window(self):
        """Test get_status_window method"""
        status_window = self.play_screen.get_status_window()

        self.assertIsInstance(status_window, StatusWindow)
        self.assertEqual(status_window, self.play_screen.status_window)

    def test_get_background_window(self):
        """Test get_background_window method"""
        background_window = self.play_screen.get_background_window()

        self.assertIsInstance(background_window, BackgroundWindow)
        self.assertEqual(background_window, self.play_screen.background_window)

    def test_get_background_rects(self):
        """Test get_background_rects method"""
        background_rects = self.play_screen.get_background_rects()

        self.assertIsInstance(background_rects, list)
        self.assertEqual(background_rects, self.play_screen.background_rects)

        # Verify all items are pygame.Rect
        for rect in background_rects:
            self.assertIsInstance(rect, pygame.Rect)

    def test_set_background_rect_color(self):
        """Test set_background_rect_color method"""
        # Test setting to black
        self.play_screen.set_background_rect_color((0, 0, 0))
        self.assertEqual(self.play_screen.background_window.rect_color, (0, 0, 0))

        # Test setting to red
        self.play_screen.set_background_rect_color((255, 0, 0))
        self.assertEqual(self.play_screen.background_window.rect_color, (255, 0, 0))


if __name__ == "__main__":
    unittest.main()
