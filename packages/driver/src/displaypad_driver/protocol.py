"""Protocol helpers and constants for the DisplayPad device."""

VID = 0x3282
PID = 0x0009

NUM_KEYS = 12
KEYS_PER_ROW = 6
ICON_SIZE = 102
CHUNK_SIZE = 1024
HEADER_SIZE = 306
PACKET_SIZE = 31438  # total payload = 31744 = 31 × 1024
EP_DISPLAY = 0x02
EP_CMD = 0x04
EP_IN = 0x83

# Key-event byte/bit map: K1-K7 -> data[42], K8-K12 -> data[47]
KEY_MAP = (
    [(42, m) for m in (0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80)] +
    [(47, m) for m in (0x01, 0x02, 0x04, 0x08, 0x10)]
)

INIT_MSG = bytes.fromhex(
    "0011800000010000000000000000000000000000000000000000000000000000"
    "00000000000000000000000000000000000000000000000000000000000000"
    "0000"
)

IMG_MSG_TEMPLATE = bytearray.fromhex(
    "0021000000FF3d00006565000000000000000000000000000000000000000000"
    "00000000000000000000000000000000000000000000000000000000000000"
    "0000"
)


def get_pressed_keys(msg: bytes) -> list:
    """Extract the list of currently pressed keys from the message (0-indexed)."""
    pressed_keys = []
    if not msg or len(msg) < 48 or msg[0] != 0x01:
        return pressed_keys

    for idx, (byte_idx, mask) in enumerate(KEY_MAP):
        if byte_idx < len(msg) and (msg[byte_idx] & mask):
            pressed_keys.append(idx)

    return pressed_keys

