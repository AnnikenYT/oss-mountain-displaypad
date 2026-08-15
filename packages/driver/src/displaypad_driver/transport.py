"""USB transport layer for the DisplayPad device (Interface 1 bulk OUT + Interface 3 hidraw)."""

import gc
import time
from logging import getLogger
from typing import Tuple, Optional

from .exceptions import TransportError, DeviceNotFoundError
from .protocol import VID, PID

log = getLogger(__name__)

try:
    import hid
    HID_AVAILABLE = True
except ImportError:
    HID_AVAILABLE = False

try:
    import usb.core
    import usb.util
    PYUSB_AVAILABLE = True
except ImportError:
    PYUSB_AVAILABLE = False


def check_dependencies():
    if not HID_AVAILABLE:
        raise TransportError("hidapi is not installed (pip install hid)")
    if not PYUSB_AVAILABLE:
        raise TransportError("PyUSB is not installed (pip install pyusb)")


def open_interfaces() -> Tuple[usb.core.Device, hid.Device]:
    """Open PyUSB device (Interface 1 for pixel bulk data) and HID device (Interface 3 for commands/events)."""
    check_dependencies()
    gc.collect()

    device_path = None
    for d in hid.enumerate(VID, PID):
        if d.get('interface_number') == 3:
            device_path = d.get('path')
            break

    if device_path is None:
        raise DeviceNotFoundError(f"DisplayPad Interface 3 not found ({hex(VID)}:{hex(PID)})")

    last_err = None
    for attempt in range(3):
        hid_dev = None
        try:
            hid_dev = hid.Device(path=device_path)
            hid_dev.nonblocking = False
            usb_dev = usb.core.find(idVendor=VID, idProduct=PID)
            if usb_dev is None:
                hid_dev.close()
                raise DeviceNotFoundError("DisplayPad not found via PyUSB")

            usb.util.claim_interface(usb_dev, 1)
            init_handshake_ctrl(usb_dev)
            return usb_dev, hid_dev
        except Exception as e:
            last_err = e
            if hid_dev is not None:
                try:
                    hid_dev.close()
                except Exception:
                    pass
            time.sleep(0.2)

    raise TransportError(f"DisplayPad open failed: {last_err}") if last_err else DeviceNotFoundError("Open failed")


def init_handshake_ctrl(usb_dev):
    """
    Step 1: Detach kernel driver on IF0 (keyboard) if active.
    Step 2: SET_IDLE on IF0, IF1 (pixels), IF3 (cmd) to suppress report flooding.
    Step 3: SET_REPORT (payload {0x03, 0x01}) on IF0 to enable event reporting mode.
    Step 4: Release IF0 and reattach its kernel driver so OS keyboard keeps working.
    """
    if0_was_active = False
    try:
        if0_was_active = bool(usb_dev.is_kernel_driver_active(0))
    except Exception:
        pass

    if if0_was_active:
        try:
            usb_dev.detach_kernel_driver(0)
        except Exception:
            pass

    if0_claimed = False
    try:
        usb.util.claim_interface(usb_dev, 0)
        if0_claimed = True
    except Exception:
        pass

    def _set_idle(iface):
        try:
            usb_dev.ctrl_transfer(0x21, 0x0A, 0x0000, iface, None, timeout=500)
        except Exception:
            pass

    if if0_claimed:
        _set_idle(0)
    _set_idle(1)  # IF_PIXELS
    _set_idle(3)  # IF_CMD

    if if0_claimed:
        try:
            usb_dev.ctrl_transfer(0x21, 0x09, 0x0203, 0x0000, bytes([0x03, 0x01]), timeout=500)
        except Exception:
            pass
        try:
            usb.util.release_interface(usb_dev, 0)
        except Exception:
            pass
        if if0_was_active:
            try:
                usb_dev.attach_kernel_driver(0)
            except Exception:
                pass


def close_interfaces(usb_dev: Optional[usb.core.Device], hid_dev: Optional[hid.Device]):
    """Release interfaces and dispose of USB resources cleanly."""
    if usb_dev is not None:
        try:
            usb.util.release_interface(usb_dev, 1)
        except Exception:
            pass
        try:
            usb.util.dispose_resources(usb_dev)
        except Exception:
            pass
    if hid_dev is not None:
        try:
            hid_dev.close()
        except Exception:
            pass

