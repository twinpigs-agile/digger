"""Tests for HobbinView rendering."""

import pygame
import os

from mainloop.environment import Environment
from mainloop.screens import Window
from views.hobbin_view import HobbinView
from settings import ASSETS_DIR
from tests.graph.base_surface import BaseSurfaceTest


SPRITE_SIZE = (2, 2)
SURFACE_SIZE = (4, 4)


class TestHobbinView(BaseSurfaceTest):
    """Tests for HobbinView class."""

    def __init__(self, *args, **kwargs):
        super().__init__(SURFACE_SIZE, *args, **kwargs)
        self.hobbin_path = os.path.join(ASSETS_DIR, "hobbin")
        self.env = None
        self.window = None

    def setUp(self):
        super().setUp()
        # Create environment and window for view testing
        self.env = Environment(self.surface)

        # Create a simple window for testing
        class TestWindow(Window):
            def tick(self, events):
                # Call tick on all views
                for _, view in self._views:
                    view.tick()

        self.window = TestWindow(self.env)
        self.window.set_rect(pygame.Rect(1, 1, 2, 2))  # Set window at (1,1)

    def tearDown(self):
        self.env = None
        self.window = None
        super().tearDown()

    def test_hobbin_view_type(self):
        """Test that HobbinView has correct type."""
        view = HobbinView(SPRITE_SIZE)
        self.assertEqual(view.view_type, "hobbin")

    def test_hobbin_view_initialization(self):
        """Test that HobbinView initializes correctly."""
        view = HobbinView(SPRITE_SIZE)
        self.assertIsNotNone(view.animation)
        self.assertIsNotNone(view.animated_sprite)
        self.assertEqual(view.get_position(), (0, 0))

    def test_hobbin_direction_setting(self):
        """Test hobbin direction can be set."""
        view = HobbinView(SPRITE_SIZE)

        # Test setting all directions
        view.set_direction("r")
        self.assertEqual(view.animation.direction, "r")

        view.set_direction("l")
        self.assertEqual(view.animation.direction, "l")

        view.set_direction("u")
        self.assertEqual(view.animation.direction, "u")

        view.set_direction("d")
        self.assertEqual(view.animation.direction, "d")

    def test_hobbin_animation_sequence(self):
        """Test hobbin animation has correct structure."""
        view = HobbinView(SPRITE_SIZE)

        # Should have 2 frames
        self.assertEqual(view.animation.get_animation_length(), 2)
        self.assertEqual(view.animation.get_current_frame(), 0)

    def test_hobbin_rendering_with_anchor(self):
        """Test hobbin rendering considers anchor point."""
        view = HobbinView(SPRITE_SIZE)

        # Anchor is at (1, 1) for each frame in animation.json
        # To place sprite's top-left corner at window position (0, 0),
        # we need to set position at anchor point: (1, 1)
        # So that: draw_pos = position - anchor = (1, 1) - (1, 1) = (0, 0)
        view.set_position((1, 1))
        view.set_direction("r")
        view.animation.set_current_frame(0)

        self.window.add_view(0, view)

        # Clear surface with black
        self.surface.fill((0, 0, 0))

        # Draw the view
        view.tick()

        # Window is at screen position (1, 1)
        # Source sprite is 1x1 (FF0000.png), scaled to SPRITE_SIZE (2, 2)
        # Sprite should draw at window local (0, 0) which is screen (1, 1)
        drawn_pixels = 0
        for x in range(1, 3):  # Check 2x2 area
            for y in range(1, 3):
                pixel = self.surface.get_at((x, y))
                if pixel[:3] == (255, 0, 0):  # Red from FF0000.png
                    drawn_pixels += 1

        # Should have drawn at least one red pixel
        self.assertGreater(
            drawn_pixels,
            0,
            f"Should draw red sprite pixels at (1,1), got {drawn_pixels} red pixels",
        )

    def test_hobbin_frame_advancement(self):
        """Test hobbin animation frame advancement through view."""
        view = HobbinView(SPRITE_SIZE)
        view.set_position((0, 0))
        view.set_direction("r")

        self.window.add_view(0, view)

        # Initially at frame 0
        self.assertEqual(view.animation.get_current_frame(), 0)

        # Clear surface
        self.surface.fill((0, 0, 0))

        # First tick renders frame 0 and advances
        view.tick()
        self.assertEqual(view.animation.get_current_frame(), 1)

        # Second tick renders frame 1 and wraps
        self.surface.fill((0, 0, 0))
        view.tick()
        self.assertEqual(view.animation.get_current_frame(), 0)

    def test_hobbin_orphaned_view(self):
        """Test that hobbin view handles being orphaned gracefully."""
        view = HobbinView(SPRITE_SIZE)
        view.set_position((0, 0))
        view.set_direction("r")

        # Don't add to window - view is orphaned

        # Clear surface
        self.surface.fill((0, 0, 0))

        # Tick should not raise error
        view.tick()

        # Surface should remain unchanged (no drawing)
        # All pixels should still be black
        self.assertPixelEquals((0, 0), (0, 0, 0))
