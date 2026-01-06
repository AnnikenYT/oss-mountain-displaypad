from .button import Button
from .canvas import Canvas
from displaypad_driver import DisplayPad as DPDriver
import logging

log = logging.getLogger(__name__)

class DisplayPad:
    def __init__(self):
        self.dp = DPDriver(0x3282, 0x0009)
        self.canvas = Canvas(self)
        self.buttons = [Button(i, canvas=self.canvas) for i in range(12)]
        
    def __enter__(self):
        self.dp.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.dp.__exit__(exc_type, exc_value, traceback)
        
    def draw(self):
        imgdata = []
        for row in self.canvas.pixels:
            for pixel in row:
                imgdata.append(pixel)
                
        self.dp.set_panel_image(imgdata=imgdata)
        
    def update(self):
        
        try:
            self.draw()
        except Exception as e:
            log.warning('DisplayPad update draw failed: %s', e)
        
        try:
            key_events = self.dp.poll_key()
        except Exception as e:
            log.debug('DisplayPad update poll_key failed: %s', e)
            return {'pressed': [], 'released': [], 'current': []}
            
        for key_id in key_events['pressed']:
            self.buttons[key_id].trigger_down()
            
        for key_id in key_events['released']:
            self.buttons[key_id].trigger_up()
            
        
        return key_events