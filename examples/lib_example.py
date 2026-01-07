from displaypad_lib import DisplayPad, Key
from displaypad_lib.key import FramerateLimitedKey, LoggerKey, IconKey
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
        # Draw the graph
        graph_width = 133
        graph_height = 80  # Adjusted height to move the graph higher
        max_usage = 100
        for i in range(len(self.cpu_usage_history) - 1):
            x1 = i * (graph_width // len(self.cpu_usage_history))
            y1 = graph_height - (self.cpu_usage_history[i] / max_usage * graph_height)
            x2 = (i + 1) * (graph_width // len(self.cpu_usage_history))
            y2 = graph_height - (self.cpu_usage_history[i + 1] / max_usage * graph_height)
            ctx.line(x1, y1, x2, y2, color="green", width=2)
        # Draw the current usage text
        usage_text = f"CPU: {self.cpu_usage:.1f}%"
        ctx.text(10, graph_height + 15, usage_text, color="white")  # Adjusted text position

# The User sets up the board
pad = DisplayPad()

pad[0] = LoggerKey(0)
pad[1] = HoldButton(1)
pad[2] = MuteButton(2)
pad[3] = CPUUsageKey(3)
pad[4] = IconKey(PIL.open("examples/assets/heart.png"))
        
while True:
    try:
        pad.update(100)
    except KeyboardInterrupt:
        break
    except Exception as e:
        logging.error(f"Error in main loop: {e}")

pad.disable()