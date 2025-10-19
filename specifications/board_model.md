Technical Specification for BoardModel Class
1. General Requirements
Full unit test coverage (100%).
Unit tests must be in a separate file.
Type checking with Mypy.
Full type annotations for all necessary types.
2. Class Constructor BoardModel
Constructor Parameters:
size: Tuple[int, int] — size of the board in large cells (sx, sy).
cell_size: int — size of the cell in steps (P), must be an odd number.
data: List[str] — list of strings representing cell contents.
Checks:
cell_size must be an odd number. If cell_size is an even number, raise a ValueError.
3. Board Structure
The board is a rectangle of sx * sy large cells (LC).

Each large cell contains one of the following static objects:

Gold bag (G)
Ruby (*)
Rock (#)
Empty space (space)
The center of each large cell is connected to the centers of neighboring cells horizontally and vertically by a road of P steps — a chain of P-1 small cells (SC).

Each small cell can be filled with rock or be empty.

4. Object Coordinates
Static Objects:
Coordinates of static objects on the board are tuples (bx, by) ranging from (0, 0) to (sx-1, sy-1).
These objects are always located in large cells.

Dynamic Objects:
Dynamic objects have absolute coordinates consisting of two tuples:

Coordinates of the large cell (bx, by).
Local coordinates of the small cell (mx, my) within it.
Coordinates are passed as a tuple of tuples: ((bx, by), (mx, my)).

Only one coordinate in the pair (mx, my) can be non-zero.
If bx = 0, then mx < 0 is prohibited.
If by = 0, then my < 0 is prohibited.
If bx = size_x - 1, then mx > 0 is prohibited.
If by = size_y - 1, then my > 0 is prohibited.
Both mx and my cannot be non-zero simultaneously.
5. Storage Structure for Small Cells
The storage structure for small cells in each large cell includes five cells:

Center.
All small cells above the center have the same content.
All small cells below the center have the same content.
All small cells to the left of the center have the same content.
All small cells to the right of the center have the same content.
6. Methods of BoardModel Class
Check if SC is the center of LC:
Method checks if the given small cell is the center of the large cell.
Returns True if it is, otherwise False.
Make one step from the given SC in the specified direction:
Method accepts the current coordinates of the small cell and direction (u, l, r, b).
Returns new coordinates of the small cell if the step is possible.
If the step is not possible due to the edge of the field or perpendicularity to the road, returns None.
This method does not consider cell occupancy, it is purely a geometric step.
From any SC that is not the center of LC, you can only move towards the center or away from it.
If bx = 0, then mx < 0 is prohibited.
If by = 0, then my < 0 is prohibited.
If bx = size_x - 1, then mx > 0 is prohibited.
If by = size_y - 1, then my > 0 is prohibited.
Both mx and my cannot be non-zero simultaneously.
After all checks, if mx or my exceeds (P-1)//2, transition to the neighboring LC.
Get the content of the cell at the given SC coordinates:
Method accepts the absolute coordinates of the small cell.
Returns the content of the cell.
Set the required content in the cell at the given SC coordinates:
Method accepts the absolute coordinates of the small cell and the content.
Sets the content in the cell.
Convert LC coordinates to SC center coordinates:
Method accepts the coordinates of the large cell.
Returns the absolute coordinates of the central small cell of this large cell.
Convert any SC coordinates to LC coordinates in which it is located:
Method accepts the absolute coordinates of the small cell.
Returns the coordinates of the large cell in which it is located.
7. Static Constants for Main Types of Content
Constants:
EMPTY = 0
GOLD = 1
RUBY = 2
ROCK = 3
8. Unit Tests
Tests for checking correct class initialization.
Tests for checking exceptions for incorrect parameters.
Tests for checking methods for working with small cells.
Tests for checking reading and writing cell content.
Tests for checking coordinate conversion.
Tests for checking invalid SC coordinates.
Tests for checking movement from the center of edge LCs towards the nearest edge.
9. Type Checking
Full type annotations for all parameters and methods.
Type checking with Mypy.
Example Data Structure for Cell Contents
The list of strings data forms a rectangular array of letters of size (3*sx, 3*sy).

Each large cell corresponds to a 3*3 square of symbols.

The central element of such a square is the content of the central small cell of this large cell:

G — gold
* — ruby
Space — empty
# — rock
All small cells, except the central one, are initially filled depending on the central cell:

Empty if the central cell is empty.
Rock if the central cell has any other content.
Four small cells, the most distant from the center, are filled based on the four cells on different sides of the square:

Either rock (if #), or empty (if space).
The storage structure for small cells in each large cell includes only five cells:

Center.
All small cells above it.
All small cells below it.
All small cells to the left.
All small cells to the right.
