"""USB transport layer for the DisplayPad device."""
from typing import Optional
import usb.core
import usb.util
import array
from .exceptions import TransportError, DeviceNotFoundError
from logging import getLogger

log = getLogger(__name__)

class USBTransport:
    """Low-level USB read/write handling."""

    def __init__(self, vendor_id: int, product_id: int):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device = self._get_device()

    def _get_device(self):
        dev = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)
        if dev is None:
            raise DeviceNotFoundError(f"Device {hex(self.vendor_id)}:{hex(self.product_id)} not found")

        # detach kernel drivers if needed
        try:
            for cfg in dev:
                for intf in cfg:
                    if dev.is_kernel_driver_active(intf.bInterfaceNumber):
                        try:
                            dev.detach_kernel_driver(intf.bInterfaceNumber)
                        except usb.core.USBError:
                            # ignore and continue; operation may fail later when accessing
                            pass
        except Exception:
            # some backends or devices may not support iteration the same
            pass

        dev.set_configuration()
        # On Windows, freeing resources here breaks subsequent bulk transfers.
        # Instead, explicitly claim the first interface if present and keep it open.
        try:
            cfg = dev.get_active_configuration()
            intf = cfg[(0, 0)]
            usb.util.claim_interface(dev, intf.bInterfaceNumber)
        except Exception:
            # If claiming fails, continue; many backends claim automatically.
            pass
        return dev

    def read_interrupt(self, endpoint: int = 0x83, length: int = 64, buffer: int = 64, timeout: int = 1000) -> bytes:
        """Read and accumulate data until 'length' bytes are received."""
        remainder = array.array('B', [])
        try:
            urbrx = self.device.read(endpoint, buffer, timeout)
            remainder.extend(urbrx)
            while len(remainder) < length:
                urbrx = self.device.read(endpoint, buffer, timeout)
                remainder.extend(urbrx)
            return bytearray(remainder)
        except usb.core.USBError as e:
            raise TransportError(e)

    def clear_halt(self, endpoint: int):
        """Best-effort halt clear; USB stacks may stall mid-transfer on Windows."""
        try:
            usb.util.clear_halt(self.device, endpoint)
        except Exception:
            # Clearing a halt can legitimately fail depending on backend/state.
            pass

    def write_interrupt(self, endpoint: int = 0x4, data: bytes = b'', length: int = 64, timeout: int = 2000, read_response: bool = True) -> bytes:
        """Write data broken into 'length' chunks, then read response."""
        remainder = bytes(data)
        # log.debug(f"Writing to endpoint {endpoint}: {data}")
        try:
            while len(remainder) != 0:
                buffer = remainder[:length]
                # pad to length
                if len(buffer) < length:
                    buffer = bytes(buffer) + (b"\x00" * (length - len(buffer)))
                urbtx = self.device.write(endpoint, buffer, timeout)
                if urbtx < length:
                    # if write length is less than expected, raise TransportError
                    # Note: On Windows, the USB driver may report one extra byte due to protocol overhead
                    raise TransportError(f"Wrote {urbtx} bytes, expected at least {length}")
                remainder = remainder[length:]
            if not read_response:
                return b''
            # read a standard small response
            resp = self.read_interrupt(endpoint=0x83, length=64)
            return resp
        except usb.core.USBError as e:
            raise TransportError(e)
