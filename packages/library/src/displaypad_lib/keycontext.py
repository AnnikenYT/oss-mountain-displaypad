import PIL.ImageDraw as ImageDraw
from PIL import Image, ImageFont


class KeyContext:
    """A drawing context for a single key on the DisplayPad.
    Automatically offsets drawing commands to the key's position.
    Provides helper methods for common drawing tasks."""
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

    def text(self, x, y, text, fill="white", font=None, **kwargs):
        font = font or self.font
        self.draw.text((self.ox + x, self.oy + y), text,
                       fill=fill, font=font, **kwargs)

    def rectangle(self, x, y, w, h, fill="red", **kwargs):
        self.draw.rectangle(
            [self.ox + x, self.oy + y, self.ox + x + w, self.oy + y + h],
            fill=fill,
            **kwargs
        )

    def ellipse(self, x, y, w, h, fill="red", **kwargs):
        self.draw.ellipse(
            [self.ox + x, self.oy + y, self.ox + x + w, self.oy + y + h],
            fill=fill,
            **kwargs
        )

    def line(self, x1, y1, x2, y2, fill="red", width=1, **kwargs):
        self.draw.line(
            [self.ox + x1, self.oy + y1, self.ox + x2, self.oy + y2],
            fill=fill,
            width=width,
            **kwargs
        )

    def polygon(self, points, fill="red", **kwargs):
        offset_points = [(self.ox + x, self.oy + y) for (x, y) in points]
        self.draw.polygon(offset_points, fill=fill, **kwargs)

    def pixel(self, x, y, fill="red", **kwargs):
        self.draw.point((self.ox + x, self.oy + y), fill=fill, **kwargs)
        
    def point(self, x, y, fill="red", **kwargs):
        self.draw.point((self.ox + x, self.oy + y), fill=fill, **kwargs)

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
        cropped = src.crop((crop_left, crop_top, crop_left +
                           (clip_right - clip_left), crop_top + (clip_bottom - clip_top)))

        alpha = cropped.getchannel("A") if "A" in cropped.getbands() else None
        rgb = cropped.convert("RGB")
        self.image.paste(rgb, (clip_left, clip_top), mask=alpha)

    def arc(self, x1, y1, x2, y2, start, end, fill="red", width=1, **kwargs):
        self.draw.arc(
            [self.ox + x1, self.oy + y1, self.ox + x2, self.oy + y2],
            start,
            end,
            fill=fill,
            width=width, **kwargs
        )

    # Layout helpers
    def center_text(self, text, y=None, fill="white", font=None):
        font = font or self.font
        # bbox: (left, top, right, bottom)
        _, _, w, h = self.draw.textbbox((0, 0), text, font=font)
        x = (self.width - w) // 2
        y = (self.height - h) // 2 if y is None else y
        self.text(x, y, text, fill=fill, font=font)

    def fill(self, fill="black", **kwargs):
        self.rectangle(0, 0, self.width, self.height, fill=fill, **kwargs)
        
    

    def clear(self):
        self.fill("black")

    def apply_alpha_mask(self, alpha_mask: Image.Image):
        """Apply an alpha mask to the key's image area."""
        if self.image is None:
            raise ValueError(
                "KeyContext needs a base image to apply alpha mask onto")

        # Support both key-sized masks and full-panel masks.
        if alpha_mask.size == (self.width, self.height):
            mask_cropped = alpha_mask
        elif alpha_mask.size == self.image.size:
            mask_cropped = alpha_mask.crop(
                (self.ox, self.oy, self.ox + self.width, self.oy + self.height))
        else:
            # Fallback: resize to key area
            mask_cropped = alpha_mask.resize((self.width, self.height))

        key_area = self.image.crop(
            (self.ox, self.oy, self.ox + self.width, self.oy + self.height)).convert("RGBA")
        key_area.putalpha(mask_cropped)
        self.image.paste(key_area, (self.ox, self.oy))

    def textbbox(self, text, font=None, **kwargs):
        font = font or self.font
        return self.draw.textbbox((0, 0), text, font=font, **kwargs)