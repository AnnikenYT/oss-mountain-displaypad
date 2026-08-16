# DisplayPad (library)

Developer notes for `displaypad_lib.displaypad.DisplayPad`, the high-level manager for keys, multi-page layouts, rendering, and device updates.

## Getting Started
- Install the library (and driver) from the repo root: `pip install -e packages/library -e packages/driver`.
- Create a minimal app:
  ```python
  from displaypad_lib import DisplayPad, Key, Page

  class Hello(Key):
      def render(self, ctx):
          ctx.fill("black")
          ctx.center_text("Hello", color="white")

  pad = DisplayPad()
  pad[0] = Hello()

  try:
      while True:
          pad.update(20)
  except KeyboardInterrupt:
      pass
  finally:
      pad.disable()
  ```

## Responsibilities & Architecture
- Owns the hardware driver (`displaypad_driver.DisplayPad`), backing `800x240` RGB buffer, and `PageManager` multi-page registry.
- Operates an asynchronous background render queue with frame deduplication so screen repaints do not block key event polling.
- Batches multi-key updates: single-key updates use fast per-button tile uploads; multi-key or page transitions execute a full-panel batch update (`push_image()`).
- Automatically renders solid black tiles for unassigned key slots (`None`), erasing previous background image remnants.

## Key APIs
- `pad = DisplayPad(rotation=0)`: Constructs driver, buffer, and `PageManager`.
- `pad[index] = key`: Mounts a `Key` at `index` (0-11) on the active page.
- `pad.add_page("Settings", page)`: Registers a new `Page` layout. If adding/updating the active page, repaints automatically. See [page.md](./page.md).
- `pad.switch_to_page("Settings")`: Switches active page and triggers full-panel repaint.
- `pad.push_image(image_or_path=None)`: Slices image buffer (or given image/file path) into 12 tile payloads and streams immediately to hardware.
- `pad.update(timeout=20)`: Single iteration of main loop.
  - Checks page auto-timeouts (`mode: "after" | "idle"`).
  - Polls hardware input via `driver.poll_key(timeout)`.
  - Dispatches `on_press`, `on_release`, `on_double_press`, `on_long_press` (with synthetic press guards for fast taps).
  - Ticks active page keys and queues dirty tile uploads.
- `pad.set_brightness(percent)`: Sets hardware backlight level (0–100%).
- `pad.clear()`: Resets buffer and unassigned slots to black.
- `pad.disable()`: Releases interfaces and closes worker threads.
- `pad.screenshot(path)`: Saves current buffer to disk.


## Acknowledgments
Performance optimizations and multi-page layout engine design inspired by [ramisotti13-eng/BaseCamp-Linux](https://github.com/ramisotti13-eng/BaseCamp-Linux).

