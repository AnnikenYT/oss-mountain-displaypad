import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../packages/driver/src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../packages/library/src')))

from displaypad_lib import DisplayPad, Key
from displaypad_lib.key import FramerateLimitedKey
from PIL import ImageFont
from datetime import datetime


pad = DisplayPad()

class DateKey(Key):
    
    def __init__(self, format="%Y-%m-%d"):
        super().__init__()
        self.format = format
        self.date_str = ""
        
    def on_tick(self):
        now = datetime.now()
        date_str = now.strftime(self.format)
        if date_str != self.date_str:
            self.date_str = date_str
            self.request_redraw()
        return super().on_tick()
    
    def render(self, ctx):    
        ctx.fill("black")
        ctx.center_text(self.date_str, color="white", font=ImageFont.truetype("examples/assets/arial.ttf", 32))

pad[2] = DateKey(format="%H")
pad[3] = DateKey(format="%M")
pad[7] = DateKey(format="%a")
pad[8] = DateKey(format="%b")
pad[9] = DateKey(format="%d")
pad[10] = DateKey(format="%Y")

initial_screen_path = os.path.join(os.path.dirname(__file__), 'assets/initial_screen.png')

try:
    while True:
        pad.update()
except KeyboardInterrupt:
    pass
finally:
    if os.path.exists(initial_screen_path):
        pad.push_image(initial_screen_path)
    pad.disable()