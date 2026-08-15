"""Unit tests for packages/driver."""

import os
import sys
import unittest
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../packages/driver/src')))

from displaypad_driver.protocol import get_pressed_keys, NUM_KEYS, ICON_SIZE
from displaypad_driver.image import (
    image_to_bgr102, split_image_to_tiles, split_gif_to_tiles,
    load_gif_frames, make_label_icon, make_folder_icon
)


class TestDriverProtocol(unittest.TestCase):

    def test_get_pressed_keys_byte42(self):
        # K1 (idx 0) is bit 1 of byte 42 (0x02)
        msg = bytearray(64)
        msg[0] = 0x01
        msg[42] = 0x02
        self.assertEqual(get_pressed_keys(msg), [0])

        # K7 (idx 6) is bit 7 of byte 42 (0x80)
        msg[42] = 0x80
        self.assertEqual(get_pressed_keys(msg), [6])

    def test_get_pressed_keys_byte47(self):
        # K8 (idx 7) is bit 0 of byte 47 (0x01)
        msg = bytearray(64)
        msg[0] = 0x01
        msg[47] = 0x01
        self.assertEqual(get_pressed_keys(msg), [7])

        # K12 (idx 11) is bit 4 of byte 47 (0x10)
        msg[47] = 0x10
        self.assertEqual(get_pressed_keys(msg), [11])

    def test_get_pressed_keys_multiple(self):
        msg = bytearray(64)
        msg[0] = 0x01
        msg[42] = 0x06  # bits 1 and 2 -> K1 (0) and K2 (1)
        msg[47] = 0x03  # bits 0 and 1 -> K8 (7) and K9 (8)
        self.assertEqual(get_pressed_keys(msg), [0, 1, 7, 8])


class TestDriverImage(unittest.TestCase):

    def setUp(self):
        self.test_img = Image.new("RGB", (612, 204), (255, 0, 0))

    def test_image_to_bgr102(self):
        bgr = image_to_bgr102(self.test_img)
        self.assertEqual(len(bgr), ICON_SIZE * ICON_SIZE * 3)
        # Red RGB (255, 0, 0) becomes Blue BGR (0, 0, 255)
        self.assertEqual(bgr[:3], bytes([0, 0, 255]))

    def test_split_image_to_tiles(self):
        tiles = split_image_to_tiles(self.test_img)
        self.assertEqual(len(tiles), NUM_KEYS)
        for tile in tiles:
            self.assertEqual(len(tile), ICON_SIZE * ICON_SIZE * 3)

    def test_make_label_icon(self):
        img = make_label_icon("Test Key")
        self.assertEqual(img.size, (ICON_SIZE, ICON_SIZE))


if __name__ == '__main__':
    unittest.main()
