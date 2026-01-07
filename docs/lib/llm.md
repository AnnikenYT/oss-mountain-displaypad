# LLM quick sheet

Purpose: teach a code agent how to use the DisplayPad library safely and correctly.

## Core pieces
- `DisplayPad` (in `displaypad_lib.displaypad`): owns driver, 800x240 RGB buffer, and 12 key slots (2 rows x 6 cols).
- `Key` (in `displaypad_lib.key`): abstract key behavior. Override `render(ctx)`; optionally `on_mount`, `on_press`, `on_release`, `on_tick`.
- `KeyContext` (in `displaypad_lib.keycontext`): drawing helper scoped to one key; exposes `width`, `height`, `fill`, `center_text`, `rectangle`, `ellipse`, `line`, `text`, `paste_image` (requires backing image).

## Main loop contract
```python
pad = DisplayPad()
pad[index] = key_instance  # 0-11; calls key.on_mount and marks dirty
while True:
    pad.update(timeout_ms)
```
- `pad.update`:
  - polls hardware: `driver.poll_key(timeout)` → dict of `pressed`, `released`, `held` indices
  - dispatches `on_press` / `on_release`
  - calls `on_tick` on each key
  - renders keys with `_needs_redraw` into shared buffer using `KeyContext`
  - if any key was dirty, pushes BGR image to device via `driver.set_panel_image`
- `pad.disable()` should be called on exit.

## Redraw semantics
- Keys must call `request_redraw()` when state changes. `_needs_redraw` is reset after render.
- `FramerateLimitedKey(fps)` helper triggers redraws on a cadence via `on_tick`.

## Coordinate system
- Per-key size: `KeyContext.width = 800 // 6`, `KeyContext.height = 240 // 2`.
- `KeyContext` offsets all drawing by its `(ox, oy)`; treat `(0,0)` as top-left of the key.

## Examples to follow
- `examples/clock.py`: simple text/time tiles using `request_redraw` when text changes.
- `examples/lib_example.py`: mix of logger, toggle, hold button, CPU graph (`FramerateLimitedKey`), and `IconKey` using `paste_image`.

## Safety/efficiency hints
- Keep `on_tick` lightweight; avoid blocking I/O in the update loop.
- Reuse fonts/images instead of loading each frame.
- Use `pad.screenshot(path)` to debug renders without hardware.
