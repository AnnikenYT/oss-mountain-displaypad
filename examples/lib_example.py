from displaypad_lib import DisplayPad, Key
import logging
import time

logging.basicConfig(level=logging.INFO)

# The User defines a reusable component
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

# The User sets up the board
pad = DisplayPad()


pad[0] = LoggerKey(0)
pad[1] = HoldButton(1)
pad[2] = MuteButton(2)

while True:
    try:
        pad.update()
    except KeyboardInterrupt:
        break
    except Exception as e:
        logging.error(f"Error in main loop: {e}")

pad.disable()