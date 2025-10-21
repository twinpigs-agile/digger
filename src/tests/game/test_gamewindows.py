import unittest
from unittest.mock import Mock
from game.playscreen import PlayScreen
from mainloop.environment import Environment


class TestGameWindows(unittest.TestCase):
    """Test cases for game window rectangle calculations"""

    def setUp(self):
        """Set up test environment"""
        # Mock pygame display
        self.mock_display = Mock()
        self.mock_display.get_size.return_value = (1920, 1080)

        # Mock environment
        self.env = Mock(spec=Environment)
        self.env.display = self.mock_display
        self.env.clock = Mock()

    def test_wide_display_calculation(self):
        """Test window calculation for wide display (1920x1080)"""
        self.mock_display.get_size.return_value = (1920, 1080)

        play_screen = PlayScreen(self.env, interval=60)
        game_rect, status_rect, background_rects = play_screen._calculate_window_rects(
            1920, 1080
        )

        # Game board should use full height
        self.assertEqual(game_rect.height, 1080)
        self.assertEqual(game_rect.width, 720)  # 1080 * (10/15) = 720

        # Status window should be 10% of game board width
        self.assertEqual(status_rect.width, 72)  # 720 * 0.1 = 72
        self.assertEqual(status_rect.height, 1080)

        # Status should be adjacent to game board
        self.assertEqual(status_rect.left, game_rect.right)
        self.assertEqual(status_rect.top, game_rect.top)

        # Combined windows should be centered
        # total_width = 720 + 72  # 792
        expected_left = (1920 - 792) // 2  # 564
        self.assertEqual(game_rect.left, expected_left)
        self.assertEqual(game_rect.top, 0)  # Full height, so top = 0

        # Should have background rectangles on left and right
        self.assertEqual(len(background_rects), 2)

        # Left background rectangle
        left_rect = background_rects[0]
        self.assertEqual(left_rect.left, 0)
        self.assertEqual(left_rect.width, expected_left)
        self.assertEqual(left_rect.height, 1080)

        # Right background rectangle
        right_rect = background_rects[1]
        self.assertEqual(right_rect.left, expected_left + 792)
        self.assertEqual(right_rect.width, 1920 - (expected_left + 792))
        self.assertEqual(right_rect.height, 1080)

    def test_narrow_display_calculation(self):
        """Test window calculation for narrow display (800x600)"""
        self.mock_display.get_size.return_value = (800, 600)

        play_screen = PlayScreen(self.env, interval=60)
        game_rect, status_rect, background_rects = play_screen._calculate_window_rects(
            800, 600
        )

        # Game board should use full height
        self.assertEqual(game_rect.height, 600)
        self.assertEqual(game_rect.width, 400)  # 600 * (10/15) = 400

        # Status window should be 10% of game board width
        self.assertEqual(status_rect.width, 40)  # 400 * 0.1 = 40
        self.assertEqual(status_rect.height, 600)

        # Status should be adjacent to game board
        self.assertEqual(status_rect.left, game_rect.right)
        self.assertEqual(status_rect.top, game_rect.top)

        # Combined windows should be centered
        # total_width = 400 + 40  # 440
        expected_left = (800 - 440) // 2  # 180
        self.assertEqual(game_rect.left, expected_left)
        self.assertEqual(game_rect.top, 0)  # Full height, so top = 0

        # Should have background rectangles on left and right
        self.assertEqual(len(background_rects), 2)

        # Left background rectangle
        left_rect = background_rects[0]
        self.assertEqual(left_rect.left, 0)
        self.assertEqual(left_rect.width, expected_left)
        self.assertEqual(left_rect.height, 600)

        # Right background rectangle
        right_rect = background_rects[1]
        self.assertEqual(right_rect.left, expected_left + 440)
        self.assertEqual(right_rect.width, 800 - (expected_left + 440))
        self.assertEqual(right_rect.height, 600)

    def test_very_narrow_display_calculation(self):
        """Test window calculation for very narrow display (600x400)"""
        self.mock_display.get_size.return_value = (600, 400)

        play_screen = PlayScreen(self.env, interval=60)
        game_rect, status_rect, background_rects = play_screen._calculate_window_rects(
            600, 400
        )

        # Game board should use full height
        self.assertEqual(game_rect.height, 400)
        self.assertEqual(game_rect.width, 266)  # 400 * (10/15) ≈ 266 (integer division)

        # Status window should be 10% of game board width
        self.assertEqual(status_rect.width, 26)  # 266 * 0.1 ≈ 26
        self.assertEqual(status_rect.height, 400)

        # Status should be adjacent to game board
        self.assertEqual(status_rect.left, game_rect.right)
        self.assertEqual(status_rect.top, game_rect.top)

        # Combined windows should be centered
        # total_width = 266 + 26  # 292
        expected_left = (600 - 292) // 2  # 154
        self.assertEqual(game_rect.left, expected_left)
        self.assertEqual(game_rect.top, 0)  # Full height, so top = 0

        # Should have background rectangles on left and right
        self.assertEqual(len(background_rects), 2)

        # Left background rectangle
        left_rect = background_rects[0]
        self.assertEqual(left_rect.left, 0)
        self.assertEqual(left_rect.width, expected_left)
        self.assertEqual(left_rect.height, 400)

        # Right background rectangle
        right_rect = background_rects[1]
        self.assertEqual(right_rect.left, expected_left + 292)
        self.assertEqual(right_rect.width, 600 - (expected_left + 292))
        self.assertEqual(right_rect.height, 400)

    def test_extremely_narrow_display(self):
        """Test window calculation for extremely narrow display (400x300)"""
        self.mock_display.get_size.return_value = (400, 300)

        play_screen = PlayScreen(self.env, interval=60)
        game_rect, status_rect, background_rects = play_screen._calculate_window_rects(
            400, 300
        )

        # Game board should use full height
        self.assertEqual(game_rect.height, 300)
        self.assertEqual(game_rect.width, 200)  # 300 * (10/15) = 200

        # Status window should be 10% of game board width
        self.assertEqual(status_rect.width, 20)  # 200 * 0.1 = 20
        self.assertEqual(status_rect.height, 300)

        # Status should be adjacent to game board
        self.assertEqual(status_rect.left, game_rect.right)
        self.assertEqual(status_rect.top, game_rect.top)

        # Combined windows should be centered
        # total_width = 200 + 20  # 220
        expected_left = (400 - 220) // 2  # 90
        self.assertEqual(game_rect.left, expected_left)
        self.assertEqual(game_rect.top, 0)  # Full height, so top = 0

        # Should have background rectangles on left and right
        self.assertEqual(len(background_rects), 2)

        # Left background rectangle
        left_rect = background_rects[0]
        self.assertEqual(left_rect.left, 0)
        self.assertEqual(left_rect.width, expected_left)
        self.assertEqual(left_rect.height, 300)

        # Right background rectangle
        right_rect = background_rects[1]
        self.assertEqual(right_rect.left, expected_left + 220)
        self.assertEqual(right_rect.width, 400 - (expected_left + 220))
        self.assertEqual(right_rect.height, 300)

    def test_square_display(self):
        """Test window calculation for square display (800x800)"""
        self.mock_display.get_size.return_value = (800, 800)

        play_screen = PlayScreen(self.env, interval=60)
        game_rect, status_rect, background_rects = play_screen._calculate_window_rects(
            800, 800
        )

        # Game board should use full height
        self.assertEqual(game_rect.height, 800)
        self.assertEqual(game_rect.width, 533)  # 800 * (10/15) ≈ 533

        # Status window should be 10% of game board width
        self.assertEqual(status_rect.width, 53)  # 533 * 0.1 ≈ 53
        self.assertEqual(status_rect.height, 800)

        # Status should be adjacent to game board
        self.assertEqual(status_rect.left, game_rect.right)
        self.assertEqual(status_rect.top, game_rect.top)

        # Combined windows should be centered
        # total_width = 533 + 53  # 586
        expected_left = (800 - 586) // 2  # 107
        self.assertEqual(game_rect.left, expected_left)
        self.assertEqual(game_rect.top, 0)  # Full height, so top = 0

        # Should have background rectangles on left and right
        self.assertEqual(len(background_rects), 2)

        # Left background rectangle
        left_rect = background_rects[0]
        self.assertEqual(left_rect.left, 0)
        self.assertEqual(left_rect.width, expected_left)
        self.assertEqual(left_rect.height, 800)

        # Right background rectangle
        right_rect = background_rects[1]
        self.assertEqual(right_rect.left, expected_left + 586)
        self.assertEqual(right_rect.width, 800 - (expected_left + 586))
        self.assertEqual(right_rect.height, 800)

    def test_tall_display(self):
        """Test window calculation for tall display (600x1200)"""
        self.mock_display.get_size.return_value = (600, 1200)

        play_screen = PlayScreen(self.env, interval=60)
        game_rect, status_rect, background_rects = play_screen._calculate_window_rects(
            600, 1200
        )

        # Width is limited by display width, so need to recalculate
        # Expected: game_width = 600 / (1 + 0.1) ≈ 545
        self.assertLessEqual(game_rect.width, 600)
        self.assertGreater(game_rect.width, 500)

        # Height should be recalculated based on width constraint
        # Expected: game_height = game_width / (10/15) = game_width * 1.5
        expected_height = int(game_rect.width * 1.5)
        self.assertEqual(game_rect.height, expected_height)

        # Status window should be 10% of game board width
        self.assertEqual(status_rect.width, int(game_rect.width * 0.1))
        self.assertEqual(status_rect.height, game_rect.height)

        # Status should be adjacent to game board
        self.assertEqual(status_rect.left, game_rect.right)
        self.assertEqual(status_rect.top, game_rect.top)

        # Combined windows should be centered
        total_width = game_rect.width + status_rect.width
        total_height = game_rect.height
        expected_left = (600 - total_width) // 2
        expected_top = (1200 - total_height) // 2
        self.assertEqual(game_rect.left, expected_left)
        self.assertEqual(game_rect.top, expected_top)

        # Should have background rectangles (could be 2-4 depending on layout)
        self.assertGreaterEqual(len(background_rects), 2)
        self.assertLessEqual(len(background_rects), 4)

        # Check that all background rectangles are positioned correctly
        for bg_rect in background_rects:
            # Background rectangles should not overlap with main windows
            self.assertFalse(game_rect.colliderect(bg_rect))
            self.assertFalse(status_rect.colliderect(bg_rect))

    def test_minimum_display_size(self):
        """Test window calculation for minimum viable display size"""
        # Minimum size where both windows can fit
        self.mock_display.get_size.return_value = (200, 150)

        play_screen = PlayScreen(self.env, interval=60)
        game_rect, status_rect, background_rects = play_screen._calculate_window_rects(
            200, 150
        )

        # Game board should use full height
        self.assertEqual(game_rect.height, 150)
        self.assertEqual(game_rect.width, 100)  # 150 * (10/15) = 100

        # Status window should be 10% of game board width
        self.assertEqual(status_rect.width, 10)  # 100 * 0.1 = 10
        self.assertEqual(status_rect.height, 150)

        # Status should be adjacent to game board
        self.assertEqual(status_rect.left, game_rect.right)
        self.assertEqual(status_rect.top, game_rect.top)

        # Combined windows should be centered
        total_width = 100 + 10  # 110
        expected_left = (200 - 110) // 2  # 45
        self.assertEqual(game_rect.left, expected_left)
        self.assertEqual(game_rect.top, 0)  # Full height, so top = 0

        # Should have background rectangles on left and right
        self.assertEqual(len(background_rects), 2)
        
        # Left background rectangle
        left_rect = background_rects[0]
        self.assertEqual(left_rect.left, 0)
        self.assertEqual(left_rect.width, expected_left)
        self.assertEqual(left_rect.height, 150)
        
        # Right background rectangle
        right_rect = background_rects[1]
        self.assertEqual(right_rect.left, expected_left + 110)
        self.assertEqual(right_rect.width, 200 - (expected_left + 110))
        self.assertEqual(right_rect.height, 150)

    def test_aspect_ratio_preservation(self):
        """Test that game board aspect ratio is preserved"""
        test_cases = [
            (1920, 1080),
            (800, 600),
            (600, 400),
            (400, 300),
            (800, 800),
            (600, 1200),
        ]

        for width, height in test_cases:
            with self.subTest(display=(width, height)):
                self.mock_display.get_size.return_value = (width, height)

                play_screen = PlayScreen(self.env, interval=60)
                game_rect, _, _ = play_screen._calculate_window_rects(width, height)

                # Calculate actual aspect ratio
                actual_ratio = game_rect.width / game_rect.height
                expected_ratio = 10 / 15  # BOARD_SIZE ratio

                # Allow small floating point differences
                self.assertAlmostEqual(actual_ratio, expected_ratio, places=2)

    def test_status_width_percentage(self):
        """Test that status window width is correct percentage of game board"""
        test_cases = [(1920, 1080), (800, 600), (600, 400), (400, 300)]

        for width, height in test_cases:
            with self.subTest(display=(width, height)):
                self.mock_display.get_size.return_value = (width, height)

                play_screen = PlayScreen(self.env, interval=60)
                game_rect, status_rect, _ = play_screen._calculate_window_rects(
                    width, height
                )

                # Status width should be 10% of game board width
                expected_status_width = int(game_rect.width * 0.1)
                self.assertEqual(status_rect.width, expected_status_width)

    def test_no_window_overlap(self):
        """Test that game board and status windows do not overlap"""
        test_cases = [
            (1920, 1080),
            (800, 600),
            (600, 400),
            (400, 300),
            (800, 800),
            (600, 1200),
        ]

        for width, height in test_cases:
            with self.subTest(display=(width, height)):
                self.mock_display.get_size.return_value = (width, height)

                play_screen = PlayScreen(self.env, interval=60)
                game_rect, status_rect, _ = play_screen._calculate_window_rects(
                    width, height
                )

                # Game board right edge should equal status left edge
                self.assertEqual(game_rect.right, status_rect.left)

                # Windows should not overlap
                self.assertFalse(game_rect.colliderect(status_rect))

    def test_background_coverage(self):
        """Test that background rectangles cover all remaining area"""
        test_cases = [(1920, 1080), (800, 600), (600, 400), (400, 300)]

        for width, height in test_cases:
            with self.subTest(display=(width, height)):
                self.mock_display.get_size.return_value = (width, height)

                play_screen = PlayScreen(self.env, interval=60)
                game_rect, status_rect, background_rects = (
                    play_screen._calculate_window_rects(width, height)
                )

                # Calculate total covered area
                game_area = game_rect.width * game_rect.height
                status_area = status_rect.width * status_rect.height
                background_area = sum(
                    rect.width * rect.height for rect in background_rects
                )

                total_covered = game_area + status_area + background_area
                total_display = width * height

                # All area should be covered
                self.assertEqual(total_covered, total_display)

    def test_window_positions(self):
        """Test that windows are positioned correctly"""
        self.mock_display.get_size.return_value = (800, 600)

        play_screen = PlayScreen(self.env, interval=60)
        game_rect, status_rect, background_rects = play_screen._calculate_window_rects(
            800, 600
        )

        # Combined windows should be centered
        total_width = game_rect.width + status_rect.width
        expected_left = (800 - total_width) // 2
        self.assertEqual(game_rect.left, expected_left)
        self.assertEqual(game_rect.top, 0)  # Full height, so top = 0

        # Status should be to the right of game board
        self.assertEqual(status_rect.left, game_rect.right)
        self.assertEqual(status_rect.top, game_rect.top)

        # Background rectangles should not overlap with main windows
        for bg_rect in background_rects:
            self.assertFalse(game_rect.colliderect(bg_rect))
            self.assertFalse(status_rect.colliderect(bg_rect))


if __name__ == "__main__":
    unittest.main()
