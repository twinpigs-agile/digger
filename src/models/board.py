from typing import Tuple, List, Dict, Optional


def sign(x: int) -> int:
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0


class BoardModel:
    EMPTY = 0
    GOLD = 1
    RUBY = 2
    ROCK = 3

    def __init__(self, size: Tuple[int, int], cell_size: int, data: List[str]) -> None:
        self.size = size  # Size of the board in large cells (sx, sy)
        self.cell_size = cell_size  # Size of the cell in steps (P)
        self.half_cell_size = (cell_size - 1) // 2  # Precomputed half cell size
        self.data = data  # List of strings representing cell contents

        # Check that cell_size is an odd number
        if cell_size % 2 == 0:
            raise ValueError("Cell size must be an odd number.")

        # Initialize the field
        self.field = self._initialize_field()

    def _initialize_field(self) -> List[List[Dict[Tuple[int, int], int]]]:
        # Method to initialize the field
        field = []
        for i in range(self.size[0]):
            row = []
            for j in range(self.size[1]):
                cell_map = self._get_content_from_data(i, j)
                row.append(cell_map)
            field.append(row)
        return field

    _decode_bc = {
        "G": GOLD,
        "#": ROCK,
        "*": RUBY,
        " ": EMPTY,
    }
    _decode_sc = {
        "#": ROCK,
        " ": EMPTY,
    }

    def _get_content_from_data(self, bx: int, by: int) -> Dict[Tuple[int, int], int]:
        # Method to get content from data
        return {
            (0, 0): self._decode_bc[self.data[3 * by + 1][4 * bx + 1]],
            (0, 1): self._decode_sc[self.data[3 * by + 2][4 * bx + 1]],
            (0, -1): self._decode_sc[self.data[3 * by][4 * bx + 1]],
            (1, 0): self._decode_sc[self.data[3 * by + 1][4 * bx + 2]],
            (-1, 0): self._decode_sc[self.data[3 * by + 1][4 * bx]],
        }

    def is_center(self, coords: Tuple[Tuple[int, int], Tuple[int, int]]) -> bool:
        # Check if SC is the center of LC
        (bx, by), (mx, my) = coords
        return mx == 0 and my == 0

    def step(
        self, coords: Tuple[Tuple[int, int], Tuple[int, int]], direction: str
    ) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        # Make one step from the given SC in the specified direction
        (bx, by), (mx, my) = coords
        new_coords = None

        if direction == "u":
            new_coords = (bx, by), (mx, my - 1)
        elif direction == "l":
            new_coords = (bx, by), (mx - 1, my)
        elif direction == "r":
            new_coords = (bx, by), (mx + 1, my)
        elif direction == "d":
            new_coords = (bx, by), (mx, my + 1)

        if new_coords:
            (new_bx, new_by), (new_mx, new_my) = new_coords
            if (
                (new_bx == 0 and new_mx < 0)
                or (new_by == 0 and new_my < 0)
                or (new_bx == self.size[0] - 1 and new_mx > 0)
                or (new_by == self.size[1] - 1 and new_my > 0)
            ):
                return None
            if new_mx != 0 and new_my != 0:
                return None
            if new_mx < -self.half_cell_size:
                new_bx -= 1
                new_mx = self.half_cell_size
            elif new_mx > self.half_cell_size:
                new_bx += 1
                new_mx = -self.half_cell_size
            if new_my < -self.half_cell_size:
                new_by -= 1
                new_my = self.half_cell_size
            elif new_my > self.half_cell_size:
                new_by += 1
                new_my = -self.half_cell_size
            return (new_bx, new_by), (new_mx, new_my)
        return None

    def get_cell_content(self, coords: Tuple[Tuple[int, int], Tuple[int, int]]) -> int:
        # Get the content of the cell at the given SC coordinates
        (bx, by), (mx, my) = coords
        return self.field[bx][by].get((sign(mx), sign(my)), self.EMPTY)

    def set_cell_content(
        self, coords: Tuple[Tuple[int, int], Tuple[int, int]], content: int
    ) -> None:
        # Set the required content in the cell at the given SC coordinates
        (bx, by), (mx, my) = coords
        self.field[bx][by][(sign(mx), sign(my))] = content

    def lc_to_sc_center(
        self, lc_coords: Tuple[int, int]
    ) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        # Convert LC coordinates to SC center coordinates
        bx, by = lc_coords
        return (bx, by), (0, 0)

    def sc_to_lc(
        self, sc_coords: Tuple[Tuple[int, int], Tuple[int, int]]
    ) -> Tuple[int, int]:
        # Convert any SC coordinates to LC coordinates in which it is located
        (bx, by), (mx, my) = sc_coords
        return bx, by

    def __repr__(self) -> str:
        cr = "\n    "
        return f"BoardModel(size={self.size}, cell_size={self.cell_size}, data=[\n    {cr.join(self.data)}\n])"
