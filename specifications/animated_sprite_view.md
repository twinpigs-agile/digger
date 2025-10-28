# AnimatedSpriteView

## Overview

`AnimatedSpriteView` is a concrete implementation of the `View` base class that handles rendering animated sprites. It combines the `AnimatedSprite` (sprite assets and animation data) with the `Animation` (runtime state) to provide a window-aware rendering component.

## Purpose

- **Visual Representation**: Renders animated game objects within a window
- **Animation Management**: Handles sprite animation frame advancement
- **Coordinate Handling**: Converts between local window coordinates and screen coordinates
- **Window Integration**: Automatically draws to the parent window's display surface

## Class Structure

### AnimatedSpriteView

```python
class AnimatedSpriteView(View):
    view_type = "animated_sprite"
    
    def __init__(self, animated_sprite: AnimatedSprite) -> None:
        """Initialize with an AnimatedSprite."""
    
    def tick(self) -> None:
        """Update animation and draw to window."""
    
    def set_position(self, position: Tuple[int, int]) -> None:
        """Set sprite position in window-local coordinates."""
    
    def get_position(self) -> Tuple[int, int]:
        """Get current sprite position."""
    
    def set_animation(self, animation_name: str) -> None:
        """Start named animation sequence."""
    
    def set_variation(self, variation: str) -> None:
        """Set sprite variation (e.g., 'idle', 'walk')."""
    
    def set_direction(self, direction: str) -> None:
        """Set sprite direction (e.g., 'r', 'l', 'u', 'd')."""
    
    def get_animation(self) -> Animation:
        """Get the animation object for advanced control."""
```

For frame-level control methods on Animation, see [animated_sprites.md](animated_sprites.md).

## Usage Example

### Basic Setup

```python
from animations.animated import AnimatedSprite
from animations.common_views import AnimatedSpriteView
from mainloop.screens import Window

# Load sprite assets
sprite = AnimatedSprite("path/to/sprite", (64, 64))

# Create view
sprite_view = AnimatedSpriteView(sprite)

# Set position within window
sprite_view.set_position((100, 50))

# Add to window (will handle tick calls and rendering)
window.add_view(priority=0, view=sprite_view)
```

### Controlling Animation

```python
# Change animation sequence
sprite_view.set_animation("walk")

# Change sprite variation
sprite_view.set_variation("heavy")

# Change direction
sprite_view.set_direction("u")  # up

# Get animation object for frame control
animation = sprite_view.get_animation()
# For frame-level control, see animated_sprites.md
```

### Multiple Sprites

```python
# Each view has independent animation
player_view = AnimatedSpriteView(player_sprite)
enemy_view = AnimatedSpriteView(enemy_sprite)

window.add_view(priority=5, view=player_view)
window.add_view(priority=10, view=enemy_view)

# Update independently
player_view.set_position((200, 300))
enemy_view.set_position((400, 300))
enemy_view.set_animation("attack")
```

## How It Works

### Initialization
1. **Receives** an `AnimatedSprite` (contains sprite sheets and animation metadata)
2. **Creates** an `Animation` instance for runtime state
3. **Stores** initial position at (0, 0)

### Tick (Update) Process
1. **Check** if view is associated with a window
   - If not associated, tick does nothing (graceful degradation)
2. **Convert** local position to screen coordinates using `window.to_screen_coords()`
3. **Draw** current animation frame at screen position
4. **Advance** animation frame for next tick

### Coordinate System

```
Window-Local Coordinates:        Screen Coordinates:
┌─────────────────────┐         ┌─────────────────────┐
│ (0,0)      (100,50) │         │ Window offset       │
│   ●────────────●    │    →    │ (200, 100)          │
│                     │         │   ●────────────●    │
│              Window │         │   (200,100)  (300,150)
└─────────────────────┘         └─────────────────────┘

Local Pos:     (100, 50)
Window Rect:   (200, 100, 600, 400)
Screen Pos:    (200 + 100, 100 + 50) = (300, 150)
```

## Design Features

### 1. **Independent Animation Per View**
Each view has its own `Animation` instance, so multiple sprites can:
- Show different frames
- Use different variations
- Face different directions
- All independently

### 2. **Window-Aware Rendering**
- Uses weak reference to parent window
- Automatically handles coordinate conversion
- Gracefully handles orphaned views (no crash if window deleted)

