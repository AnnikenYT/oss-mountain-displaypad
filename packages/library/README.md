# displaypad-lib package

This package provides a high-level library for interacting with the Mountain DisplayPad device, built on top of the `displaypad-driver` package.

The main class is the `DisplayPad`. Opening it as a context manager will automatically handle device connection and disconnection.

The `DisplayPad` contains a list of `Button`s. A button represets a physical key on the DisplayPad, and provides the ability to register callback functions for key press and release events. **Please Note**: The DisplayPad is not incredibly fast at reporting key events, so rapid key presses may be missed, especially if multiple keys are pressed in quick succession or an Image is being sent to the DisplayPad at the same time. (If you know how to improve this, please open an issue or PR!)

Each `Button` can be assigned an `Icon`. An `Icon` represents the image displayed on a button, and can be created from image files or raw RGB data. It can also display a text label which can be changed.

For a usage example, see [lib_example.py](../../examples/lib_example.py).