"""Higher-level DisplayPad device API built on top of the USB transport."""

import logging
import threading
import time
from typing import List, Dict, Optional, Tuple, Set


from .exceptions import DisplayPadError, TransportError, DeviceNotFoundError
from .protocol import (
    VID, PID, NUM_KEYS, ICON_SIZE, CHUNK_SIZE, HEADER_SIZE, PACKET_SIZE,
    EP_DISPLAY, INIT_MSG, IMG_MSG_TEMPLATE, KEY_MAP, get_pressed_keys
)
from .transport import open_interfaces, close_interfaces, check_dependencies

log = logging.getLogger(__name__)


class DisplayPad:
    """Object representing the DisplayPad device.

    Example:
        with DisplayPad() as d:
            d.set_brightness(50)
            d.upload_button(0, bgr_data)
    """

    def __init__(self, vendor_id: int = VID, product_id: int = PID):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.usb_dev = None
        self.hid_dev = None
        self.pressed_keys: Set[int] = set()
        self.connected = False
        self._usb_lock = threading.Lock()
        self._pending_key_packets: List[bytes] = []

        self.connect()

    def connect(self):
        """Open USB interfaces and execute initialization handshake."""
        with self._usb_lock:
            if self.connected:
                return

            self.usb_dev, self.hid_dev = open_interfaces()
            self._init_device()
            self.connected = True

    def close(self):
        """Close USB interfaces and release resources."""
        with self._usb_lock:
            if self.connected:
                close_interfaces(self.usb_dev, self.hid_dev)
                self.usb_dev = None
                self.hid_dev = None
                self.connected = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _init_device(self):
        """Send INIT_MSG on Interface 3 and wait for a matching echo with 250ms firmware settling sleep."""
        if not self.hid_dev:
            raise DisplayPadError("HID device interface not open")

        pkt = INIT_MSG
        echo = pkt[1:6]
        ack_received = False

        for _attempt in range(60):
            try:
                self.hid_dev.write(pkt)
            except Exception:
                time.sleep(0.01)
                continue

            try:
                resp = self.hid_dev.read(64, timeout=500)
            except Exception:
                resp = None

            if not resp:
                time.sleep(0.01)
                continue

            if len(resp) >= 5 and bytes(resp[:5]) == echo:
                # Firmware settling delay before display engine is ready
                time.sleep(0.25)
                ack_received = True
                break

        if not ack_received:
            raise DisplayPadError("DisplayPad did not respond to INIT handshake")

    def set_brightness(self, percent: int = 100):
        """Set DisplayPad backlight brightness. percent: 0 to 100."""
        with self._usb_lock:
            if not self.hid_dev:
                raise DisplayPadError("Device not connected")

            percent = max(0, min(100, int(percent)))
            buf = bytearray(64)
            buf[0] = 0x12
            buf[1] = 0x03
            buf[4] = percent
            try:
                self.hid_dev.write(bytes(buf))
            except Exception as e:
                raise DisplayPadError(f"Failed to set brightness: {e}")

    def upload_button(self, key_index: int, bgr_pixels: bytes, key_events: Optional[list] = None):
        """Upload a 102x102 BGR image payload to a specific button (key_index 0..11).

        If key_events list is provided or key events arrive during ACK wait,
        key event reports are buffered so no keypresses are lost.
        """
        if not (0 <= key_index < NUM_KEYS):
            raise ValueError(f"key_index must be between 0 and {NUM_KEYS - 1}")

        with self._usb_lock:
            if not self.usb_dev or not self.hid_dev:
                raise DisplayPadError("Device not connected")

            # Step 1: Send image message template targeting key_index
            msg = bytearray(IMG_MSG_TEMPLATE)
            msg[5] = key_index
            self.hid_dev.write(bytes(msg))

            # Step 2: Wait for readiness ACK (0x21 0x00 0x00), buffering incoming key events
            for _ in range(100):
                resp = self.hid_dev.read(64, timeout=5)
                if resp and len(resp) >= 3 and resp[0] == 0x21 and resp[1] == 0x00 and resp[2] == 0x00:
                    break
                if resp and len(resp) >= 48 and resp[0] == 0x01:
                    raw_evt = bytes(resp)
                    if not self._pending_key_packets or self._pending_key_packets[-1] != raw_evt:
                        self._pending_key_packets.append(raw_evt)
                    if key_events is not None:
                        key_events.append(list(resp))
            else:
                raise DisplayPadError(f"No ready response for key {key_index}")

            # Step 3: Write payload (HEADER_SIZE + PACKET_SIZE) in 1024-byte chunks
            payload = bytearray(HEADER_SIZE + PACKET_SIZE)
            payload[HEADER_SIZE:HEADER_SIZE + len(bgr_pixels)] = bgr_pixels

            for i in range(0, len(payload), CHUNK_SIZE):
                self.usb_dev.write(EP_DISPLAY, bytes(payload[i:i + CHUNK_SIZE]), timeout=1000)

            # Step 4: Wait for confirmation ACK (0x21 0x00 0xFF), buffering incoming key events
            for _ in range(100):
                resp = self.hid_dev.read(64, timeout=5)
                if resp and len(resp) >= 3 and resp[0] == 0x21 and resp[1] == 0x00 and resp[2] == 0xFF:
                    return
                if resp and len(resp) >= 48 and resp[0] == 0x01:
                    raw_evt = bytes(resp)
                    if not self._pending_key_packets or self._pending_key_packets[-1] != raw_evt:
                        self._pending_key_packets.append(raw_evt)
                    if key_events is not None:
                        key_events.append(list(resp))

            raise DisplayPadError(f"Transfer confirmation timed out for key {key_index}")



    def upload_panel(self, tiles_bgr: List[bytes], key_events: Optional[list] = None):
        """Upload BGR payloads for all 12 buttons."""
        if len(tiles_bgr) != NUM_KEYS:
            raise ValueError(f"Expected {NUM_KEYS} BGR tile payloads, got {len(tiles_bgr)}")

        for idx, bgr in enumerate(tiles_bgr):
            self.upload_button(idx, bgr, key_events=key_events)

    def read_raw_report(self, timeout: int = 150) -> Optional[bytes]:
        """Read a raw HID report from Interface 3."""
        with self._usb_lock:
            if not self.hid_dev:
                return None
            try:
                data = self.hid_dev.read(64, timeout=timeout)
                return bytes(data) if data else None
            except Exception as e:
                log.debug("read_raw_report failed: %s", e)
                return None

    def poll_key(self, timeout: int = 150) -> Dict[str, List[int]]:
        """Poll for key events and return newly pressed, newly released, and current key lists.

        Drains buffered key events captured during image updates first.
        """
        raw = None
        with self._usb_lock:
            if self._pending_key_packets:
                raw = self._pending_key_packets.pop(0)
            elif self.hid_dev:
                try:
                    data = self.hid_dev.read(64, timeout=timeout)
                    raw = bytes(data) if data else None
                except Exception as e:
                    log.debug("poll_key read failed: %s", e)

        if not raw or len(raw) < 48 or raw[0] != 0x01:
            return {
                'pressed': [],
                'released': [],
                'current': sorted(list(self.pressed_keys))
            }

        current_pressed = set(get_pressed_keys(raw))
        newly_pressed = list(current_pressed - self.pressed_keys)
        newly_released = list(self.pressed_keys - current_pressed)
        self.pressed_keys = current_pressed

        return {
            'pressed': sorted(newly_pressed),
            'released': sorted(newly_released),
            'current': sorted(list(current_pressed))
        }