"""Higher-level DisplayPad device API built on top of the USB transport."""
from typing import Optional
import struct
import logging
import time

from .transport import USBTransport
from .protocol import URB_HEADERS, KEYMAP, parse_response, get_pressed_keys
from .image import load_image_bytes
from .exceptions import DisplayPadError
from time import sleep

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
        self.pressed_keys = set()  # Track currently pressed keys
        
        self.reset()
        self.enable(True)
        
    def reset(self):
        self.transport.device.reset()
    
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.reset()
        self.enable(False)

    def poll_key(self) -> dict:
        """Poll for key events and return pressed and released keys.
        
        Returns:
            A dictionary with 'pressed' and 'released' keys:
            {
                'pressed': [list of newly pressed key indices],
                'released': [list of newly released key indices],
                'current': [list of all currently pressed key indices]
            }
        """
        try:
            msg = self.transport.read_interrupt()
        except Exception as e:
            log.debug('poll_key read failed: %s', e)
            return {'pressed': [], 'released': [], 'current': list(self.pressed_keys)}

        if not isinstance(msg, (bytes, bytearray)):
            return {'pressed': [], 'released': [], 'current': list(self.pressed_keys)}

        if not msg or msg[0] != 0x01:
            return {'pressed': [], 'released': [], 'current': list(self.pressed_keys)}

        # Get current pressed keys from message
        current_pressed = set(get_pressed_keys(msg))
        
        # Calculate newly pressed and released keys
        newly_pressed = list(current_pressed - self.pressed_keys)
        newly_released = list(self.pressed_keys - current_pressed)
        
        # Update state
        self.pressed_keys = current_pressed
        
        return {
            'pressed': sorted(newly_pressed),
            'released': sorted(newly_released),
            'current': sorted(current_pressed)
        }

    def enable(self, enabled: bool = True) -> bool:
        header = URB_HEADERS.get('APEnable')
        enabled_byte = 0x1 if enabled else 0x0
        msg = bytearray(header) + bytearray([enabled_byte])

        log.debug("Enabling device: %s", "ON" if enabled else "OFF")
        log.debug("Message to send: %s", msg)

        try:
            start_time = time.time()
            r = self.transport.write_interrupt(0x4, msg)
            elapsed_time = time.time() - start_time
            log.debug("Write operation completed in %.2f seconds", elapsed_time)
        except Exception as e:
            log.error("Error during write_interrupt: %s", e)
            if hasattr(e, 'errno'):
                log.error("Error number: %s", e.errno)
            if hasattr(e, 'strerror'):
                log.error("Error description: %s", e.strerror)
            raise DisplayPadError(e)

        # parse response
        if isinstance(r, (bytes, bytearray)):
            log.debug("Response received: %s", r)
            if r.startswith(bytes(header)):
                if len(r) > len(header) + 1 and r[len(header) + 1] == 0x01:
                    self.enabled = enabled
                    log.debug("Device successfully enabled.")
                    return True
            self.enabled = enabled
            log.debug("Fallback: Device treated as %s.", "enabled" if enabled else "disabled")
            return True

        log.warning("Unexpected response or no response received.")
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
            width = (right - left)
            height = (bottom - top)
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
