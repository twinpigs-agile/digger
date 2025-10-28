"""HobbinView - A simple animated hobbin sprite view for testing."""

from typing import Tuple

from animations.animated import AnimatedSprite
from animations.common_views import AnimatedSpriteView


class HobbinView(AnimatedSpriteView):
    """
    A specialized AnimatedSpriteView for rendering a hobbin sprite.
    Accepts an AnimatedSprite and provides a simple view interface.
    """

    view_type = "hobbin"

    def __init__(
        self,
        animated_sprite: AnimatedSprite,
        size: Tuple[int, int] = (2, 2),
    ) -> None:
        """
        Initialize the hobbin view.

        Args:
            animated_sprite: The AnimatedSprite instance to use.
            size: The sprite size (width, height) in pixels. Used for reference only.
        """
        # Initialize parent with the animated sprite
        super().__init__(animated_sprite)
