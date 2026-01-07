# Key and subclasses

Developer documentation for `displaypad_lib.key` base class and included utilities.

## Core `Key` contract
- Inherit from `Key` and implement `render(ctx: KeyContext)`.
- Lifecycle hooks (optional): `on_mount(index)`, `on_press()`, `on_release()`, `on_tick()`.
- Call `request_redraw()` whenever your state changes; `DisplayPad.update` will repaint and push when any key is dirty.
- Instance field `_needs_redraw` is managed by the base class; you normally do not touch it directly.

## Included helpers
- `FramerateLimitedKey(fps=10)`: triggers redraw at most `fps` times per second via `on_tick`; useful for clocks or lightweight animations.
- `LoggerKey(idx)`: logs presses/releases; simple diagnostic key.
- `IconKey(pil_image, margin=10)`: draws a static image with automatic resizing and centering inside the key bounds.

## Implementing a custom key
```python
import time
from displaypad_lib.key import Key

class HoldButton(Key):
    def __init__(self, idx):
        super().__init__()
        self.idx = idx
        self.start = None
        self.held = False

    def on_press(self):
        self.start = time.time()
        self.held = True
        self.request_redraw()

    def on_release(self):
        held_time = time.time() - self.start
        print(f"Key {self.idx} held {held_time:.2f}s")
        self.held = False
        self.request_redraw()

    def render(self, ctx):
        color = "orange" if self.held else "purple"
        ctx.rectangle(0, 0, ctx.width, ctx.height, color=color)
        label = "HOLDING" if self.held else "HOLD"
        ctx.center_text(f"{label} {self.idx}", color="white")
```

## Rendering guidelines
- Use the provided `KeyContext` for all drawing; it automatically offsets into your key region and provides clipping helpers.
- Keep drawing within `ctx.width`/`ctx.height`; anything outside is clipped, but painting within bounds avoids wasted work.
- Prefer integer coordinates to avoid blurry lines; PIL will anti-alias text for you.
- For frequent updates (graphs, clocks), subclass `FramerateLimitedKey` and do minimal work in `on_tick` to keep the loop responsive.

## Examples worth reading
- `examples/clock.py`: `DateKey` extends `Key` and uses `request_redraw` only when text changes.
- `examples/lib_example.py`: combines `LoggerKey`, `FramerateLimitedKey`, and custom keys like `HoldButton`, `MuteButton`, and an `IconKey`.
