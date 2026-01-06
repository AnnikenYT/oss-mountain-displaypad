# displaypad-driver package

This package contains a refactored, object-oriented driver for the DisplayPad device.

Most of the functionality is taken from the original procedural code in the [ReversingForFun DisplayPad project](https://github.com/ReversingForFun/MountainDisplayPadPy/tree/main).

Modules:

- `transport.py` - `USBTransport` class encapsulates low-level USB read/write operations.
- `device.py` - `DisplayPad` class providing friendly methods: `poll_key`, `set_brightness`, `set_panel_image`, `enable`.
- `protocol.py` - protocol constants and helpers used by the driver.
 - `image.py` - `load_image_bytes(path, size=None)` helper to load/resize images and return a list
     of `(R,G,B)` tuples suitable for `DisplayPad.set_panel_image`.

For a usage example, see [driver_example.py](../../examples/driver_example.py).

Note: operations that write to or read from USB will raise exceptions defined in `displaypad.exceptions` on error.
