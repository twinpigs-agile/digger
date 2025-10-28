from typing import Tuple

from mainloop.screens import View
from animations.animated import AnimatedSprite, Animation


class AnimatedSpriteView(View):
    """
    View for rendering an animated sprite.
    Takes an AnimatedSprite and creates an Animation to manage frame progression.
    Draws the sprite to the window's surface during tick.
    """

    view_type = "animated_sprite"

    def __init__(self, animated_sprite: AnimatedSprite) -> None:
        """
        Initialize the animated sprite view.

        Args:
            animated_sprite: The AnimatedSprite instance to animate and render.
        """
        super().__init__()
        self.animated_sprite = animated_sprite
        self.animation = animated_sprite.create_animation()
        self._position: Tuple[int, int] = (0, 0)

    def tick(self) -> None:
        """
        Update animation frame and draw to parent window.
        Called each frame by the window's tick method.
        """
        window = self.get_window()
        if window is None:
            return

        # Convert position from local window coordinates to screen coordinates
        screen_pos = window.to_screen_coords(self._position)
        self.animation.set_position(screen_pos)
        self.animation.draw(window.env.display)

        # Advance to next frame
        self.animation.next_frame()

    def set_position(self, position: Tuple[int, int]) -> None:
        """
        Set the position of the sprite within the window.

        Args:
            position: (x, y) position in local window coordinates.
        """
        self._position = position
        # Don't set animation position yet - it will be done during tick()
        # when we convert to screen coordinates

    def get_position(self) -> Tuple[int, int]:
        """Get the current position of the sprite."""
        return self._position

    def set_animation(self, animation_name: str) -> None:
        """
        Start a new animation sequence.

        Args:
            animation_name: Name of the animation to start.
        """
        self.animation.start_animation(animation_name)

    def set_variation(self, variation: str) -> None:
        """
        Set the sprite variation (e.g., "idle", "walk").

        Args:
            variation: Name of the variation.
        """
        self.animation.set_variation(variation)

    def set_direction(self, direction: str) -> None:
        """
        Set the sprite direction.

        Args:
            direction: Direction code (e.g., "r", "l", "u", "d").
        """
        self.animation.set_direction(direction)

    def get_animation(self) -> Animation:
        """Get the animation object for advanced control."""
        return self.animation
