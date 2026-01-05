# displaypad package

This package contains a refactored, object-oriented driver for the DisplayPad device.

Modules:

- `transport.py` — `USBTransport` class encapsulates low-level USB read/write operations.
- `device.py` — `DisplayPad` class providing friendly methods: `poll_key`, `set_brightness`, `set_panel_image`, `enable`.
- `protocol.py` — protocol constants and helpers used by the driver.
 - `image.py` — `load_image_bytes(path, size=None)` helper to load/resize images and return a list
     of `(R,G,B)` tuples suitable for `DisplayPad.set_panel_image`.

Quick usage:

```python
from displaypad import DisplayPad

# create instance (vendor_id, product_id)
dp = DisplayPad(0x3282, 0x0009)

# set brightness
dp.set_brightness(50)

# poll for a key press
key = dp.poll_key()
if key is not None:
    print('key pressed', key)

# send image data (list of (R,G,B) tuples)
# dp.set_panel_image(imgdata)
```

Note: operations that write to or read from USB will raise exceptions defined in `displaypad.exceptions` on error.
