"""Higher-level DisplayPad device API built on top of the USB transport."""
from typing import Optional
import struct
import logging

from .transport import USBTransport
from .protocol import URB_HEADERS, KEYMAP, parse_response
from .image import load_image_bytes
from .exceptions import DisplayPadError

log = logging.getLogger(__name__)


class DisplayPad:
    """Object representing the DisplayPad device with friendly methods.

    Example:
        d = DisplayPad(0x3282, 0x0009)
        d.set_brightness(50)
    """

    def __init__(self, vendor_id: int, product_id: int):
        self.transport = USBTransport(vendor_id, product_id)
        self.enabled = False

        try:
            self.enable(True)
        except DisplayPadError as e:
            log.error('Failed to enable DisplayPad: %s', e)

    def poll_key(self) -> Optional[int]:
        """Poll for a key press and return the key index or None."""
        try:
            msg = self.transport.read_interrupt()
        except Exception as e:
            log.debug('poll_key read failed: %s', e)
            return None

        if not isinstance(msg, (bytes, bytearray)):
            return None

        if msg and msg[0] == 0x01:
            parsed = parse_response(msg)
            if parsed in KEYMAP:
                return KEYMAP.index(parsed)

        return None

    def enable(self, enabled: bool = True) -> bool:
        header = URB_HEADERS.get('APEnable')
        enabled_byte = 0x1 if enabled else 0x0
        msg = bytearray(header) + bytearray([enabled_byte])
        try:
            r = self.transport.write_interrupt(0x4, msg)
        except Exception as e:
            raise DisplayPadError(e)

        # parse response
        if isinstance(r, (bytes, bytearray)):
            if r.startswith(bytes(header)):
                # expected success byte is at header length + 1 in original implementation
                if len(r) > len(header) + 1 and r[len(header) + 1] == 0x01:
                    self.enabled = True
                    return True
                # sometimes device returns timeout tuple-equivalent -> treat as enabled
            # fallback: treat as enabled if no error
            self.enabled = True
            return True

        return False

    def set_brightness(self, value: int = 100):
        value = max(0, min(100, int(value)))
        header = URB_HEADERS.get('SetMainBrightness')
        msg = bytearray(header) + struct.pack('<B', value)
        try:
            r = self.transport.write_interrupt(0x4, msg)
            return r
        except Exception as e:
            raise DisplayPadError(e)

    def set_panel_image(self, imgdata=None, imgpath: Optional[str] = None, left=0, top=0, bottom=240, right=800) -> bool:
        """Send image data (list of (r,g,b) tuples) to the panel.

        imgdata should be a sequence of (R,G,B) tuples in PIL order. Alternatively,
        an `imgpath` may be provided and the image will be loaded and optionally
        resized to the panel area.
        """
        header = URB_HEADERS.get('SetPanelImage')
        success_header = bytearray([0x21, 0, 0xff])

        if imgpath:
            # calculate expected size and load/resize image accordingly
            width = (right - left) + 1
            height = (bottom - top) + 1
            imgdata = load_image_bytes(imgpath, size=(width, height))

        if not imgdata:
            raise DisplayPadError('imgdata required')

        right -= 1
        bottom -= 1

        height = (bottom - top) + 1
        width = (right - left) + 1
        area = (height * width * 3) >> 9

        msg = struct.pack('<hxxxxhh', area, right, bottom)
        msg = bytearray(header) + bytearray(msg)
        r = self.transport.write_interrupt(0x4, msg)

        if isinstance(r, (bytes, bytearray)) and bytes(header) in r:
            # build pixel stream (device expects BGR order)
            pixel_array = []
            for pixel in imgdata:
                # pixel might be (R,G,B, A) or (R,G,B)
                r_, g_, b_ = pixel[:3]
                pixel_bytes = bytes([b_, g_, r_])
                pixel_array.append(pixel_bytes)
            data = b''.join(pixel_array)

            # send in 1024-byte chunks
            chunk_size = 1024
            try:
                resp = self.transport.write_interrupt(0x2, data, length=chunk_size)
            except Exception as e:
                raise DisplayPadError(e)

            if resp and success_header in resp[:len(success_header)]:
                return True
            else:
                return False

        raise DisplayPadError('Device not ready for image data')
