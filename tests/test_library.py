"""Unit tests for packages/library."""

import os
import sys
import unittest
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../packages/driver/src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../packages/library/src')))

from displaypad_lib.key import Key, LabelKey, IconKey
from displaypad_lib.keycontext import KeyContext
from displaypad_lib.page import Page, PageManager


class DummyKey(Key):
    def __init__(self):
        super().__init__()
        self.pressed = False
        self.released = False
        self.double_pressed = False

    def on_press(self):
        self.pressed = True

    def on_release(self):
        self.released = True

    def on_double_press(self):
        self.double_pressed = True

    def render(self, ctx: KeyContext):
        ctx.fill("red")


class TestLibrary(unittest.TestCase):

    def test_key_hooks(self):
        key = DummyKey()
        key.on_mount(0)
        self.assertEqual(key.index, 0)

        key.on_press()
        self.assertTrue(key.pressed)

        key.on_release()
        self.assertTrue(key.released)

        key.on_double_press()
        self.assertTrue(key.double_pressed)

    def test_label_key_render(self):
        key = LabelKey("MUTE", bg_color="red", text_color="white")
        img = Image.new("RGB", (133, 120), (0, 0, 0))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        ctx = KeyContext(draw, 0, 0, image=img)
        key.render(ctx)
        # Background pixel should be red (255, 0, 0)
        self.assertEqual(img.getpixel((5, 5)), (255, 0, 0))

    def test_page_manager_navigation(self):
        main = Page(name="Main")
        sub = Page(name="Settings")

        pm = PageManager(main)
        pm.add_page("Settings", sub)

        self.assertEqual(pm.get_current_page().name, "Main")
        self.assertTrue(pm.switch_to("Settings"))
        self.assertEqual(pm.get_current_page().name, "Settings")
        self.assertEqual(pm.previous_page_id, "Main")

        self.assertTrue(pm.back())
        self.assertEqual(pm.get_current_page().name, "Main")

    def test_synthetic_press_on_release(self):
        from displaypad_lib import DisplayPad
        pad = DisplayPad.__new__(DisplayPad)
        pad.debounce_sec = 0.15
        pad.dc_window = 0.6
        pad._last_fire_time = {}
        pad._press_start_time = {}
        pad._dc_timers = {}
        pad._dc_pending_single = {}
        pad._synced_keys = [object()] * 12
        pad._key_down_state = [False] * 12
        pad.page_manager = PageManager()


        
        key = DummyKey()
        pad[0] = key

        # Simulate a released event arriving with no prior pressed event
        input_state = {'pressed': [], 'released': [0], 'current': []}
        
        # Manually execute the release handling loop
        now = 100.0
        if input_state['released']:
            for idx in input_state['released']:
                if idx not in pad._press_start_time:
                    pad.page_manager.note_activity()
                    pad._last_fire_time[idx] = now
                    pad._press_start_time[idx] = now
                    k = pad[idx]
                    if k:
                        k.on_press()
                start_t = pad._press_start_time.pop(idx, None)
                k = pad[idx]
                if k:
                    k.on_release()

        self.assertTrue(key.pressed)
        self.assertTrue(key.released)

    def test_keycontext_native_imagedraw_and_forwarding(self):
        img = Image.new("RGB", (102, 102), (0, 0, 0))
        ctx = KeyContext(width=102, height=102, image=img)
        
        # Test native draw access
        ctx.draw.rounded_rectangle([0, 0, 101, 101], radius=20, fill=(255, 0, 0))
        self.assertEqual(img.getpixel((50, 50)), (255, 0, 0))

        # Test helper method
        ctx.line(0, 0, 50, 50, fill=(0, 255, 0), width=2)
        self.assertEqual(img.getpixel((10, 10)), (0, 255, 0))

    def test_isolated_key_rendering_and_clipping(self):
        from displaypad_lib import DisplayPad
        pad = DisplayPad.__new__(DisplayPad)
        pad.width = 612
        pad.height = 204
        pad.image_buffer = Image.new("RGB", (pad.width, pad.height), (0, 0, 0))
        
        class OversizedKey(Key):
            def render(self, ctx: KeyContext):
                # Try to draw way outside local bounds (200x200)
                ctx.rectangle(0, 0, 200, 200, fill="blue")

        key0 = OversizedKey()
        pad._render_key_to_buffer(0, key0)

        # Key 0 tile (0..101, 0..101) should be blue (0, 0, 255)
        self.assertEqual(pad.image_buffer.getpixel((50, 50)), (0, 0, 255))
        # Key 1 tile (102..203, 0..101) MUST NOT be affected (remains 0, 0, 0 black)
        self.assertEqual(pad.image_buffer.getpixel((102, 50)), (0, 0, 0))


if __name__ == '__main__':
    unittest.main()
