import unittest
from models.board import BoardModel


class TestBoardModel(unittest.TestCase):
    def setUp(self):
        self.size = (5, 5)
        self.cell_size = 3
        self.data = [
            "### ### ### ### ###",
            "#G# # # # # # # # #",
            "### ### ### ### ###",
            "### # # ### ### ###",
            "# # # #   # # # # #",
            "### ### ### ### ###",
            "### ### ### ### ###",
            "# # #   # # # # # #",
            "### ### # # ### ###",
            "### ### ### ### ###",
            "# # # # # # # # # #",
            "### ### ### ### ###",
            "### ### ### ### ###",
            "# # # # # # # # # #",
            "### ### ### ### ###",
        ]
        self.board = BoardModel(self.size, self.cell_size, self.data)

    def test_initialization(self):
        self.assertEqual(self.board.size, self.size)
        self.assertEqual(self.board.cell_size, self.cell_size)
        self.assertEqual(self.board.data, self.data)
        repr(self.board)  # just to call it

    def test_invalid_cell_size(self):
        with self.assertRaises(ValueError):
            BoardModel(self.size, 4, self.data)

    def test_is_center(self):
        self.assertTrue(self.board.is_center(((0, 0), (0, 0))))
        self.assertFalse(self.board.is_center(((0, 0), (1, 1))))

    def test_cell_contents(self):
        # Check cell (1, 1)
        self.assertEqual(
            self.board.get_cell_content(((1, 1), (0, -1))), BoardModel.EMPTY
        )  # Up
        self.assertEqual(
            self.board.get_cell_content(((1, 1), (0, 1))), BoardModel.ROCK
        )  # Down
        self.assertEqual(
            self.board.get_cell_content(((1, 1), (-1, 0))), BoardModel.ROCK
        )  # Left
        self.assertEqual(
            self.board.get_cell_content(((1, 1), (1, 0))), BoardModel.ROCK
        )  # Right

        # Check cell (1, 2)
        self.assertEqual(
            self.board.get_cell_content(((1, 2), (0, -1))), BoardModel.ROCK
        )  # Up
        self.assertEqual(
            self.board.get_cell_content(((1, 2), (0, 1))), BoardModel.ROCK
        )  # Down
        self.assertEqual(
            self.board.get_cell_content(((1, 2), (-1, 0))), BoardModel.ROCK
        )  # Left
        self.assertEqual(
            self.board.get_cell_content(((1, 2), (1, 0))), BoardModel.EMPTY
        )  # Right

        # Check cell (2, 1)
        self.assertEqual(
            self.board.get_cell_content(((2, 1), (0, -1))), BoardModel.ROCK
        )  # Up
        self.assertEqual(
            self.board.get_cell_content(((2, 1), (0, 1))), BoardModel.ROCK
        )  # Down
        self.assertEqual(
            self.board.get_cell_content(((2, 1), (-1, 0))), BoardModel.EMPTY
        )  # Left
        self.assertEqual(
            self.board.get_cell_content(((2, 1), (1, 0))), BoardModel.ROCK
        )  # Right

        # Check cell (2, 2)
        self.assertEqual(
            self.board.get_cell_content(((2, 2), (0, -1))), BoardModel.ROCK
        )  # Up
        self.assertEqual(
            self.board.get_cell_content(((2, 2), (0, 1))), BoardModel.EMPTY
        )  # Down
        self.assertEqual(
            self.board.get_cell_content(((2, 2), (-1, 0))), BoardModel.ROCK
        )  # Left
        self.assertEqual(
            self.board.get_cell_content(((2, 2), (1, 0))), BoardModel.ROCK
        )  # Right

    def test_set_cell_content(self):
        self.board.set_cell_content(((0, 0), (0, 0)), BoardModel.RUBY)
        self.assertEqual(self.board.get_cell_content(((0, 0), (0, 0))), BoardModel.RUBY)

    def test_lc_to_sc_center(self):
        self.assertEqual(self.board.lc_to_sc_center((0, 0)), ((0, 0), (0, 0)))
        self.assertEqual(self.board.lc_to_sc_center((1, 1)), ((1, 1), (0, 0)))

    def test_sc_to_lc(self):
        self.assertEqual(self.board.sc_to_lc(((0, 0), (0, 0))), (0, 0))
        self.assertEqual(self.board.sc_to_lc(((1, 1), (0, 0))), (1, 1))

    def test_negative_coordinates(self):
        self.assertIsNone(self.board.step(((0, 0), (0, -1)), "u"))
        self.assertIsNone(self.board.step(((0, 0), (-1, 0)), "l"))
        self.assertEqual(self.board.step(((0, 0), (1, 0)), "r"), ((1, 0), (-1, 0)))
        self.assertEqual(self.board.step(((0, 0), (0, 1)), "d"), ((0, 1), (0, -1)))
        self.assertEqual(self.board.step(((1, 1), (-1, 0)), "l"), ((0, 1), (1, 0)))
        self.assertEqual(self.board.step(((1, 1), (0, -1)), "u"), ((1, 0), (0, 1)))

        self.assertIsNone(self.board.step(((1, 1), (0, 1)), "q"))

        self.assertEqual(
            self.board.get_cell_content(((0, 0), (-1, 0))), BoardModel.ROCK
        )
        self.assertEqual(
            self.board.get_cell_content(((0, 0), (0, -1))), BoardModel.ROCK
        )
        self.assertEqual(self.board.get_cell_content(((0, 0), (3, 0))), BoardModel.ROCK)
        self.assertEqual(self.board.get_cell_content(((0, 0), (0, 3))), BoardModel.ROCK)

    def test_invalid_sc_coordinates(self):
        self.assertIsNone(self.board.step(((1, 1), (0, 1)), "r"))
        self.assertIsNone(self.board.step(((1, 1), (0, 1)), "l"))
        self.assertIsNone(self.board.step(((1, 1), (1, 0)), "u"))
        self.assertIsNone(self.board.step(((1, 1), (1, 0)), "d"))

    def test_edge_lc_movement(self):
        self.assertIsNone(self.board.step(((0, 0), (0, 0)), "u"))
        self.assertIsNone(self.board.step(((0, 0), (0, 0)), "l"))
        self.assertIsNone(self.board.step(((4, 4), (0, 0)), "r"))
        self.assertIsNone(self.board.step(((4, 4), (0, 0)), "d"))


if __name__ == "__main__":
    unittest.main()