### 3. **Separation of Concerns**
- **AnimatedSprite**: Asset loading and transformation
- **Animation**: Runtime state (current frame, position)
- **AnimatedSpriteView**: Integration with window and rendering

### 4. **Frame Advancement**
Automatically advances animation on each tick:
```python
def tick(self):
    # Draw current frame
    self.animation.draw(window.env.display)
    # Move to next frame
    self.animation.next_frame()  # Wraps at animation end
```

For direct frame control methods, see [animated_sprites.md](animated_sprites.md).

## Integration with Window's Tick

When a window calls `tick()` on all its views in priority order:

```python
class GameWindow(Window):
    def tick(self, events):
        # Window updates (handle input, etc.)
        
        # Views update (animation frames advance, sprites draw)
        for priority, view in self._views:
            view.tick()
        
        # Display updates
        pygame.display.flip()
```

## Testing

Comprehensive tests cover:

1. **Initialization**: View creates animation correctly
2. **Position Management**: Setting and getting local coordinates
3. **Animation Control**: Changing variations, animations, directions
4. **Coordinate Conversion**: Local → screen coordinate transformation
5. **Frame Advancement**: Animation progresses on each tick
6. **Window Association**: Proper weak reference handling
7. **Graceful Degradation**: Tick without window doesn't crash
8. **Drawing**: Verify animation.draw() is called
9. **Independence**: Multiple views maintain separate state
10. **Optional Transform**: Sprites without transform section load correctly
11. **Shared References**: Images are reused when transform is absent
12. **Frame Control**: 
    - `get_animation_length()` returns correct count
    - `get_current_frame()` returns correct index
    - `set_current_frame()` sets frame with wrapping
    - Negative indices raise ValueError

See `tests/animations/test_common_views.py` for AnimatedSpriteView tests and
`tests/graph/animation/test_animation.py` for AnimatedSprite and Animation tests.

## Performance Considerations

### Sprite Sheet Loading
- Sprites are pre-loaded and scaled during `AnimatedSprite` creation
- Not done per-frame (efficient)
- When transform is absent, images are shared (same object reference)

### Animation Updates
- `next_frame()` only increments counter (O(1))
- `set_current_frame()` uses modulo for wrapping (O(1))
- `get_animation_length()` returns cached value (O(1))
- `draw()` performs simple `surface.blit()` operation

### Memory
- Each view holds reference to shared `AnimatedSprite`
- Each view has own `Animation` instance (lightweight)
- Weak reference to window prevents memory leaks
- Optional transform saves memory by sharing image objects

## Common Patterns

### Group Sprites by Priority Layer

```python
# Background characters (drawn first)
background_views = [
    AnimatedSpriteView(npc1_sprite),
    AnimatedSpriteView(npc2_sprite),
]
for view in background_views:
    window.add_view(priority=100, view=view)

# Main player (drawn on top)
player_view = AnimatedSpriteView(player_sprite)
window.add_view(priority=0, view=player_view)
```

### Update Multiple Sprites

```python
# Game loop or screen's tick()
for view in sprite_views:
    # Update position based on game logic
    view.set_position(entity.get_position())
    
    # Update animation based on entity state
    if entity.is_moving:
        view.set_animation("walk")
    else:
        view.set_animation("idle")
```

### Animation Sequence

```python
# Run animation sequence, detect when finished
sprite_view.set_animation("attack")
sprite_view.set_direction("d")  # down

# Later, check if animation completed
if sprite_view.get_animation().is_at_start():
    # Animation finished, transition to idle
    sprite_view.set_animation("idle")
```

### Frame-Based Control

```python
# Sync multiple sprites at same frame
master_animation = master_view.get_animation()
current_frame = master_animation.get_current_frame()

for slave_view in slave_views:
    slave_animation = slave_view.get_animation()
    slave_animation.set_current_frame(current_frame)
    # All slaves now synchronized with master

# Rewind to beginning
animation.set_current_frame(0)

# Jump to halfway through animation
animation.set_current_frame(animation.get_animation_length() // 2)
```

## Future Extensions

Possible enhancements:
- **Callback Events**: Execute code when animation finishes
- **Animation Blending**: Smooth transitions between animations
- **Sprite Pooling**: Reuse view instances
- **Batch Rendering**: Optimize rendering multiple sprites
- **Physics Integration**: Velocity-based positioning
- **Frame Events**: Trigger actions at specific frames
