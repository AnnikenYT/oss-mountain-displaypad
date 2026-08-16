# displaypad-driver package

`displaypad-driver` provides a thread-safe, high-performance driver for the Mountain DisplayPad device.

## Acknowledgments
Performance optimizations, dual-interface transport handling, initialization handshakes, and input report interleaving were built with inspiration from [ramisotti13-eng/BaseCamp-Linux](https://github.com/ramisotti13-eng/BaseCamp-Linux).

## Modules

- `transport.py` — Low-level interface opener (`open_interfaces`, `init_handshake_ctrl`, `close_interfaces`). Claims Interface 1 (PyUSB display bulk transfer endpoint `0x02`) and Interface 3 (`hidapi` command/event endpoint), handles temporary IF0 kernel driver detachment to send HID `SET_IDLE` and `SET_REPORT` commands.
- `device.py` — Thread-safe `DisplayPad` manager.
  - `upload_button(key_index, bgr_pixels)` — Uploads a 102×102 BGR tile to a specific key slot (0–11) with non-blocking HID report interleaving.
  - `upload_panel(tiles_bgr)` — Uploads 12 tile payloads in batch.
  - `poll_key(timeout)` — Non-blocking polling returning `pressed`, `released`, and `current` key lists.
  - `set_brightness(percent)` — Adjusts backlight brightness (0–100%).
- `protocol.py` — VID/PID constants, payload headers, INIT/IMG templates, and `get_pressed_keys` bitmask parser.
- `image.py` — Image processing utilities:
  - `image_to_bgr102(img, rotation)` — Converts PIL Image to 102×102 BGR bytes with 0°/90°/180°/270° rotation.
  - `split_image_to_tiles(img, rotation)` — Slices full-panel 612×204 images into 12 BGR tile payloads.
  - `split_gif_to_tiles(gif)` & `load_gif_frames(gif)` — Animated GIF parser.
  - `make_label_icon()` & `make_folder_icon()` — Dynamic text label and icon generator.

For a usage example, see [driver_example.py](https://github.com/AnnikenYT/oss-mountain-displaypad/blob/main/examples/driver_example.py).

