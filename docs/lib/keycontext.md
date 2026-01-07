# KeyContext

`displaypad_lib.keycontext.KeyContext` is the drawing helper for a single key. It wraps a shared `ImageDraw` instance and a base image, automatically offsetting all commands into the key's rectangle.

## Dimensions and offsets
- Default per-key size: `width = 800 // 6`, `height = 240 // 2` (derived from the 2x6 grid).
- `ox` / `oy` are the top-left offsets for the current key; all drawing methods add these automatically.

## Drawing helpers
- `text(x, y, text, color="white", font=None)`: draw text at local coordinates.
- `rectangle(x, y, w, h, color="red")`, `ellipse(...)`, `line(x1, y1, x2, y2, color="red", width=1)`: primitives with automatic offset.
- `center_text(text, color="white", font=None)`: centers within the key bounds using `textbbox` for proper sizing.
- `fill(color="black")` / `clear()`: fill the whole key area (clear is an alias for fill black).
- `paste_image(pil_image, x=0, y=0)`: pastes with clipping to the key bounds; requires `KeyContext` to have a backing image.
- `set_font(font)`: change the default font.

## Using `paste_image`
```python
from displaypad_lib.keycontext import KeyContext
from PIL import Image

# ctx is provided inside Key.render
logo = Image.open("examples/assets/heart.png")
ctx.paste_image(logo, x=4, y=4)  # clipped to the key region
```

## Good practices
- Treat coordinates as local: `(0, 0)` is the top-left of the key, not the whole panel.
- Keep a single `ImageFont` instance if you draw text frequently; loading fonts per frame is expensive.
- When centering text or icons, use `center_text` or compute with `ctx.width`/`ctx.height` instead of hard-coding pixel values.
- Avoid mutating the base image outside of `KeyContext` methods; `DisplayPad` uses a shared buffer for all keys.

## Example references
- `examples/clock.py`: uses `center_text` with a custom font for time/date tiles.
- `examples/lib_example.py`: draws rectangles, text, lines, and uses `IconKey` which relies on `paste_image` clipping.
