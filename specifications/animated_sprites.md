### Technical Specification (TS)

## Technical Requirements

1. All types must be statically annotated.
2. The code must be checked using Mypy to ensure type correctness.

## Classes

### AnimatedSprite

**Description**: A class that stores possible sprite states (all frames, all directions, all variations, all animation rules).

**Constructor Parameters**:
- `path` (str): Path to the directory where sprite files and the `animation.json` file are located.
- `size` (tuple or Sequence): Sprite dimensions.

**Methods**:
- `__init__(self, path: str, size: tuple)`: Constructor that initializes the object, reads the `animation.json` file, and loads images.
- `create_animation(self) -> 'Animation'`: Method to create and return an `Animation` object linked to the current `AnimatedSprite` object.

**Note**: No public methods are required other than creating the `Animation` object.

**Optional Features**:
- If `animation.json` does not contain a `"transform"` section, the same image is used for all four directions (r, l, u, d), and the same object reference is shared for memory efficiency.

### Animation

**Description**: A class that stores animation context and can manage animation.

**Constructor Parameters**:
- `animated_sprite` ('AnimatedSprite'): An `AnimatedSprite` object from which frames and animation settings are taken.

**Methods**:
- `__init__(self, animated_sprite: 'AnimatedSprite') -> None`: Constructor that initializes the object and links it to `AnimatedSprite`. If the animation is not explicitly chosen, the first available variation is used.
- `draw(self, surface: pygame.Surface) -> None`: Method to draw the current animation frame on the given surface.
- `set_variation(self, variation: str) -> None`: Method to set the sprite variation.
- `set_direction(self, direction: str) -> None`: Method to set the sprite direction.
- `start_animation(self, animation_name: str) -> None`: Method to start the animation from the beginning.
- `next_frame(self) -> None`: Method to advance to the next animation step.
- `is_at_start(self) -> bool`: Method to check if we are at the start of the animation sequence.
- `set_position(self, position: Tuple[int, int]) -> None`: Method to set the sprite position.

**New Methods** (Frame Control):
- `get_animation_length(self) -> int`: Get the number of frames in the current animation sequence.
- `get_current_frame(self) -> int`: Get the index of the current frame (0-based).
- `set_current_frame(self, frame_index: int) -> None`: Set the current frame. The frame index is automatically wrapped to the valid range [0, animation_length). Raises ValueError if frame_index is negative.

## Structure of `animation.json`

### With Transformations (Standard)

```json
{
  "directional": true,
  "transform": {
    "r": [],
    "l": ["mirror"],
    "u": ["rotate"],
    "d": ["rotate", "rotate", "rotate"]
  },
  "frame_count": 5,
  "variations": ["n"],
  "animations": {
    "default": [0, 1, 2, 3, 4, 3, 2, 1]
  },
  "anchors": [
    [256, 256],
    [256, 256],
    [256, 256],
    [256, 256],
    [256, 256],
    [256, 256],
    [256, 256],
    [256, 256]
  ]
}
```

### Without Transformations (Optional)

When the `"transform"` section is omitted, the same image is used for all directions:

```json
{
  "frame_count": 1,
  "variations": ["idle"],
  "animations": {
    "default": [0]
  },
  "anchors": [[0, 0]]
}
```

Benefits:
- Simpler configuration for sprites that don't need directional variations
- Memory efficient: same image object is shared for all directions (r, l, u, d)
- No transformation overhead

## Example Usage

### Basic Usage

```python
import pygame
from animations.animated import AnimatedSprite, Animation

# Initialize Pygame
pygame.init()

# Create AnimatedSprite object
sprite = AnimatedSprite(path="path/to/animations", size=(64, 64))

# Create Animation object via create_animation method
animation = sprite.create_animation()

# Set variation and start animation
animation.set_variation("n")
animation.set_direction("r")
animation.start_animation("default")

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Set sprite position
    animation.set_position((100, 100))

    # Update animation
    animation.next_frame()

    # Clear screen
    screen.fill((0, 0, 0))

    # Draw animation
    animation.draw(screen)
    
    # Update screen
    pygame.display.flip()

pygame.quit()
```

### Frame Control Usage

```python
import pygame
from animations.animated import AnimatedSprite

pygame.init()
sprite = AnimatedSprite(path="path/to/animations", size=(64, 64))
animation = sprite.create_animation()

# Get animation information
length = animation.get_animation_length()
current_frame = animation.get_current_frame()

# Jump to specific frame
animation.set_current_frame(3)

# Check if at last frame
if animation.get_current_frame() == length - 1:
    print("At last frame of animation")

# Frame wrapping (automatic)
animation.set_current_frame(length + 5)  # Wraps to frame 5
animation.set_current_frame(length * 10)  # Wraps to frame 0

# Synchronize multiple animations
master_animation = master_sprite.create_animation()
slave_animation = slave_sprite.create_animation()
slave_animation.set_current_frame(master_animation.get_current_frame())
```

## Next Steps

1. Clarify method implementation details.
2. Conduct testing and debugging using Mypy.

If there are additional requirements or changes, please specify.
