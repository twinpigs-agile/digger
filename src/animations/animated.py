import os
import json
import pygame
from typing import Dict, Tuple, List, cast

from util.sopen import smart_open
from util.image_loader import load_image


class AnimatedSprite:
    def __init__(self, path: str, size: Tuple[int, int]) -> None:
        self.path = path
        self.size = size
        self.animation_data = self._load_animation_data()
        self.sprites = self._load_sprites()

    def _load_animation_data(
        self,
    ) -> Dict[str, int | str | List[Tuple[int, int]] | Dict[str, int | str]]:
        with smart_open(os.path.join(self.path, "animation.json")) as f:
            return cast(
                Dict[str, int | str | List[Tuple[int, int]] | Dict[str, int | str]],
                json.load(f),
            )

    def _load_sprites(
        self,
    ) -> Dict[Tuple[str, int, str], Tuple[pygame.Surface, List[int]]]:
        sprites = {}
        for variation in cast(Dict[str, List[int]], self.animation_data["variations"]):
            for frame_index in range(cast(int, self.animation_data["frame_count"])):
                filename = f"{variation}_{frame_index}.png"
                image = load_image(os.path.join(self.path, filename)).convert_alpha()
                original_size = image.get_size()
                image = pygame.transform.scale(image, self.size)
                for direction in cast(List[str], self.animation_data["transform"]):
                    anchor = self._scale_anchor(
                        cast(List[List[int]], self.animation_data["anchors"])[
                            frame_index
                        ],
                        original_size,
                    )
                    sprites[(variation, frame_index, direction)] = (
                        self._apply_transformations(image, direction, anchor)
                    )
        return sprites

    def _scale_anchor(
        self, anchor: List[int], original_size: Tuple[int, int]
    ) -> List[int]:
        scaled_anchor = [
            anchor[0] * self.size[0] // original_size[0],
            anchor[1] * self.size[1] // original_size[1],
        ]
        return scaled_anchor

    def _apply_transformations(
        self, image: pygame.Surface, direction: str, anchor: List[int]
    ) -> Tuple[pygame.Surface, List[int]]:
        transformations = cast(Dict[str, List[str]], self.animation_data["transform"])[
            direction
        ]

        for transformation in transformations:
            if transformation == "mirror":
                # Flip horizontally
                image = pygame.transform.flip(image, True, False)
                anchor[0] = image.get_width() - anchor[0] - 1

            elif transformation == "rotate":
                # Rotate 90° clockwise
                image = pygame.transform.rotate(image, -90)
                old_anchor = anchor[:]
                # Rotate anchor around origin (0,0)
                anchor = [image.get_width() - old_anchor[1] - 1, old_anchor[0]]

            else:
                raise ValueError(f"Unknown transformation: {transformation}")

        return image, anchor

    """def _apply_transformations(
            self,
            image: pygame.Surface,
            direction: str,
            anchor: List[int]
    ) -> Tuple[pygame.Surface, List[int]]:
        transformations = self.animation_data['transform'][direction]

        for transformation in transformations:
            if transformation == 'mirror':
                image = pygame.transform.flip(image, True, False)
                anchor[0] = image.get_width() - anchor[0]

            elif transformation == 'rotate':
                image = pygame.transform.rotate(image, -90)
                old_anchor = anchor[:]
                anchor = [image.get_width() - old_anchor[1], old_anchor[0]]

            else:
                raise ValueError(f"Unknown transformation: {transformation}")

        return image, anchor
    """

    def create_animation(self) -> "Animation":
        return Animation(self)


class Animation:
    def __init__(self, animated_sprite: "AnimatedSprite") -> None:
        self.animated_sprite = animated_sprite
        self.current_variation = cast(
            List[str], self.animated_sprite.animation_data["variations"]
        )[
            0
        ]  # First available variation
        self.current_animation = cast(
            Dict[str, List[int]], self.animated_sprite.animation_data["animations"]
        )["default"]
        self.current_frame_index = 0
        self.position = [0, 0]  # Initial sprite position
        self.direction = "r"  # Initial direction

    def draw(self, surface: pygame.Surface) -> None:
        frame_index = self.current_animation[self.current_frame_index]
        frame, anchor = self.animated_sprite.sprites[
            (self.current_variation, frame_index, self.direction)
        ]
        surface.blit(
            frame, (self.position[0] - anchor[0], self.position[1] - anchor[1])
        )

    def set_variation(self, variation: str) -> None:
        self.current_variation = variation

    def set_direction(self, direction: str) -> None:
        self.direction = direction

    def start_animation(self, animation_name: str) -> None:
        self.current_animation = cast(
            Dict[str, List[int]], self.animated_sprite.animation_data["animations"]
        )[animation_name]
        self.current_frame_index = 0

    def next_frame(self) -> None:
        self.current_frame_index += 1
        if self.current_frame_index >= len(self.current_animation):
            self.current_frame_index = 0

    def is_at_start(self) -> bool:
        return self.current_frame_index == 0

    def set_position(self, position: Tuple[int, int]) -> None:
        self.position = list(position)
