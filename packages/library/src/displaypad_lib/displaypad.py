from PIL import Image, ImageDraw
from .key import Key
from .keycontext import KeyContext
from displaypad_driver import DisplayPad as Driver
from logging import getLogger

log = getLogger(__name__)

class DisplayPad:
    def __init__(self):
        self.driver = Driver()
        self.keys = [None] * 12  # The 2x6 grid
        self.width = 800
        self.height = 240
        self.image_buffer = Image.new("RGB", (self.width, self.height))
        self.running = False

    def __setitem__(self, index, key_instance):
        """Allows syntax: pad[0] = MyCustomKey()"""
        if 0 <= index < 12:
            self.keys[index] = key_instance
            key_instance.on_mount(index)
            key_instance.request_redraw()
            
    def disable(self):
        self.driver.enable(False)

    def _get_key_coords(self, index):
        # Calculate x, y, width, height for index 0-11
        # 6 columns, 2 rows. 
        # width approx 133px, height 120px
        row = index // 6
        col = index % 6
        w = self.width // 6
        h = self.height // 2
        return (col * w, row * h)
    
    def screenshot(self, filename):
        """Save current buffer to a file for debugging"""
        self.image_buffer.save(filename)

    def update(self, timeout=500):
        """The Main Loop"""
        # 1. Poll Driver
        input_state = self.driver.poll_key(timeout)
        # input_state e.g., {'pressed': [0], 'released': [1], 'held': [0]}

        global_dirty = False

        # 2. Dispatch Input Events
        for idx in input_state['pressed']:
            if self.keys[idx]: self.keys[idx].on_press()
        
        for idx in input_state['released']:
            if self.keys[idx]: self.keys[idx].on_release()

        # 3. Render Pass
        for i, key in enumerate(self.keys):
            if key:
                # Optional: Call on_tick for animations
                key.on_tick()
                
                if key._needs_redraw:
                    # Create a drawing context for this specific area
                    x, y = self._get_key_coords(i)
                    # Create a crop or strictly bounded draw interface
                    # For simplicity, we can pass the global draw and offset
                    draw = ImageDraw.Draw(self.image_buffer)
                    
                    # We pass a custom context that handles the offset automatically
                    ctx = KeyContext(draw, x_offset=x, y_offset=y, image=self.image_buffer)
                    key.render(ctx)
                    
                    key._needs_redraw = False
                    global_dirty = True

        # 4. Push to Device
        if global_dirty:
            r, g, b, = self.image_buffer.split()
            bgr_image = Image.merge("RGB", (b, g, r))
            
            img_data = bgr_image.tobytes()
            try:
                self.driver.set_panel_image(img_data)
            except Exception as e:
                log.error(f"Failed to update display: {e}")