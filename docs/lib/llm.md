# LLM Quick Sheet

Purpose: teach a code agent how to use the DisplayPad library safely, efficiently, and correctly.

## Core Architecture
- `DisplayPad` (in `displaypad_lib.displaypad`): manages hardware driver, multi-page layouts, 800x240 RGB buffer, and async render queue.
- `Page` & `PageManager` (in `displaypad_lib.page`): multi-page layout engine supporting navigation stacks and automatic inactivity/fixed-delay timeouts (`mode: "after" | "idle"`).
- `Key` (in `displaypad_lib.key`): abstract key class. Override `render(ctx)`; optional hooks: `on_mount`, `on_press`, `on_release`, `on_double_press`, `on_long_press`, `on_tick`.
- Key implementations: `GifKey`, `IconKey`, `LabelKey`, `FramerateLimitedKey`, `LoggerKey`.
- `KeyContext` (in `displaypad_lib.keycontext`): scoped key drawing context. Exposes `width`, `height`, `fill`, `center_text`, `rectangle`, `ellipse`, `line`, `polygon`, `arc`, `text`, `paste_image`, `clear`. Supports both `color` and `fill` parameter aliases.

## Main Loop Contract
```python
from displaypad_lib import DisplayPad, LoggerKey, Page

pad = DisplayPad(rotation=0)
pad[0] = LoggerKey(0)  # Assign to slot 0 on active page

# Multi-page setup
settings_page = Page(name="Settings", timeout_mode="idle", timeout_seconds=10, timeout_target="Main")
settings_page[0] = LoggerKey(1)
pad.add_page("Settings", settings_page)

try:
    while True:
        pad.update(20)  # Poll hardware and tick keys
except KeyboardInterrupt:
    pass
finally:
    pad.push_image("examples/assets/initial_screen.png")  # Restore splash screen on exit
    pad.disable()

```

## Event Dispatch & Redraw Semantics
- `on_press()` fires on every physical button down transition.
- `on_double_press()` additionally fires if a second press occurs within `0.6s`.
- `on_long_press()` fires if held longer than `0.8s`.
- Fast taps missed during USB streaming automatically synthesize `on_press()` prior to `on_release()`.
- Call `request_redraw()` when key state changes. `DisplayPad` automatically uses fast per-button tile uploads for single key changes and full-panel batching for layout switches.
- Unassigned key slots (`None`) are automatically cleared to solid black hardware tiles.

## Acknowledgments
Performance optimizations and multi-page layout engine design inspired by [ramisotti13-eng/BaseCamp-Linux](https://github.com/ramisotti13-eng/BaseCamp-Linux).

