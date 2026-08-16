"""DisplayPad package exports."""

from .device import DisplayPad
from .image import (
    image_to_bgr102, split_image_to_tiles, split_gif_to_tiles,
    load_gif_frames, make_label_icon, make_folder_icon
)
from .exceptions import DisplayPadError, TransportError, DeviceNotFoundError
from .protocol import (
    VID, PID, NUM_KEYS, KEYS_PER_ROW, ICON_SIZE, CHUNK_SIZE,
    HEADER_SIZE, PACKET_SIZE, EP_DISPLAY, EP_CMD, EP_IN
)

__version__ = "1.1.0"


__all__ = [
    "__version__",
    "DisplayPad",

    "image_to_bgr102",
    "split_image_to_tiles",
    "split_gif_to_tiles",
    "load_gif_frames",
    "make_label_icon",
    "make_folder_icon",
    "DisplayPadError",
    "TransportError",
    "DeviceNotFoundError",
    "VID",
    "PID",
    "NUM_KEYS",
    "KEYS_PER_ROW",
    "ICON_SIZE",
    "CHUNK_SIZE",
    "HEADER_SIZE",
    "PACKET_SIZE",
    "EP_DISPLAY",
    "EP_CMD",
    "EP_IN",
]