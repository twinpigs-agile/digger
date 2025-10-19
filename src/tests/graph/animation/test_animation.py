import pygame
import os
from typing import Dict

import settings
from animations.animated import AnimatedSprite
from settings import asset_path
from tests.graph.base_surface import BaseSurfaceTest
from util.image_loader import load_image

SPRITE_SIZE = (4, 4)
SURFACE_SIZE = (4, 4)


class TestAnimatedSprite(BaseSurfaceTest):
    def __init__(self, *args, **kwargs):
        super().__init__(SURFACE_SIZE, *args, **kwargs)
        self.sprite_dir = asset_path("digger")
        self.animated_sprite = None
        self.reference_images: Dict[str, pygame.Surface] = {}

    def setUp(self):
        super().setUp()
        self.animated_sprite = AnimatedSprite(self.sprite_dir, SPRITE_SIZE)
        # Load all reference frames for variations
        for variation in self.animated_sprite.animation_data["variations"]:
            for frame_index in range(
                self.animated_sprite.animation_data["frame_count"]
            ):
                filename = f"{variation}_{frame_index}.png"
                orig_img = load_image(os.path.join(self.sprite_dir, filename)).convert()
                for direction in "ruld":
                    img = orig_img
                    for transformation in self.animated_sprite.animation_data[
                        "transform"
                    ][direction]:
                        if transformation == "mirror":
                            img = pygame.transform.flip(img, True, False)
                        elif transformation == "rotate":
                            img = pygame.transform.rotate(img, -90)
                        else:
                            self.fail(
                                f"Transformation '{transformation}' not implemented"
                            )
                    self.reference_images[f"{variation}_{frame_index}_{direction}"] = (
                        pygame.transform.scale(img, SPRITE_SIZE)
                    )

    def tearDown(self):
        self.animated_sprite = None
        self.reference_images.clear()
        super().tearDown()

    def test_render_all_combinations(self):
        animation = self.animated_sprite.create_animation()
        directions = list(self.animated_sprite.animation_data["transform"].keys())
        variations = self.animated_sprite.animation_data["variations"]
        animations = self.animated_sprite.animation_data["animations"]

        for variation in variations:
            animation.set_variation(variation)
            for anim_name, frame_sequence in animations.items():
                animation.start_animation(anim_name)
                for direction in directions:
                    animation.set_direction(direction)
                    for frame_index in frame_sequence:
                        self.surface.fill((0, 0, 0))
                        animation.current_frame_index = frame_sequence.index(
                            frame_index
                        )
                        _, anchor = self.animated_sprite.sprites[
                            (variation, frame_index, direction)
                        ]
                        animation.set_position(anchor)
                        animation.draw(self.surface)
                        expected = self.reference_images[
                            f"{variation}_{frame_index}_{direction}"
                        ]
                        if not settings.NO_DISPLAY_ON_TEST:
                            print(
                                f"Checking var={variation}, frame_index={frame_index}, direction={direction}"
                            )
                        self.assertImageEquals((0, 0), expected)

    def test_sprite_structure_and_anchors(self):
        sprites = self.animated_sprite.sprites
        variations = self.animated_sprite.animation_data["variations"]
        directions = list(self.animated_sprite.animation_data["transform"].keys())
        frame_count = self.animated_sprite.animation_data["frame_count"]

        expected_count = len(variations) * frame_count * len(directions)
        self.assertEqual(
            len(sprites), expected_count, "Sprite dictionary size mismatch"
        )

        original_size = (2, 2)  # original PNG size
        for (variation, frame_index, direction), (surface, anchor) in sprites.items():
            self.assertEqual(
                surface.get_size(),
                SPRITE_SIZE,
                f"Incorrect size for {variation}-{frame_index}-{direction}",
            )

            # Scale anchor using integer division as in AnimatedSprite._scale_anchor
            original_anchor = self.animated_sprite.animation_data["anchors"][
                frame_index
            ]
            scaled_anchor = [
                original_anchor[0] * SPRITE_SIZE[0] // original_size[0],
                original_anchor[1] * SPRITE_SIZE[1] // original_size[1],
            ]

            # Apply transformations in the same order as in AnimatedSprite._apply_transformations
            for transformation in self.animated_sprite.animation_data["transform"][
                direction
            ]:
                if transformation == "mirror":
                    scaled_anchor[0] = SPRITE_SIZE[0] - scaled_anchor[0] - 1
                elif transformation == "rotate":
                    old_anchor = scaled_anchor[:]
                    scaled_anchor = [SPRITE_SIZE[0] - old_anchor[1] - 1, old_anchor[0]]
                else:
                    self.fail(f"Transformation '{transformation}' not implemented")

            self.assertEqual(
                anchor,
                scaled_anchor,
                f"Anchor scaling mismatch for {variation}-{frame_index}-{direction}",
            )

    def test_animation_sequence(self):
        animation = self.animated_sprite.create_animation()
        animations = self.animated_sprite.animation_data["animations"]

        for anim_name, frame_sequence in animations.items():
            animation.start_animation(anim_name)
            actual_order = []
            for _ in range(len(frame_sequence)):
                actual_order.append(
                    animation.current_animation[animation.current_frame_index]
                )
                animation.next_frame()
            self.assertEqual(
                actual_order,
                frame_sequence,
                f"Frame order mismatch for animation {anim_name}",
            )
