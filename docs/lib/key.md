# Key and subclasses

Developer documentation for `displaypad_lib.key` base class, specialized key subclasses, and interaction lifecycle hooks.

## Core `Key` contract
- Inherit from `Key` and implement `render(ctx: KeyContext)`.
- Lifecycle hooks (optional):
  - `on_mount(index)`: Called when assigned to a board slot (0–11).
  - `on_press()`: Called when the button is pressed down.
  - `on_release()`: Called when the button is released.
  - `on_double_press()`: Called on double-tap within double-click window (`0.6s`).
  - `on_long_press()`: Called when held down longer than `0.8s`.
  - `on_tick()`: Called every loop iteration for animations and timers.
- Call `request_redraw()` whenever your state changes; `DisplayPad.update` will repaint and queue tile uploads.

## Included Subclasses
- `GifKey(path_or_img, rotation=0)`: Plays animated GIFs at native frame rates with rotation support.
- `IconKey(image_or_path, margin=10)`: Draws static images (PIL Image or file path) with automatic scaling and centering.
- `LabelKey(label, bg_color="navy", text_color="white", font_size=18)`: Displays centered text labels with customizable background/text colors and font size (default 18pt).
- `FramerateLimitedKey(fps=10)`: Rate-limits redraw requests via `on_tick`.
- `LoggerKey(idx)`: Diagnostic key logging presses and releases.


