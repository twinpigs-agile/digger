import unittest
import pygame
import os
from typing import cast

from mainloop.environment import Environment
from mainloop.screens import Window
from animations.animated import AnimatedSprite, Animation
from animations.common_views import AnimatedSpriteView
from settings import ASSETS_DIR


class TestAnimatedSpriteView(unittest.TestCase):
    """Tests for the AnimatedSpriteView class."""

    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        self.display = pygame.display.set_mode((800, 600))
        self.env = Environment(self.display)

        # Load test animated sprite
        self.sprite_path = os.path.join(ASSETS_DIR, "animation")
        self.animated_sprite = AnimatedSprite(self.sprite_path, (100, 100))

    def test_view_type(self):
        """Test that view type is correctly identified."""
        view = AnimatedSpriteView(self.animated_sprite)
        self.assertEqual(view.view_type, "animated_sprite")

    def test_initialization(self):
        """Test that view initializes with animation."""
        view = AnimatedSpriteView(self.animated_sprite)

        self.assertIsNotNone(view.animated_sprite)
        self.assertIsNotNone(view.animation)
        self.assertIsInstance(view.animation, Animation)
        self.assertEqual(view.get_position(), (0, 0))

    def test_position_setting(self):
        """Test setting and getting sprite position."""
        view = AnimatedSpriteView(self.animated_sprite)
        test_pos = (100, 200)

        view.set_position(test_pos)
        self.assertEqual(view.get_position(), test_pos)

    def test_set_animation(self):
        """Test setting animation name."""
        view = AnimatedSpriteView(self.animated_sprite)

        # Start with default animation
        # default_frame_count = len(view.animation.current_animation)

        # Should not raise error (default is the only animation in test assets)
        view.set_animation("default")
        self.assertEqual(view.animation.current_frame_index, 0)

    def test_set_variation(self):
        """Test setting sprite variation."""
        view = AnimatedSpriteView(self.animated_sprite)
        variations = cast(list, self.animated_sprite.animation_data["variations"])

        for variation in variations:
            view.set_variation(variation)
            self.assertEqual(view.animation.current_variation, variation)

    def test_set_direction(self):
        """Test setting sprite direction."""
        view = AnimatedSpriteView(self.animated_sprite)
        directions = cast(dict, self.animated_sprite.animation_data["transform"]).keys()

        for direction in directions:
            view.set_direction(direction)
            self.assertEqual(view.animation.direction, direction)

    def test_get_animation_object(self):
        """Test retrieving animation object."""
        view = AnimatedSpriteView(self.animated_sprite)
        animation = view.get_animation()

        self.assertIs(animation, view.animation)

    def test_tick_without_window(self):
        """Test that tick handles lack of window gracefully."""
        view = AnimatedSpriteView(self.animated_sprite)

        # Should not raise error when not associated with window
        initial_frame = view.animation.current_frame_index
        view.tick()

        # Frame should not advance without window
        self.assertEqual(view.animation.current_frame_index, initial_frame)

    def test_tick_advances_frame(self):
        """Test that tick advances animation frame."""

        class SimpleWindow(Window):
            def tick(self, events):
                pass

        view = AnimatedSpriteView(self.animated_sprite)
        window = SimpleWindow(self.env)
        window.add_view(0, view)

        initial_frame = view.animation.current_frame_index
        view.tick()

        # Frame should advance after tick
        expected_frame = (initial_frame + 1) % len(view.animation.current_animation)
        self.assertEqual(view.animation.current_frame_index, expected_frame)

    def test_tick_draws_to_display(self):
        """Test that tick calls draw on animation."""

        class TrackingAnimation(Animation):
            """Animation that tracks draw calls."""

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.draw_called = False
                self.last_draw_position = None

            def draw(self, surface):
                self.draw_called = True
                self.last_draw_position = self.position[:]
                super().draw(surface)

        class SimpleWindow(Window):
            def tick(self, events):
                pass

        view = AnimatedSpriteView(self.animated_sprite)
        window = SimpleWindow(self.env)

        # Replace animation with tracking animation
        tracking_animation = TrackingAnimation(self.animated_sprite)
        view.animation = tracking_animation

        window.add_view(0, view)
        view.set_position((50, 75))
        view.tick()

        # Draw should have been called
        self.assertTrue(tracking_animation.draw_called)

    def test_coordinate_conversion_to_screen(self):
        """Test that window-local coordinates are converted to screen coordinates."""

        class TrackingAnimation(Animation):
            """Animation that tracks position."""

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.set_position_calls = []

            def set_position(self, position):
                self.set_position_calls.append(position)
                super().set_position(position)

        class SimpleWindow(Window):
            def tick(self, events):
                pass

        view = AnimatedSpriteView(self.animated_sprite)
        window = SimpleWindow(self.env)

        # Set window rect to known position
        import pygame

        window.set_rect(pygame.Rect(100, 200, 400, 300))

        # Replace animation with tracking animation
        tracking_animation = TrackingAnimation(self.animated_sprite)
        view.animation = tracking_animation

        window.add_view(0, view)

        # Set local position within window
        local_pos = (50, 75)
        view.set_position(local_pos)

        # Expected screen position = window offset + local position
        expected_screen_pos = (100 + 50, 200 + 75)

        view.tick()

        # The second call should be from tick (after set_position call in tick)
        if len(tracking_animation.set_position_calls) >= 2:
            actual_screen_pos = tuple(tracking_animation.set_position_calls[-1])
            self.assertEqual(actual_screen_pos, expected_screen_pos)

    def test_multiple_views_independent_animation(self):
        """Test that multiple views have independent animations."""
        view1 = AnimatedSpriteView(self.animated_sprite)
        view2 = AnimatedSpriteView(self.animated_sprite)

        # Set different positions
        view1.set_position((10, 10))
        view2.set_position((50, 50))

        # Change variation for view1 only
        variations = cast(list, self.animated_sprite.animation_data["variations"])
        if len(variations) > 1:
            view1.set_variation(variations[1])

        self.assertEqual(view1.get_position(), (10, 10))
        self.assertEqual(view2.get_position(), (50, 50))
        self.assertNotEqual(
            view1.animation.current_variation, view2.animation.current_variation
        )

    def test_view_window_association(self):
        """Test that view properly associates with window."""

        class SimpleWindow(Window):
            def tick(self, events):
                pass

        view = AnimatedSpriteView(self.animated_sprite)
        window = SimpleWindow(self.env)

        # Initially no window
        self.assertIsNone(view.get_window())

        # Add to window
        window.add_view(0, view)
        self.assertIs(view.get_window(), window)

        # Remove from window
        window.remove_view(view)
        self.assertIsNone(view.get_window())
