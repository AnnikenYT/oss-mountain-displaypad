# Checks if the current user has permissions to access the udev device files for DisplayPad.
# Vendor: 0x3282, Product: 0x0009
import os
import sys
import usb.core
import usb.util
from pathlib import Path

def check_udev_permissions(vendor_id: int, product_id: int) -> bool:
    """Check if the current user has permissions to access the udev device files."""
    try:
        dev = usb.core.find(idVendor=vendor_id, idProduct=product_id)
        if dev is None:
            print(f"Device {hex(vendor_id)}:{hex(product_id)} not found.")
            return False

        # Try to read the device descriptor to check permissions
        _ = dev.ctrl_transfer(0x80, 6, 0x100, 0, 18)
        print(f"User has permissions to access device {hex(vendor_id)}:{hex(product_id)}.")
        return True
    except usb.core.USBError as e:
        if e.errno == 13:  # Permission denied
            print(f"Permission denied for device {hex(vendor_id)}:{hex(product_id)}.")
            # Print udev rules suggestion
            udev_rule = f'SUBSYSTEM=="usb", ATTR{{idVendor}}=="{vendor_id:04x}", ATTR{{idProduct}}=="{product_id:04x}", MODE="0666"'
            print("You may need to create a udev rule like the following:")
            print(udev_rule)
            return False
        else:
            print(f"USB error occurred: {e}")
            return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
    
if __name__ == "__main__":
    VENDOR_ID = 0x3282
    PRODUCT_ID = 0x0009
    has_permissions = check_udev_permissions(VENDOR_ID, PRODUCT_ID)
    if not has_permissions:
        sys.exit(1)
    sys.exit(0)