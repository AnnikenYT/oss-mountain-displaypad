from .button import Button
from .canvas import Canvas
from displaypad_driver import DisplayPad as DPDriver
import logging
import time

log = logging.getLogger(__name__)

class DisplayPad:
    def __init__(self):
        self.dp = DPDriver(0x3282, 0x0009)
        self.canvas = Canvas(self)
        self.buttons = [Button(i, canvas=self.canvas) for i in range(12)]
        self._last_key_events = {'pressed': [], 'released': [], 'current': []}
        
    def __enter__(self):
        self.dp.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.dp.__exit__(exc_type, exc_value, traceback)
        
    def draw(self):
        # Skip USB traffic when nothing changed to avoid backpressure on key polling
        if not self.canvas.dirty:
            return

        imgdata = []
        for row in self.canvas.pixels:
            for pixel in row:
                imgdata.append(pixel)

        # Device can briefly reject image data while handling other USB traffic;
        # retry a couple times with a short pause before surfacing the error.
        last_error = None
        for _ in range(3):
            try:
                self.dp.set_panel_image(imgdata=imgdata)
                self.canvas.dirty = False
                return
            except Exception as e:
                last_error = e
                time.sleep(0.05)

        raise last_error
        
    def update(self):
        key_events = self._poll_keys_with_retry()
            
        for key_id in key_events['pressed']:
            self.buttons[key_id].trigger_down()
            
        for key_id in key_events['released']:
            self.buttons[key_id].trigger_up()
            
        try:
            self.draw()
        except Exception as e:
            log.warning('DisplayPad update draw failed: %s', e)

        # Fast taps can begin and end during a long draw; poll again afterward
        post_draw_events = self._poll_keys_with_retry()
        for key_id in post_draw_events['pressed']:
            self.buttons[key_id].trigger_down()
        for key_id in post_draw_events['released']:
            self.buttons[key_id].trigger_up()
        
        return {
            'pressed': key_events['pressed'] + post_draw_events['pressed'],
            'released': key_events['released'] + post_draw_events['released'],
            'current': post_draw_events.get('current', key_events.get('current', []))
        }

    def _poll_keys_with_retry(self):
        key_events = {'pressed': [], 'released': [], 'current': self._last_key_events.get('current', [])}

        for _ in range(3):
            try:
                key_events = self.dp.poll_key()
                break
            except Exception as e:
                log.debug('DisplayPad poll_key retrying after: %s', e)
                time.sleep(0.005)

        self._last_key_events = key_events
        return key_events