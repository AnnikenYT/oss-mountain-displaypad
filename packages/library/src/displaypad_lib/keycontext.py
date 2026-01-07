import PIL.ImageDraw as ImageDraw
from PIL import Image, ImageFont

class KeyContext:
    width = 800 // 6
    height = 240 // 2
    
    def __init__(self, pil_draw: ImageDraw.ImageDraw, x_offset, y_offset, font=None, image: Image.Image | None = None):
        self.draw = pil_draw
        self.ox = x_offset
        self.oy = y_offset
        self.font = font or ImageFont.load_default()
        self.image = image

    def set_font(self, font):
        self.font = font

    def text(self, x, y, text, color="white", font=None):
        font = font or self.font
        self.draw.text((self.ox + x, self.oy + y), text, fill=color, font=font)

    def rectangle(self, x, y, w, h, color="red"):
        self.draw.rectangle(
            [self.ox + x, self.oy + y, self.ox + x + w, self.oy + y + h], 
            fill=color
        )
        
    def ellipse(self, x, y, w, h, color="red"):
        self.draw.ellipse(
            [self.ox + x, self.oy + y, self.ox + x + w, self.oy + y + h], 
            fill=color
        )
        
    def line(self, x1, y1, x2, y2, color="red", width=1):
        self.draw.line(
            [self.ox + x1, self.oy + y1, self.ox + x2, self.oy + y2],
            fill=color,
            width=width
        )

    def paste_image(self, pil_image: Image.Image, x=0, y=0):
        """Paste an image into the key bounds, clipping to this key's area."""
        if self.image is None:
            raise ValueError("KeyContext needs a base image to paste onto")

        src = pil_image.convert("RGBA")

        dest_left = self.ox + x
        dest_top = self.oy + y
        dest_right = dest_left + src.width
        dest_bottom = dest_top + src.height

        key_left, key_top = self.ox, self.oy
        key_right, key_bottom = self.ox + self.width, self.oy + self.height

        clip_left = max(dest_left, key_left)
        clip_top = max(dest_top, key_top)
        clip_right = min(dest_right, key_right)
        clip_bottom = min(dest_bottom, key_bottom)

        if clip_left >= clip_right or clip_top >= clip_bottom:
            return

        crop_left = clip_left - dest_left
        crop_top = clip_top - dest_top
        cropped = src.crop((crop_left, crop_top, crop_left + (clip_right - clip_left), crop_top + (clip_bottom - clip_top)))

        alpha = cropped.getchannel("A") if "A" in cropped.getbands() else None
        rgb = cropped.convert("RGB")
        self.image.paste(rgb, (clip_left, clip_top), mask=alpha)
        
    # Layout helpers
    def center_text(self, text, color="white", font=None):
        font = font or self.font
        # bbox: (left, top, right, bottom)
        _, _, w, h = self.draw.textbbox((0, 0), text, font=font)
        x = (self.width - w) // 2
        y = (self.height - h) // 2
        self.text(x, y, text, color, font=font)
        
    def fill(self, color="black"):
        self.rectangle(0, 0, self.width, self.height, color)
        
    def clear(self):
        self.fill("black")