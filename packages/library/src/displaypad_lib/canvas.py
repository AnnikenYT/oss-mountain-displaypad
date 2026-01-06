"""
Docstring for displaypad.canvas
The Canvas provides a drawing surface for the DisplayPad buttons.
Its main purpose is to assemble images for the proper display on the buttons.
"""

from .icon import Icon
from PIL import Image

class Canvas:
    """
    Canvas class for DisplayPad buttons.
    """
    
    def __init__(self, displaypad, width: int = 800, height: int = 240):
        self.displaypad = displaypad
        self.width = width
        self.height = height
        self.pixels = [[(0, 0, 0) for _ in range(width)] for _ in range(height)]
        # Track whether the in-memory canvas differs from what has been sent to the device
        self.dirty = True
        
    def draw_icon(self, icon: Icon, position: tuple):
        """Draw an Icon onto the Canvas at the specified position (x, y)."""
        icon_pixels = icon.get_image_pixels()
        icon_width, icon_height = Icon.size

        x_offset, y_offset = position

        # Any draw operation means we need to push pixels to the device again
        self.dirty = True

        for y in range(icon_height):
            row = icon_pixels[y]
            for x in range(icon_width):
                pixel = row[x]
                # pixel may be an int (grayscale), an (R,G,B) tuple, or (R,G,B,A)
                if isinstance(pixel, tuple):
                    r, g, b = pixel[0], pixel[1], pixel[2]
                else:
                    # grayscale value
                    r = g = b = int(pixel)

                canvas_x = x_offset + x
                canvas_y = y_offset + y

                if 0 <= canvas_x < self.width and 0 <= canvas_y < self.height:
                    self.pixels[canvas_y][canvas_x] = (r, g, b)
                            
    def draw_button(self, button_id: int, icon: Icon):
        """Draw an Icon onto the Canvas at the position corresponding to the button ID."""
        if button_id < 0 or button_id > 11:
            raise ValueError("Button ID must be between 0 and 11")
        
        x = (button_id % 6) * Icon.size[0]
        y = (button_id // 6) * Icon.size[1]
        
        self.draw_icon(icon, (x, y))
        
    def export(self, filepath: str):
        """Export the current canvas to an image file."""        
        img = Image.new('RGB', (self.width, self.height))
        for y in range(self.height):
            for x in range(self.width):
                img.putpixel((x, y), self.pixels[y][x])
        
        # Save the image as png
        img.save(filepath, format='PNG')