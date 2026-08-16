# KeyContext

`displaypad_lib.keycontext.KeyContext` is the drawing helper for a single key. It wraps a shared `ImageDraw` instance and a base image, automatically offsetting all commands into the key's rectangle.

## Dimensions and Offsets
- Per-key size: `width` and `height` derived from exact fractional grid boundaries (`x1 = round(col * 800 / 6)`), eliminating column clipping across the 800×240 panel.
- `ox` / `oy` are the top-left offsets for the current key; all drawing methods add these automatically.

## Font Management
- `get_default_font(size=18)`: Automatically loads a crisp, bold system font (`DejaVuSans-Bold`, `FreeSansBold`, `LiberationSans-Bold`, or scaled PIL font) at 18pt by default for high readability.
- `set_font(font)`: Changes the active font for this context.

## Drawing Helpers
- `text(x, y, text, fill="white", font=None)`: Draw text at local coordinates. Accepts both `fill` and `color` parameter aliases.
- `rectangle(x, y, w, h, fill="red")`, `ellipse(...)`, `line(x1, y1, x2, y2, fill="red", width=1)`: Primitives with automatic offset and `color`/`fill` alias support.
- `center_text(text, y=None, fill="white", font=None)`: Centers text within key bounds using exact `textbbox` baseline offsets.
- `fill(fill="black")` / `clear()`: Fills the whole key area (clear is an alias for fill black).
- `paste_image(pil_image, x=0, y=0)`: Pastes an image with clipping to key bounds.

## Example Reference
```python
# Inside Key.render(ctx):
ctx.fill("navy")
ctx.center_text("MEDIA", color="white")
```

