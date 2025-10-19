import unittest
import pygame
import os
from typing import Tuple

import settings

SCREEN_SIZE: Tuple[int, int] = (8, 6)


class BaseSurfaceTest(unittest.TestCase):
    def __init__(self, size: Tuple[int, int] = SCREEN_SIZE, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._size: Tuple[int, int] = size
        self.surface: pygame.Surface | None = None

    def setUp(self) -> None:
        if settings.NO_DISPLAY_ON_TEST:
            os.environ["SDL_VIDEODRIVER"] = "dummy"

        pygame.init()
        pygame.display.init()
        self.surface = pygame.Surface(self._size)

        # Если NO_DISPLAY_ON_TEST, создаём отдельную поверхность
        # Иначе используем поверхность окна
        if settings.NO_DISPLAY_ON_TEST:
            pygame.display.set_mode(self._size)
        else:
            pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    def tearDown(self) -> None:
        self.surface = None
        pygame.quit()

    # Helpers
    def fill_pixel(self, pos: Tuple[int, int], color: Tuple[int, int, int]) -> None:
        assert self.surface is not None
        self.surface.set_at(pos, color)

    def get_pixel(self, pos: Tuple[int, int]) -> pygame.Color:
        assert self.surface is not None
        return self.surface.get_at(pos)

    def get_image(self, rect: pygame.Rect) -> pygame.Surface:
        assert self.surface is not None
        return self.surface.subsurface(rect).copy()

    # Assertions
    def assertPixelEquals(
        self, pos: Tuple[int, int], color: Tuple[int, int, int]
    ) -> None:
        actual = self.get_pixel(pos)
        self.assertEqual(
            actual[:3], color, f"Pixel at {pos} is {actual}, expected {color}"
        )

    def assertImageEquals(
        self, lefttop: Tuple[int, int], other_image: pygame.Surface
    ) -> None:
        w, h = other_image.get_size()
        rect = pygame.Rect(lefttop, (w, h))
        sub_img = self.get_image(rect)
        if not settings.NO_DISPLAY_ON_TEST:
            zoom_factor = settings.ASSERT_VIEW_ZOOM
            zoomed_size = (w * zoom_factor, h * zoom_factor)

            z_sub = pygame.transform.scale(sub_img, zoomed_size)
            z_other = pygame.transform.scale(other_image, zoomed_size)
            screen = pygame.display.get_surface()
            screen.fill((0, 0, 0))
            if screen is None:
                raise RuntimeError("Display surface not initialized")
            screen.fill((255, 255, 255))  # Белый фон
            screen.blit(z_sub, (0, 0))
            screen.blit(z_other, (z_sub.get_width() + 10, 0))
            pygame.display.flip()
            pass  # Put a breakpoint here

        for x in range(w):
            for y in range(h):
                expected = other_image.get_at((x, y))[:3]
                actual = sub_img.get_at((x, y))[:3]
                if actual != expected:
                    self.fail(
                        f"Mismatch at ({x},{y}) in region starting {lefttop}: "
                        f"expected {expected}, got {actual}"
                    )
        pass  # Put a breakpoint here
