"""Protocol helpers and constants for the DisplayPad device."""
import binascii
import struct
from enum import Enum

URB_HEADERS = {
    'GetTFTSleepTime': bytearray([0x22, 0x00, 0x00, 0x10]),
    'APEnable': bytearray([0x11, 0x80, 0, 0]),
    'SetTFTSleepTime': bytearray([0x22, 0x10]),
    'SetPanelImage': bytearray([0x21, 0x00, 0x00, 0x1]),
    'DisplayLogo': bytearray([0x23]),
    'GetMainBrightness': bytearray([0x10, 0x00, 0x01, 0x20]),
    'SetMainBrightness': bytearray([0x31, 0x20]),
}

class URBHeader(Enum):
    GetTFTSleepTime = 0x22
    APEnable = 0x11
    SetTFTSleepTime = 0x22
    SetPanelImage = 0x21
    DisplayLogo = 0x23
    GetMainBrightness = 0x10
    SetMainBrightness = 0x31

class Endpoint(Enum):
    INTERRUPT_IN = 0x83
    CONTROL_OUT = 0x04
    BULK_OUT = 0x02

def parse_response(msg: bytes) -> bytes:
    """Return hexlified representation of the response bytes as bytes.

    This matches the existing code which compares hex strings.
    """
    return binascii.hexlify(msg)


def get_pressed_keys(msg: bytes) -> list:
    """Extract the list of currently pressed keys from the message.
    
    Byte 42 (index 42) contains state of keys 1-7 (bits 1-7)
    Byte 47 (index 47) contains state of keys 8-12 (bits 0-4)
    """
    pressed_keys = []
    
    if len(msg) < 48:
        return pressed_keys
    
    # Check byte 42 for keys 1-7 (bits 1-7)
    byte_42 = msg[42]
    for bit in range(1, 8):
        if byte_42 & (1 << bit):
            pressed_keys.append(bit - 1)  # Convert to 0-indexed
    
    # Check byte 47 for keys 8-12 (bits 0-4)
    byte_47 = msg[47]
    for bit in range(0, 5):
        if byte_47 & (1 << bit):
            pressed_keys.append(7 + bit)  # Keys 8-12 map to indices 7-11
    
    return pressed_keys


def pack_message(message: bytes, buff_size: int = 64) -> bytes:
    """Pack a message into a fixed-size buffer for interrupt transfers."""
    rem_buff = int(buff_size - len(message))
    message = bytearray(message)
    packed_message = struct.pack(f'<{len(message)}s{rem_buff}x', message)
    return packed_message
