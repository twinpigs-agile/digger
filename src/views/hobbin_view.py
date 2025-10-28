"""HobbinView - A simple animated hobbin sprite view for testing."""

import os
from typing import Tuple

from animations.animated import AnimatedSprite
from animations.common_views import AnimatedSpriteView
from settings import ASSETS_DIR


class HobbinView(AnimatedSpriteView):
    """
    A specialized AnimatedSpriteView for rendering a hobbin sprite.
    Loads hobbin sprite from test_assets and provides a simple view interface.
    """

    view_type = "hobbin"

    def __init__(self, size: Tuple[int, int] = (2, 2)) -> None:
        """
        Initialize the hobbin view.

        Args:
            size: The sprite size (width, height) in pixels. Default (2, 2).
        """
        # Load hobbin sprite from test_assets
        hobbin_path = os.path.join(ASSETS_DIR, "hobbin")
        animated_sprite = AnimatedSprite(hobbin_path, size)

        # Initialize parent with the animated sprite
        super().__init__(animated_sprite)
