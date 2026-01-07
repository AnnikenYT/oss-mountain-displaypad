class KeyContext:
    def __init__(self, pil_draw, x_offset, y_offset):
        self.draw = pil_draw
        self.ox = x_offset
        self.oy = y_offset

    def text(self, x, y, text, color="white"):
        # Automatically adds the key's offset
        self.draw.text((self.ox + x, self.oy + y), text, fill=color)

    def rectangle(self, x, y, w, h, color="red"):
        self.draw.rectangle(
            [self.ox + x, self.oy + y, self.ox + x + w, self.oy + y + h], 
            fill=color
        )
        
    # Add helper methods for images, icons, etc.