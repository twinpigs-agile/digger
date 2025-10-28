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
        self.sprite_dir = asset_path("animation")
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
            for i in range(len(frame_sequence)):
                actual_order.append(
                    animation.current_animation[animation.current_frame_index]
                )
                self.assertTrue(animation.is_at_start() != bool(i))
                animation.next_frame()
            self.assertEqual(
                actual_order,
                frame_sequence,
                f"Frame order mismatch for animation {anim_name}",
            )

    def test_bad_animation(self):
        self.assertRaises(
            ValueError, AnimatedSprite, asset_path("bad_animation"), (1, 1)
        )

    def test_optional_transform_handling(self):
        """Test that sprite without transform section loads correctly."""
        no_transform_dir = asset_path("no_transform")
        sprite = AnimatedSprite(no_transform_dir, (1, 1))

        # Should have loaded successfully
        self.assertIsNotNone(sprite.animation_data)
        self.assertNotIn("transform", sprite.animation_data)

        # Create animation and verify it works
        animation = sprite.create_animation()
        self.assertEqual(animation.direction, "r")

        # Should be able to set all directions
        for direction in ["r", "l", "u", "d"]:
            animation.set_direction(direction)
            self.assertEqual(animation.direction, direction)
            # Should not raise error when drawing
            animation.draw(self.surface)

    def test_shared_sprite_references_without_transform(self):
        """Test that all directions share same sprite object when transform is absent."""
        no_transform_dir = asset_path("no_transform")
        sprite = AnimatedSprite(no_transform_dir, (1, 1))

        # Get sprites for same frame/variation but different directions
        key_r = ("a", 0, "r")
        key_l = ("a", 0, "l")
        key_u = ("a", 0, "u")
        key_d = ("a", 0, "d")

        sprite_r = sprite.sprites[key_r]
        sprite_l = sprite.sprites[key_l]
        sprite_u = sprite.sprites[key_u]
        sprite_d = sprite.sprites[key_d]

        # All should be the same object (not copies)
        self.assertIs(
            sprite_r, sprite_l, "Sprites should be same object for l direction"
        )
        self.assertIs(
            sprite_r, sprite_u, "Sprites should be same object for u direction"
        )
        self.assertIs(
            sprite_r, sprite_d, "Sprites should be same object for d direction"
        )

        # Verify they're tuples with same surface and anchor
        surface_r, anchor_r = sprite_r
        surface_l, anchor_l = sprite_l
        self.assertIs(surface_r, surface_l, "Surface objects should be identical")
        self.assertEqual(anchor_r, anchor_l, "Anchors should be equal")

    def test_animation_length_method(self):
        """Test get_animation_length method."""
        animation = self.animated_sprite.create_animation()

        # Default animation length
        animations = self.animated_sprite.animation_data["animations"]
        expected_length = len(animations["default"])
        self.assertEqual(animation.get_animation_length(), expected_length)

        # Test with different animations
        for anim_name, frame_sequence in animations.items():
            animation.start_animation(anim_name)
            self.assertEqual(animation.get_animation_length(), len(frame_sequence))

    def test_get_current_frame(self):
        """Test get_current_frame method."""
        animation = self.animated_sprite.create_animation()
        length = animation.get_animation_length()

        # Initial frame is 0
        self.assertEqual(animation.get_current_frame(), 0)

        # After next_frame
        animation.next_frame()
        self.assertEqual(animation.get_current_frame(), 1)

        # Test frame progression
        current = animation.get_current_frame()
        animation.next_frame()
        expected_next = (current + 1) % length
        self.assertEqual(animation.get_current_frame(), expected_next)

        # Test wrapping by advancing to end
        animation.set_current_frame(length - 1)
        self.assertEqual(animation.get_current_frame(), length - 1)
        animation.next_frame()
        self.assertEqual(animation.get_current_frame(), 0)  # Should wrap to 0

    def test_set_current_frame(self):
        """Test set_current_frame method."""
        animation = self.animated_sprite.create_animation()
        length = animation.get_animation_length()

        # Set to valid frame
        animation.set_current_frame(0)
        self.assertEqual(animation.get_current_frame(), 0)

        animation.set_current_frame(1)
        self.assertEqual(animation.get_current_frame(), 1)

        # Set to last frame
        animation.set_current_frame(length - 1)
        self.assertEqual(animation.get_current_frame(), length - 1)

    def test_set_current_frame_wrapping(self):
        """Test that set_current_frame wraps frame index."""
        animation = self.animated_sprite.create_animation()
        length = animation.get_animation_length()

        # Set frame beyond length (should wrap)
        animation.set_current_frame(length + 1)
        self.assertEqual(animation.get_current_frame(), 1)

        # Set frame much beyond length
        animation.set_current_frame(length * 3 + 2)
        self.assertEqual(animation.get_current_frame(), 2)

    def test_set_current_frame_negative_raises_error(self):
        """Test that set_current_frame rejects negative indices."""
        animation = self.animated_sprite.create_animation()

        with self.assertRaises(ValueError):
            animation.set_current_frame(-1)

        with self.assertRaises(ValueError):
            animation.set_current_frame(-100)

    def test_frame_control_with_different_animations(self):
        """Test frame control with different animation sequences."""
        animation = self.animated_sprite.create_animation()
        animations = self.animated_sprite.animation_data["animations"]

        for anim_name, frame_sequence in animations.items():
            animation.start_animation(anim_name)
            length = animation.get_animation_length()

            # Set different frames and verify
            for i in range(length):
                animation.set_current_frame(i)
                self.assertEqual(animation.get_current_frame(), i)
                # Verify correct frame is in animation
                expected_frame = frame_sequence[i]
                actual_frame = animation.current_animation[
                    animation.current_frame_index
                ]
                self.assertEqual(actual_frame, expected_frame)
