# DisplayPad (library)

Developer notes for `displaypad_lib.displaypad.DisplayPad`, the high-level manager for keys, rendering, and device updates.

## Getting Started
- Install the library (and driver) from the repo root: `pip install -e packages/library -e packages/driver`.
- Verify hardware access if needed (e.g., udev rules); see project README for platform notes.
- Create a minimal app:
  ```python
  from displaypad_lib import DisplayPad, Key

  class Hello(Key):
      def render(self, ctx):
          ctx.fill("black")
          ctx.center_text("Hello", color="white")

  pad = DisplayPad()
  pad[0] = Hello()

  try:
      while True:
          pad.update(100)
  except KeyboardInterrupt:
      pass
  finally:
      pad.disable()
  ```
- Look at `examples/clock.py` and `examples/lib_example.py` for richer patterns (fonts, graphs, icons).

## Responsibilities
- Owns the hardware driver (`displaypad_driver.DisplayPad`), the backing `800x240` RGB buffer, and the 12-key (2x6) grid state.
- Maps logical key indices to pixel regions and forwards input events to the mounted `Key` instances.
- Batches redraws so the device is only updated when at least one key marks itself dirty.

## Key APIs
- `pad = DisplayPad()`: constructs the driver, buffer, and empty key slots.
- `pad[index] = key`: mounts a `Key` at `index` (0-11), calls `key.on_mount(index)`, and flags it for redraw.
- `pad.update(timeout=500)`: single iteration of the loop.
  - Polls hardware input via `driver.poll_key(timeout)`.
  - Dispatches `on_press` / `on_release`.
  - Calls `on_tick` on each key, renders dirty keys into the shared buffer via `KeyContext`.
  - Pushes the composed image to the device (BGR order) if anything changed.
- `pad.disable()`: sends the disable command; call on exit.
- `pad.screenshot(path)`: saves the current buffer for debugging.

## Coordinate system
- Grid: 2 rows x 6 columns → 12 keys.
- Per-key size: `width = 800 // 6`, `height = 240 // 2`.
- `_get_key_coords(index)` returns the top-left corner for a key region; `KeyContext` handles offsets for drawing.

## Typical loop
```python
from displaypad_lib import DisplayPad
from my_keys import MyKey

pad = DisplayPad()
pad[0] = MyKey()

try:
    while True:
        pad.update(100)  # milliseconds
except KeyboardInterrupt:
    pass
finally:
    pad.disable()
```

## Best practices
- Always call `request_redraw()` from a key when its state changes; `update` only pushes frames when something is dirty.
- Keep per-frame work light inside `update` (avoid blocking I/O); long operations should be offloaded or throttled.
- Use `timeout` to tune responsiveness vs. CPU usage. Lower timeouts tick more frequently; higher saves CPU.
- For debugging visuals without hardware, render and call `pad.screenshot("/tmp/pad.png")`.

## Example references
- `examples/clock.py`: shows simple text keys with time/date rendering.
- `examples/lib_example.py`: demonstrates multiple custom keys, logging, and animated CPU graphing.
