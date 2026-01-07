from displaypad_lib import DisplayPad, Key
import logging
import random

logging.basicConfig(level=logging.INFO)


class LoggerKey(Key):
    def __init__(self, idx):
        super().__init__()
        self.idx = idx
        
    def on_press(self):
        logging.info(f"Key {self.idx} Pressed!")
    
    def on_release(self):
        logging.info(f"Key {self.idx} Released!")

    def render(self, ctx):
        ctx.rectangle(0, 0, 133, 120, color="blue")
        ctx.text(10, 50, f"LOG KEY {self.idx}", color="white")

# The User defines a reusable component
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

# The User sets up the board
pad = DisplayPad()


for i in range(12):
    pad[i] = MuteButton(i)

while True:
    try:
        pad.update()
    except KeyboardInterrupt:
        break
    except Exception as e:
        logging.error(f"Error in main loop: {e}")

pad.disable()