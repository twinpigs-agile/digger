# Window Rectangle Calculation Specification

## Overview

This document specifies the algorithm for calculating window rectangles in the PlayScreen, including game board window, status window, and background coverage rectangles.

## Constants

- `BOARD_SIZE = (10, 15)` - Game board aspect ratio (width, height)
- `STATUS_WIDTH_PERCENT = 10` - Status window width as percentage of game board width

## Window Layout Rules

### 1. Game Board Window
- **Aspect Ratio**: Must maintain `BOARD_SIZE` ratio (10:15 = 2:3)
- **Position**: Top-left corner of the screen (0, 0)
- **Size Calculation**: Maximum possible size that fits within display constraints

### 2. Status Window
- **Width**: `STATUS_WIDTH_PERCENT` of game board width
- **Height**: Equal to game board height
- **Position**: Adjacent to game board (left edge of status = right edge of game board)
- **No Overlap**: Status window does not overlap with game board

### 3. Background Window
- **Coverage**: Entire display area
- **Priority**: Lowest (9)
- **Purpose**: Fills remaining areas not covered by game board and status windows

## Size Calculation Algorithm

### Step 1: Calculate Maximum Game Board Size
```
board_ratio = BOARD_SIZE[0] / BOARD_SIZE[1]  // 10/15 = 0.667
max_game_height = display_height
max_game_width = int(max_game_height * board_ratio)
```

### Step 2: Check Width Constraints
```
status_width = int(max_game_width * STATUS_WIDTH_PERCENT / 100)
total_width = max_game_width + status_width

if total_width > display_width:
    // Need to reduce sizes
    max_total_width = display_width
    max_game_width = int(max_total_width / (1 + STATUS_WIDTH_PERCENT / 100))
    max_game_height = int(max_game_width / board_ratio)
    status_width = int(max_game_width * STATUS_WIDTH_PERCENT / 100)
```

### Step 3: Define Window Rectangles
```
// Game board window
game_rect = pygame.Rect(0, 0, max_game_width, max_game_height)

// Status window
status_rect = pygame.Rect(max_game_width, 0, status_width, max_game_height)
```

## Background Rectangle Calculation

### Algorithm
The algorithm calculates minimum number of rectangles to cover remaining screen area:

1. **Right Area**: If there's space to the right of both windows
   ```
   right_x = max(game_rect.right, status_rect.right)
   if right_x < display_width:
       right_rect = pygame.Rect(right_x, 0, display_width - right_x, display_height)
   ```

2. **Bottom Area**: If there's space below both windows
   ```
   bottom_y = max(game_rect.bottom, status_rect.bottom)
   if bottom_y < display_height:
       bottom_width = min(game_rect.right, status_rect.right)
       bottom_rect = pygame.Rect(0, bottom_y, bottom_width, display_height - bottom_y)
   ```

### Coverage Guarantee
- All remaining screen area is covered by background rectangles
- No gaps or overlaps between background rectangles
- Minimum number of rectangles used for optimal performance

## Window Priorities

- **Background Window**: Priority 9 (lowest)
- **Game Board Window**: Priority 5 (medium)
- **Status Window**: Priority 3 (highest)

Lower numbers indicate higher priority in rendering order.

## Examples

### Example 1: Wide Display (1920x1080)
- Display: 1920x1080
- Board ratio: 2:3
- Max game height: 1080
- Max game width: 720
- Status width: 72
- Total width: 792 < 1920 ✓
- Result: Game (720x1080), Status (72x1080), Background (1128x1080 right area)

### Example 2: Narrow Display (800x600)
- Display: 800x600
- Board ratio: 2:3
- Max game height: 600
- Max game width: 400
- Status width: 40
- Total width: 440 < 800 ✓
- Result: Game (400x600), Status (40x600), Background (360x600 right area)

### Example 3: Very Narrow Display (600x400)
- Display: 600x400
- Board ratio: 2:3
- Max game height: 400
- Max game width: 267
- Status width: 27
- Total width: 294 < 600 ✓
- Result: Game (267x400), Status (27x400), Background (306x400 right area)

## Implementation Notes

### Coordinate System
- Origin (0,0) at top-left corner
- X increases to the right
- Y increases downward
- All rectangles use pygame.Rect format

### Edge Cases
- If display is too small to fit both windows, algorithm reduces sizes proportionally
- Status window width is always calculated as percentage of game board width
- Background rectangles are only created for areas not covered by main windows

### Performance Considerations
- Rectangle calculations are done once during initialization
- Background rectangles are pre-calculated and stored
- No runtime rectangle calculations during game loop

## Validation

The algorithm ensures:
1. Game board maintains correct aspect ratio
2. Status window width is correct percentage of game board
3. Windows do not overlap
4. All screen area is covered
5. Minimum number of background rectangles used
6. Windows fit within display boundaries
