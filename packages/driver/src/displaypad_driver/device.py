"""Higher-level DisplayPad device API built on top of the USB transport."""
import struct
import logging
import time

from .transport import USBTransport
from .protocol import URB_HEADERS, get_pressed_keys, Endpoint
from .exceptions import DisplayPadError

log = logging.getLogger(__name__)


class DisplayPad:
    """Object representing the DisplayPad device with friendly methods.

    Example:
        d = DisplayPad(0x3282, 0x0009)
        d.set_brightness(50)
    """

    def __init__(self, vendor_id: int = 0x3282, product_id: int = 0x0009):
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

    def poll_key(self, timeout=500) -> dict:
        """Poll for key events and return pressed and released keys.
        
        Returns:
            A dictionary with 'pressed' and 'released' keys:
            {
                'pressed': [list of newly pressed key indices],
                'released': [list of newly released key indices],
                'current': [list of all currently pressed key indices]
            }
        """
        
        if hasattr(self, '_pending_inputs') and self._pending_inputs:
            msg = self._pending_inputs.pop(0)
        else:
            try:
                msg = self.transport.read_interrupt(timeout=timeout)
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

    def set_panel_image(self, raw_data, left=0, top=0, bottom=240, right=800) -> bool:
        """
        1. Expects raw bytes (already formatted as BGR).
        2. Polls for inputs WHILE sending data to prevent missed releases.
        """
        header = URB_HEADERS.get('SetPanelImage')
        success_header = bytearray([0x21, 0, 0xff])

        right -= 1
        bottom -= 1

        height = (bottom - top) + 1
        width = (right - left) + 1
        area = (height * width * 3) >> 9

        msg = struct.pack('<hxxxxhh', area, right, bottom)
        msg = bytearray(header) + bytearray(msg)
        r = self.transport.write_interrupt(0x4, msg)

        if isinstance(r, (bytes, bytearray)) and bytes(header) in r:
            # --- THE CHUNK LOOP ---
            chunk_size = 1024
            total_len = len(raw_data)
            
            # We will check for inputs every ~16KB (approx every 10-25ms)
            # This keeps the UI responsive without slowing down the transfer too much
            check_interval = 16 * 1024 
            next_check = check_interval

            for i in range(0, total_len - chunk_size, chunk_size):
                # 1. Send the Chunk
                chunk = raw_data[i : i + chunk_size]
                self.transport.write_interrupt(Endpoint.BULK_OUT.value, chunk, length=chunk_size, read_response=False)
                
                # If we are effectively "blocking" the main thread, we must check inputs here.
                if i > next_check:
                    self._quick_poll()
                    next_check += check_interval

            # Send any remaining bytes
            remainder = raw_data[(total_len // chunk_size) * chunk_size :]
            if remainder:
                resp = self.transport.write_interrupt(Endpoint.BULK_OUT.value, remainder, length=len(remainder), read_response=True)
            
            if resp and success_header in resp[:len(success_header)]:
                return True
            else:
                return False
        raise DisplayPadError('Device not ready for image data')

    def _quick_poll(self):
        """
        Non-blocking read of the interrupt endpoint.
        If we find an event, we stash it in an internal buffer.
        """
        try:
            # We don't want to block here, so set a very short timeout. 1 is too little, 2 seems ok.
            data = self.transport.read_interrupt(Endpoint.INTERRUPT_IN.value, length=64, timeout=2)
            
            if data:
                # We will process it the next time the user calls poll()
                if not hasattr(self, '_pending_inputs'):
                    self._pending_inputs = []
                self._pending_inputs.append(data)
                
        except Exception:
            # Timeouts are expected here, just ignore them
            pass