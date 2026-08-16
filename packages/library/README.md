# displaypad-lib package

`displaypad-lib` provides a high-level, multi-page library for interacting with the Mountain DisplayPad device, built on top of `displaypad-driver`.

## Acknowledgments
Multi-page layout engine design, auto-timeout page transitions, and responsive async rendering were built with inspiration from [ramisotti13-eng/BaseCamp-Linux](https://github.com/ramisotti13-eng/BaseCamp-Linux).

## Key Features

- **Multi-Page Layout Engine (`Page`, `PageManager`)**: Create named 12-key pages with navigation stacks and auto-timeout transitions (`mode: "after" | "idle"`). See [Page](https://github.com/AnnikenYT/oss-mountain-displaypad/wiki/Page).
- **Key Abstractions (`displaypad_lib.key`)**:
  - `Key` (base class) — Implement `render(ctx: KeyContext)` and optional lifecycle hooks (`on_mount`, `on_press`, `on_release`, `on_double_press`, `on_long_press`, `on_tick`).
  - `GifKey` — Play animated GIFs at native frame rates with rotation support.
  - `IconKey` — Static image icons with aspect-ratio scaling and margins.
  - `LabelKey` — Dynamic centered text labels with customizable colors.
  - `FramerateLimitedKey` — Rate-limited key rendering.
  - `LoggerKey` — Diagnostics key logging presses and releases.
- **Drawing Context (`KeyContext`)**:
  - Isolated per-key PIL `Image` surface with native PIL `ImageDraw` (`ctx.draw`) access, automatic tile clipping, and key-relative drawing primitives: `center_text`, `text`, `rectangle`, `rounded_rectangle`, `ellipse`, `line`, `polygon`, `arc`, `fill`, `clear`, `paste_image`, `apply_alpha_mask`. Supports both `color` and `fill` parameter aliases.
- **Async Queue & Hybrid Batch Rendering**:
  - Background thread drains key updates with frame deduplication. Single-key updates use fast per-button tile uploads; layout changes automatically batch update the full panel.

For documentation, see the [project wiki](https://github.com/AnnikenYT/oss-mountain-displaypad/wiki).

For usage examples, see [lib_example.py](https://github.com/AnnikenYT/oss-mountain-displaypad/blob/main/examples/lib_example.py) and [clock.py](https://github.com/AnnikenYT/oss-mountain-displaypad/blob/main/examples/clock.py).