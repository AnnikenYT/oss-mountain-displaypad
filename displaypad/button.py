
from .icon import Icon

class Button:
    
    def __init__(self, id, canvas, icon: Icon = None):
        # ID of the button (0-11)
        if id < 0 or id > 11:
            raise ValueError("Button ID must be between 0 and 11")
        
        # Canvas must be provided
        if canvas is None:
            raise ValueError("Canvas must be provided for Button")
        
        self.id = id
        self.pressed = False
        self.icon = icon
        self.canvas = canvas
        self._down_callbacks = []
        self._up_callbacks = []
        
    def set_icon(self, icon: Icon):
        self.icon = icon
        if self.icon:
            self.canvas.draw_button(self.id, self.icon)
        
    def on_down(self, callback):
        self._down_callbacks.append(callback)
        
    def on_up(self, callback):
        self._up_callbacks.append(callback)
        
    def trigger_down(self):
        self.pressed = True
        for callback in self._down_callbacks:
            callback(self)
            
    def trigger_up(self):
        self.pressed = False
        for callback in self._up_callbacks:
            callback(self)