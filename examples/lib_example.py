import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../packages/driver/src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../packages/library/src')))

from displaypad_lib import DisplayPad, Key
from displaypad_lib.key import FramerateLimitedKey, LoggerKey, IconKey, GifKey
import logging
import time
from PIL import Image as PIL


logging.basicConfig(level=logging.INFO)

# The User defines a reusable component
class HoldButton(Key):
    def __init__(self, idx):
        super().__init__()
        self.idx = idx
        self.start = None
        self.held = False

    def on_press(self):
        self.start = time.time()
        self.held = True
        self.request_redraw()
        return super().on_press()

    def on_release(self):
        held_time = time.time() - self.start
        logging.info(f"Key {self.idx} was held for {held_time:.2f} seconds before release")
        self.held = False
        self.request_redraw()
        return super().on_release()

    def render(self, ctx):
        if self.held:
            ctx.rectangle(0, 0, 133, 120, color="orange")
            ctx.text(10, 50, f"HOLDING KEY {self.idx}", color="white")
        else:
            ctx.rectangle(0, 0, 133, 120, color="purple")
            ctx.text(10, 50, f"HOLD KEY {self.idx}", color="white")

class MuteButton(LoggerKey):
    def __init__(self, idx):
        super().__init__(idx)
        self.is_muted = False

    def on_press(self):
        self.is_muted = not self.is_muted
        # Do the actual system mute here
        self.request_redraw() # Request visual update
        return super().on_press()

    def render(self, ctx):
        if self.is_muted:
            ctx.rectangle(0, 0, 133, 120, color="red")
            ctx.text(50, 50, "MUTED", color="white")
        else:
            ctx.rectangle(0, 0, 133, 120, color="green")
            ctx.text(50, 50, "LIVE", color="white")
            
class CPUUsageKey(FramerateLimitedKey):
    def __init__(self, idx):
        super().__init__(0.5)
        self.idx = idx
        self.cpu_usage_history = [0] * 20  # Store the last 20 CPU usage values

    def on_tick(self):
        import psutil
        self.cpu_usage = psutil.cpu_percent()
        self.cpu_usage_history.append(self.cpu_usage)
        self.cpu_usage_history.pop(0)  # Keep the history size constant
        return super().on_tick()

    def render(self, ctx):
        ctx.fill("black")
        graph_width = ctx.width - 8
        graph_height = ctx.height - 35
        max_usage = 100

        points = self.cpu_usage_history
        if len(points) > 1:
            step_x = graph_width / (len(points) - 1)
            for i in range(len(points) - 1):
                p1, p2 = points[i], points[i + 1]
                x_start = 4 + int(i * step_x)
                x_end = 4 + int((i + 1) * step_x)
                y1 = graph_height - int(p1 / max_usage * graph_height) + 10
                y2 = graph_height - int(p2 / max_usage * graph_height) + 10

                for x in range(x_start, x_end):
                    progress = (x - x_start) / (x_end - x_start) if x_end > x_start else 0.0
                    y_top = int(y1 + (y2 - y1) * progress)
                    base_y = graph_height + 10
                    fill_h = base_y - y_top
                    if fill_h > 0:
                        for y_fill in range(y_top, base_y + 1):
                            t = (y_fill - y_top) / fill_h
                            g_col = int(255 * (1.0 - t * 0.85))
                            ctx.pixel(x, y_fill, fill=(0, g_col, 0))
                    ctx.pixel(x, y_top, fill=(0, 255, 0))

        usage_text = f"CPU {self.cpu_usage:.0f}%"
        ctx.center_text(usage_text, y=graph_height + 12, color="white")


# The User sets up the board
pad = DisplayPad()

image = PIL.open("examples/assets/initial_screen.png")
# Scale image to fit 800x240 if needed
image = image.resize((800, 240))
pad.image_buffer.paste(image, (0, 0))

pad.push_image()

time.sleep(2)

pad.image_buffer = PIL.new("RGB", (800, 240))

pad[0] = LoggerKey(0)
pad[1] = HoldButton(1)
pad[2] = MuteButton(2)
pad[3] = CPUUsageKey(3)
pad[4] = IconKey(PIL.open("examples/assets/heart.png"))
pad[5] = GifKey("examples/assets/coin.gif")
        
initial_screen_path = os.path.join(os.path.dirname(__file__), 'assets/initial_screen.png')

try:
    while True:
        pad.update(20)
except KeyboardInterrupt:
    pass
except Exception as e:
    logging.error(f"Error in main loop: {e}")
finally:
    if os.path.exists(initial_screen_path):
        pad.push_image(initial_screen_path)
    pad.disable()