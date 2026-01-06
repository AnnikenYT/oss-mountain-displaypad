# An Icon can be assigned to a Button to display an image on it.
# It holds an Image, and text can be overlaid on the icon.
# It also holds the logic to convert the Image to bytes for sending to the device.
# Icon size: 120x120 pixels

import PIL
from PIL import ImageDraw, ImageFont
import os


fontpath = os.path.join(os.path.dirname(__file__), './assets/arial.ttf')

class Icon:
    size = (133, 120)
    
    def __init__(self, image: PIL.Image.Image = None, image_path: str = None):
        if image_path:
            self.image = PIL.Image.open(image_path).convert('RGB')
            self.source_image
        else:
            if image is None:
                raise ValueError("Either image or image_path must be provided")
            self.image = image
            self.source_image = image
            
        self.label = {
            'content': '',
            'font_size': 12,
            'color': (255, 255, 255),
            'position': (0, 0)
        }
    
    def positioned(self, x: str, y: str):
        """Set label position using keywords: 'left', 'center', 'right' for x and 'top', 'center', 'bottom' for y."""
        if x == 'left':
            pos_x = 0
        elif x == 'center':
            pos_x = (self.size[0] - self.label['font_size'] * len(self.label['content']) // 2) // 2
        elif x == 'right':
            pos_x = self.size[0] - self.label['font_size'] * len(self.label['content'])
        else:
            raise ValueError("x must be 'left', 'center', or 'right'")
        
        if y == 'top':
            pos_y = 0
        elif y == 'center':
            pos_y = (self.size[1] - self.label['font_size']) // 2
        elif y == 'bottom':
            pos_y = self.size[1] - self.label['font_size']
        else:
            raise ValueError("y must be 'top', 'center', or 'bottom'")
        
        return (pos_x, pos_y)
        
    def set_label(self, content: str, font_size: int = 20, color: tuple = (255, 255, 255), position: tuple = (0, 0)):
        self.label['content'] = content
        self.label['font_size'] = font_size
        self.label['color'] = color
        # if position is a string tuple, convert to coordinates
        if isinstance(position, tuple) and len(position) == 2 and all(isinstance(p, str) for p in position):
            position = self.positioned(position[0], position[1])
        self.label['position'] = position
        # Update image with label
        self.image = self.source_image.copy()
        if self.label['content']:
            draw = ImageDraw.Draw(self.image)
            font = ImageFont.truetype(fontpath, self.label['font_size'])
            draw.text(self.label['position'], self.label['content'], font=font, fill=self.label['color'])
            
            
    def get_image_pixels(self) -> list:
        """Convert the icon image (with label) to a list of pixel tuples."""
        img = self.image.copy()
        
        # Resize if necessary
        img = img.resize(self.size)
        
        # Extract pixels as a list of tuples
        pixels = []
        for y in range(self.size[1]):
            row = []
            for x in range(self.size[0]):
                row.append(img.getpixel((x, y)))
            pixels.append(row)
        
        return pixels
    
    @staticmethod
    def fill_color(color: tuple):
        """Create an Icon filled with a solid color."""
        img = PIL.Image.new('RGB', Icon.size, color)
        return Icon(image=img)