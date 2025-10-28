# View Architecture

## Overview

The `View` class is the base class for all visual representations of objects in the game. Views implement a **Model-View-Controller (MVC)** pattern where:

- **Model**: Represents game data and state
- **View**: Renders the visual representation (View class)
- **Controller**: Handles user input and updates the model

## View Class

### Purpose

A `View` represents the visual presentation of a game object. Views are lightweight rendering objects that:
- Know how to draw themselves
- Update their state via `tick()`
- Track which `Window` they belong to
- Have a type identifier for filtering/debugging

### Class Structure

```python
class View:
    view_type: str = "base"  # Subclasses override this
    
    def __init__(self):
        self._window: Optional[weakref.ref] = None  # Weak reference to parent window
    
    def tick(self) -> None:
        """Update view state. Must be implemented by subclasses."""
        raise NotImplementedError(...)
    
    def set_window(self, window: Optional[Window]) -> None:
        """Associate view with window using weak reference."""
    
    def get_window(self) -> Optional[Window]:
        """Get the window this view is associated with."""
```

### Key Features

#### 1. **Type Identifier**
Each View subclass defines a `view_type` class attribute:
```python
class PlayerView(View):
    view_type = "player"  # Identifies this as a player view
```

#### 2. **Weak References to Window**
Views use weak references (`weakref.ref`) to track their parent window:
- **Why weak references?** Prevents circular references and allows views to be garbage collected when the window is deleted
- Views automatically become orphaned when removed from a window
- Views return `None` if their window is garbage collected

```python
view = PlayerView()
window.add_view(priority=5, view=view)
assert view.get_window() is window

window.remove_view(view)
assert view.get_window() is None  # Weak reference cleared
```

#### 3. **Abstract Tick Method**
Views must implement `tick()` (no parameters) to update their state:
```python
class EnemyView(View):
    view_type = "enemy"
    
    def __init__(self):
        super().__init__()
        self.animation_frame = 0
    
    def tick(self):
        self.animation_frame = (self.animation_frame + 1) % 4
```

## Window and Views Integration

### Adding Views to Windows

Windows manage a prioritized list of Views. Views are rendered in priority order:
- **Priority 0**: Rendered last (on top / highest visibility)
- **Priority 1-N**: Rendered earlier (lower visibility)
- Multiple views can share the same priority (insertion order maintained)

```python
window = SomeWindow(env)

# Add background (low priority, rendered first)
bg_view = BackgroundView()
window.add_view(priority=10, view=bg_view)

# Add player (high priority, rendered on top)
player_view = PlayerView()
window.add_view(priority=0, view=player_view)

# Views are sorted by priority: [player_view, bg_view]
```

### View Lifecycle

1. **Creation**: `view = MyView()`
2. **Association**: `window.add_view(priority, view)` → `view.set_window(window)` called automatically
3. **Active**: `view.get_window()` returns the window
4. **Removal**: `window.remove_view(view)` → `view.set_window(None)` called automatically
5. **Orphaned**: `view.get_window()` returns None

### Example Window Implementation

```python
class GameWindow(Window):
    def __init__(self, env):
        super().__init__(env)
    
    def tick(self, events):
        # Update all views in priority order
        for priority, view in self._views:
            view.tick()
        
        # Render all views
        for priority, view in self._views:
            view.render(self.env.display)  # Subclasses implement render
```

## Use Cases

### 1. Game Objects
```python
class EntityView(View):
    view_type = "entity"
    
    def __init__(self, entity_model):
        super().__init__()
        self.model = entity_model  # Reference to model
    
    def tick(self):
        # Update animation based on model state
        if self.model.is_moving:
            self.update_animation()
```

### 2. UI Elements
```python
class HealthBarView(View):
    view_type = "ui_healthbar"
    
    def __init__(self, player_model):
        super().__init__()
        self.player = player_model
    
    def tick(self):
        # Update health display from model
        self.current_health = self.player.health
```

### 3. Layered Rendering
```python
# Background layer
background = BackgroundView()
window.add_view(priority=100, view=background)

# Tile layer
tiles = TileLayerView()
window.add_view(priority=50, view=tiles)

# Game objects
for entity in entities:
    view = EntityView(entity)
    window.add_view(priority=10, view=view)

# UI overlay
ui = UIView()
window.add_view(priority=0, view=ui)  # Rendered last (on top)
```

## Testing

Views are tested via:
1. **Unit tests**: Direct testing of `tick()` logic
2. **Integration tests**: Testing views within windows
3. **Priority ordering**: Verifying correct rendering order
4. **Weak reference handling**: Ensuring proper cleanup

See `tests/mainloop/test_mainloop.py` for comprehensive test coverage.

## Design Rationale

### Why Separate View from Window?

- **Separation of Concerns**: Windows manage layout/input, Views handle rendering
- **Reusability**: Same view can theoretically be added to different windows
- **Composability**: Complex UIs built from simple view components
- **Testing**: Views can be tested independently of window logic

### Why Weak References?

- **Memory Safety**: Prevents circular references (View → Window → View)
- **Automatic Cleanup**: Views are freed when windows are destroyed
- **Clear Ownership**: Window owns views, not vice versa
- **Flexibility**: Views can exist without a window (temporary)


