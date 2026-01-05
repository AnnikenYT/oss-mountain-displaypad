"""Image helpers for DisplayPad.

Provides utilities to load and normalize image data for sending to the device.
"""
from typing import List, Tuple, Optional
from PIL import Image


def load_image_bytes(path: str, size: Optional[Tuple[int, int]] = None) -> List[Tuple[int, int, int]]:
    """Load an image from `path` and return a list of (R,G,B) tuples.

    - If `size` is provided, the image will be resized to that size (width,height).
    - Alpha channels are ignored; pixels are returned as 3-tuples.
    """
    with Image.open(path) as im:
        if size is not None:
            im = im.convert('RGBA').resize(size, resample=Image.Resampling.NEAREST)
        else:
            im = im.convert('RGBA')

        pixels = list(im.getdata())

    # normalize to (R,G,B) tuples
    rgb_pixels = [(r, g, b) for (r, g, b, *_) in pixels]
    return rgb_pixels
