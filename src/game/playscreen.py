import pygame
from typing import List, Tuple
from mainloop.screens import Screen, Window
from mainloop.environment import Environment


class BackgroundWindow(Window):
    """Background window with lowest priority, covering the entire screen"""

    def __init__(self, env: Environment, background_rects: List[pygame.Rect]) -> None:
        super().__init__(env)
        self.color = (50, 50, 50)  # Dark gray background
        self.background_rects = background_rects
        self.rect_color = (255, 255, 255)  # White color for background rectangles

    def tick(self, events: list[pygame.event.Event]) -> None:
        # Handle keyboard events for color switching
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Toggle between white and black
                    if self.rect_color == (255, 255, 255):  # White
                        self.set_rect_color((0, 0, 0))  # Black
                    else:
                        self.set_rect_color((255, 255, 255))  # White

        # Fill main background
        pygame.draw.rect(self.env.display, self.color, self.get_rect())

        # Draw background rectangles
        for rect in self.background_rects:
            pygame.draw.rect(self.env.display, self.rect_color, rect)

        # Draw color information
        font = pygame.font.Font(None, 36)
        color_text = "White" if self.rect_color == (255, 255, 255) else "Black"
        text = font.render(
            f"Background: {color_text} (SPACE to toggle)", True, (255, 255, 255)
        )
        text_rect = text.get_rect()
        text_rect.center = self.get_rect().center
        self.env.display.blit(text, text_rect)

    def set_rect_color(self, color: Tuple[int, int, int]) -> None:
        """Set the color for background rectangles"""
        self.rect_color = color


class GameWindow(Window):
    """Game board window"""

    def __init__(self, env: Environment, rect: pygame.Rect) -> None:
        super().__init__(env)
        self.set_rect(rect)
        self.color = (0, 255, 0)  # Green color for game board

    def tick(self, events: list[pygame.event.Event]) -> None:
        # Fill game board with green color
        pygame.draw.rect(self.env.display, self.color, self.get_rect())

        # Game board rendering logic will be here
        # TODO: Add grid and game elements rendering


class StatusWindow(Window):
    """Status window"""

    def __init__(self, env: Environment, rect: pygame.Rect) -> None:
        super().__init__(env)
        self.set_rect(rect)
        self.color = (0, 0, 255)  # Blue color for status

    def tick(self, events: list[pygame.event.Event]) -> None:
        # Fill status window with blue color
        pygame.draw.rect(self.env.display, self.color, self.get_rect())


BOARD_SIZE = (15, 10)  # Game board aspect ratio (width, height)
STATUS_WIDTH_PERCENT = 20  # Status width percentage of game board width


class PlayScreen(Screen):
    """Game screen with game board and status windows"""


    def __init__(self, env: Environment, interval: int = 60) -> None:
        super().__init__(env, interval)

        # Get display dimensions
        display_width, display_height = env.display.get_size()

        # Calculate window dimensions
        game_rect, status_rect, background_rects = self._calculate_window_rects(
            display_width, display_height
        )

        # Create windows
        background_window = BackgroundWindow(env, background_rects)
        background_window.set_rect(pygame.Rect(0, 0, display_width, display_height))

        game_window = GameWindow(env, game_rect)
        status_window = StatusWindow(env, status_rect)

        # Add windows with priorities (lower number = higher priority)
        self.add_window(1, background_window)  # Highest priority (drawn first)
        self.add_window(5, game_window)  # Game board
        self.add_window(3, status_window)  # Status

        # Store references for potential use
        self.game_window = game_window
        self.status_window = status_window
        self.background_window = background_window
        self.background_rects = background_rects

    def _calculate_window_rects(
        self, display_width: int, display_height: int
    ) -> Tuple[pygame.Rect, pygame.Rect, List[pygame.Rect]]:
        """
        Calculate rectangles for game board and status windows,
        and list of rectangles to cover the remaining screen area
        """
        # Calculate maximum game board size
        # considering BOARD_SIZE aspect ratio
        board_ratio = self.BOARD_SIZE[0] / self.BOARD_SIZE[1]  # width/height

        # Calculate status width as percentage of game board width
        # First try maximum height
        max_game_height = display_height
        max_game_width = int(max_game_height * board_ratio)

        # Check if game board + status fits in width
        status_width = int(max_game_width * self.STATUS_WIDTH_PERCENT / 100)
        total_width = max_game_width + status_width

        if total_width > display_width:
            # Need to reduce sizes
            # Calculate maximum width for game board
            max_total_width = display_width
            # status_width = game_width * STATUS_WIDTH_PERCENT / 100
            # total_width = game_width + status_width = game_width * (1 + STATUS_WIDTH_PERCENT / 100)
            max_game_width = int(
                max_total_width / (1 + self.STATUS_WIDTH_PERCENT / 100)
            )
            max_game_height = int(max_game_width / board_ratio)

            # Recalculate status width
            status_width = int(max_game_width * self.STATUS_WIDTH_PERCENT / 100)

        # Calculate total width and height of combined windows
        total_width = max_game_width + status_width
        total_height = max_game_height

        # Center the combined rectangle on screen
        combined_x = (display_width - total_width) // 2
        combined_y = (display_height - total_height) // 2

        # Define window positions (centered)
        # Game board on the left
        game_x = combined_x
        game_y = combined_y
        game_rect = pygame.Rect(game_x, game_y, max_game_width, max_game_height)

        # Status to the right of game board
        status_x = combined_x + max_game_width
        status_y = combined_y
        status_rect = pygame.Rect(status_x, status_y, status_width, max_game_height)

        # Calculate rectangles to cover remaining area
        background_rects = self._calculate_background_rects(
            display_width, display_height, game_rect, status_rect
        )

        return game_rect, status_rect, background_rects

    def _calculate_background_rects(
        self,
        display_width: int,
        display_height: int,
        game_rect: pygame.Rect,
        status_rect: pygame.Rect,
    ) -> List[pygame.Rect]:
        """
        Calculate minimum number of rectangles to cover
        the remaining screen area around centered windows
        """
        rects = []

        # Calculate the combined occupied area
        left_x = min(game_rect.left, status_rect.left)
        right_x = max(game_rect.right, status_rect.right)
        top_y = min(game_rect.top, status_rect.top)
        bottom_y = max(game_rect.bottom, status_rect.bottom)

        # Area to the left of the combined windows
        if left_x > 0:
            left_rect = pygame.Rect(0, 0, left_x, display_height)
            rects.append(left_rect)

        # Area to the right of the combined windows
        if right_x < display_width:
            right_rect = pygame.Rect(
                right_x, 0, display_width - right_x, display_height
            )
            rects.append(right_rect)

        # Area above the combined windows
        if top_y > 0:
            top_rect = pygame.Rect(left_x, 0, right_x - left_x, top_y)
            rects.append(top_rect)

        # Area below the combined windows
        if bottom_y < display_height:
            bottom_rect = pygame.Rect(
                left_x, bottom_y, right_x - left_x, display_height - bottom_y
            )
            rects.append(bottom_rect)

        return rects

    def get_game_window(self) -> GameWindow:
        """Return game board window"""
        return self.game_window

    def get_status_window(self) -> StatusWindow:
        """Return status window"""
        return self.status_window

    def get_background_window(self) -> BackgroundWindow:
        """Return background window"""
        return self.background_window

    def get_background_rects(self) -> List[pygame.Rect]:
        """Return list of rectangles for background areas"""
        return self.background_rects

    def set_background_rect_color(self, color: Tuple[int, int, int]) -> None:
        """Set the color for background rectangles"""
        self.background_window.set_rect_color(color)
