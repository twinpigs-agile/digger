import unittest
from unittest.mock import Mock
from game.playscreen import PlayScreen
from mainloop.environment import Environment


class TestGameWindowsBase(unittest.TestCase):
    """Base test class for game window rectangle calculations"""

    def setUp(self):
        """Set up test environment"""
        # Mock pygame display
        self.mock_display = Mock()
        self.mock_display.get_size.return_value = (1920, 1080)

        # Mock environment
        self.env = Mock(spec=Environment)
        self.env.display = self.mock_display
        self.env.clock = Mock()

    def create_play_screen(
        self,
        display_width: int,
        display_height: int,
        board_size=(15, 10),
        status_width_percent=20,
    ):
        """Helper to create PlayScreen with custom parameters"""
        self.mock_display.get_size.return_value = (display_width, display_height)
        return PlayScreen(
            self.env,
            interval=60,
            board_size=board_size,
            status_width_percent=status_width_percent,
        )

    def test_wide_display_default_config(self):
        """Test window calculation for wide display with default config (15x10, 20%)"""
        # Default: board_size=(15, 10), status_width_percent=20
        # For 1920x1080: total needs to fit, so:
        # max_game_width = 1920 / (1 + 0.2) = 1600
        # max_game_height = 1600 / (15/10) = 1066 (rounded)
        play_screen = self.create_play_screen(1920, 1080)
        game_rect, status_rect, background_rects = play_screen._calculate_window_rects(
            1920, 1080
        )

        # Game board height is limited by width constraint, not full display height
        self.assertEqual(game_rect.width, 1600)  # 1920 / 1.2
        self.assertAlmostEqual(game_rect.height, 1066, delta=1)  # 1600 / 1.5

        # Status window should be 20% of game board width
        self.assertEqual(status_rect.width, 320)  # 1600 * 0.2
        self.assertEqual(status_rect.height, game_rect.height)

        # Status should be adjacent to game board
        self.assertEqual(status_rect.left, game_rect.right)
        self.assertEqual(status_rect.top, game_rect.top)

        # Combined width should equal display width
        self.assertEqual(game_rect.width + status_rect.width, 1920)

    def test_narrow_display_default_config(self):
        """Test window calculation for narrow display with default config"""
        # For 800x600 with board_size=(15, 10), status_width_percent=20:
        # max_game_width = 800 / 1.2 = 666
        # max_game_height = 666 / 1.5 = 444
        play_screen = self.create_play_screen(800, 600)
        game_rect, status_rect, background_rects = play_screen._calculate_window_rects(
            800, 600
        )

        # Game board is constrained by width
        self.assertEqual(game_rect.width, 666)  # 800 / 1.2
        self.assertAlmostEqual(game_rect.height, 444, delta=1)  # 666 / 1.5

        # Status window should be 20% of game board width
        self.assertEqual(status_rect.width, 133)  # 666 * 0.2 = 133.2 -> 133
        self.assertEqual(status_rect.height, game_rect.height)

        # Status should be adjacent to game board
        self.assertEqual(status_rect.left, game_rect.right)
        self.assertEqual(status_rect.top, game_rect.top)

        # Combined windows should fit in display
        self.assertLessEqual(game_rect.width + status_rect.width, 800)

    def test_custom_board_size_square(self):
        """Test with custom board size (1:1 square)"""
        play_screen = self.create_play_screen(
            800, 600, board_size=(10, 10), status_width_percent=10
        )
        game_rect, status_rect, _ = play_screen._calculate_window_rects(800, 600)

        # Board should be square
        self.assertEqual(game_rect.width, game_rect.height)

        # Status should be 10% of game board width
        self.assertEqual(status_rect.width, int(game_rect.width * 0.1))

    def test_custom_board_size_wide(self):
        """Test with custom board size (2:1 very wide)"""
        play_screen = self.create_play_screen(
            800, 400, board_size=(20, 10), status_width_percent=15
        )
        game_rect, status_rect, _ = play_screen._calculate_window_rects(800, 400)

        # Board aspect ratio should be preserved
        actual_ratio = game_rect.width / game_rect.height
        expected_ratio = 20 / 10  # 2.0
        self.assertAlmostEqual(actual_ratio, expected_ratio, places=1)

        # Status should be 15% of game board width
        self.assertEqual(status_rect.width, int(game_rect.width * 0.15))

    def test_custom_status_width_percent(self):
        """Test with different status width percentages"""
        test_cases = [5, 10, 20, 30, 50]

        for status_percent in test_cases:
            with self.subTest(status_width_percent=status_percent):
                play_screen = self.create_play_screen(
                    800, 600, status_width_percent=status_percent
                )
                game_rect, status_rect, _ = play_screen._calculate_window_rects(
                    800, 600
                )

                # Status width should be correct percentage
                expected_status_width = int(game_rect.width * status_percent / 100)
                self.assertEqual(status_rect.width, expected_status_width)

    def test_minimum_display_size_custom_config(self):
        """Test minimum display size with custom config"""
        # Custom config: (5:3, 25%)
        play_screen = self.create_play_screen(
            400, 240, board_size=(5, 3), status_width_percent=25
        )
        game_rect, status_rect, background_rects = play_screen._calculate_window_rects(
            400, 240
        )

        # Check aspect ratio
        actual_ratio = game_rect.width / game_rect.height
        expected_ratio = 5 / 3
        self.assertAlmostEqual(actual_ratio, expected_ratio, places=1)

        # Status should be 25% of game board width
        self.assertEqual(status_rect.width, int(game_rect.width * 0.25))
        self.assertEqual(status_rect.height, game_rect.height)

    def test_generic_aspect_ratio_preservation(self):
        """Test that game board aspect ratio is always preserved"""
        test_cases = [
            # (display_size, board_size, status_percent)
            ((1920, 1080), (15, 10), 20),
            ((800, 600), (15, 10), 20),
            ((800, 600), (10, 10), 10),
            ((800, 400), (20, 10), 15),
            ((600, 400), (5, 4), 25),
            ((1024, 768), (4, 3), 30),
        ]

        for (display_w, display_h), (board_w, board_h), status_pct in test_cases:
            with self.subTest(
                display=(display_w, display_h),
                board_size=(board_w, board_h),
                status_percent=status_pct,
            ):
                play_screen = self.create_play_screen(
                    display_w,
                    display_h,
                    board_size=(board_w, board_h),
                    status_width_percent=status_pct,
                )
                game_rect, _, _ = play_screen._calculate_window_rects(
                    display_w, display_h
                )

                # Calculate actual aspect ratio
                actual_ratio = game_rect.width / game_rect.height
                expected_ratio = board_w / board_h

                # Allow small floating point differences
                self.assertAlmostEqual(actual_ratio, expected_ratio, places=1)

    def test_generic_status_width_percentage(self):
        """Test status width percentage with various configs"""
        test_cases = [
            ((800, 600), (15, 10), 5),
            ((800, 600), (15, 10), 20),
            ((800, 600), (15, 10), 50),
            ((1920, 1080), (10, 10), 10),
            ((600, 400), (5, 3), 25),
        ]

        for (display_w, display_h), (board_w, board_h), status_pct in test_cases:
            with self.subTest(
                display=(display_w, display_h),
                board_size=(board_w, board_h),
                status_percent=status_pct,
            ):
                play_screen = self.create_play_screen(
                    display_w,
                    display_h,
                    board_size=(board_w, board_h),
                    status_width_percent=status_pct,
                )
                game_rect, status_rect, _ = play_screen._calculate_window_rects(
                    display_w, display_h
                )

                # Status width should be correct percentage
                expected_status_width = int(game_rect.width * status_pct / 100)
                self.assertEqual(status_rect.width, expected_status_width)

    def test_generic_no_window_overlap(self):
        """Test that game board and status never overlap"""
        test_cases = [
            ((1920, 1080), (15, 10), 20),
            ((800, 600), (15, 10), 20),
            ((600, 400), (10, 10), 10),
            ((800, 400), (20, 10), 15),
            ((600, 400), (5, 3), 25),
        ]

        for (display_w, display_h), (board_w, board_h), status_pct in test_cases:
            with self.subTest(
                display=(display_w, display_h),
                board_size=(board_w, board_h),
                status_percent=status_pct,
            ):
                play_screen = self.create_play_screen(
                    display_w,
                    display_h,
                    board_size=(board_w, board_h),
                    status_width_percent=status_pct,
                )
                game_rect, status_rect, _ = play_screen._calculate_window_rects(
                    display_w, display_h
                )

                # Game board right edge should equal status left edge
                self.assertEqual(game_rect.right, status_rect.left)

                # Windows should not overlap
                self.assertFalse(game_rect.colliderect(status_rect))

    def test_generic_background_coverage(self):
        """Test that background rectangles cover all remaining area"""
        test_cases = [
            ((1920, 1080), (15, 10), 20),
            ((800, 600), (15, 10), 20),
            ((600, 400), (10, 10), 10),
            ((800, 400), (20, 10), 15),
            ((600, 400), (5, 3), 25),
        ]

        for (display_w, display_h), (board_w, board_h), status_pct in test_cases:
            with self.subTest(
                display=(display_w, display_h),
                board_size=(board_w, board_h),
                status_percent=status_pct,
            ):
                play_screen = self.create_play_screen(
                    display_w,
                    display_h,
                    board_size=(board_w, board_h),
                    status_width_percent=status_pct,
                )
                game_rect, status_rect, background_rects = (
                    play_screen._calculate_window_rects(display_w, display_h)
                )

                # Calculate total covered area
                game_area = game_rect.width * game_rect.height
                status_area = status_rect.width * status_rect.height
                background_area = sum(
                    rect.width * rect.height for rect in background_rects
                )

                total_covered = game_area + status_area + background_area
                total_display = display_w * display_h

                # All area should be covered
                self.assertEqual(total_covered, total_display)


if __name__ == "__main__":
    unittest.main()
