import PIL.ImageDraw as ImageDraw
from PIL import Image, ImageFont


def get_default_font(size: int = 18) -> ImageFont.ImageFont:
    """Load a crisp, bold system font (size 18pt by default) for high-density key displays."""
    font_paths = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    )
    for p in font_paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


class KeyContext:
    """A drawing context for a single key on the DisplayPad.
    
    Operates on an isolated per-key PIL Image surface (0, 0 top-left).
    Provides native access to PIL ImageDraw (`ctx.draw`) and per-key PIL Image (`ctx.image`),
    as well as layout and shape convenience helpers.
    Unrecognized method calls are forwarded directly to `self.draw`.
    """

    def __init__(
        self,
        pil_draw: ImageDraw.ImageDraw | None = None,
        x_offset: int = 0,
        y_offset: int = 0,
        font=None,
        image: Image.Image | None = None,
        width: int = 102,
        height: int = 102,
    ):
        self.width = width
        self.height = height
        self.ox = x_offset
        self.oy = y_offset
        self.image = image if image is not None else Image.new("RGB", (self.width, self.height), (0, 0, 0))
        self.draw = pil_draw if pil_draw is not None else ImageDraw.Draw(self.image)
        self.font = font or get_default_font(18)

    def set_font(self, font):
        self.font = font

    def text(self, x, y, text, fill="white", font=None, **kwargs):
        fill = kwargs.pop('color', fill)
        font = font or self.font
        self.draw.text((x, y), text, fill=fill, font=font, **kwargs)

    def rectangle(self, x, y, w, h, fill="red", **kwargs):
        fill = kwargs.pop('color', fill)
        x2 = x + w - 1 if w > 0 else x
        y2 = y + h - 1 if h > 0 else y
        self.draw.rectangle([x, y, x2, y2], fill=fill, **kwargs)

    def rounded_rectangle(self, x, y, w, h, radius=10, fill="red", **kwargs):
        fill = kwargs.pop('color', fill)
        x2 = x + w - 1 if w > 0 else x
        y2 = y + h - 1 if h > 0 else y
        self.draw.rounded_rectangle([x, y, x2, y2], radius=radius, fill=fill, **kwargs)

    def ellipse(self, x, y, w, h, fill="red", **kwargs):
        fill = kwargs.pop('color', fill)
        x2 = x + w - 1 if w > 0 else x
        y2 = y + h - 1 if h > 0 else y
        self.draw.ellipse([x, y, x2, y2], fill=fill, **kwargs)

    def line(self, x1, y1, x2, y2, fill="red", width=1, **kwargs):
        fill = kwargs.pop('color', fill)
        self.draw.line([x1, y1, x2, y2], fill=fill, width=width, **kwargs)

    def polygon(self, points, fill="red", **kwargs):
        fill = kwargs.pop('color', fill)
        self.draw.polygon(points, fill=fill, **kwargs)

    def pixel(self, x, y, fill="red", **kwargs):
        fill = kwargs.pop('color', fill)
        self.draw.point((x, y), fill=fill, **kwargs)

    def point(self, x, y, fill="red", **kwargs):
        fill = kwargs.pop('color', fill)
        self.draw.point((x, y), fill=fill, **kwargs)

    def arc(self, x1, y1, x2, y2, start, end, fill="red", width=1, **kwargs):
        fill = kwargs.pop('color', fill)
        self.draw.arc([x1, y1, x2, y2], start, end, fill=fill, width=width, **kwargs)

    def paste_image(self, pil_image: Image.Image, x=0, y=0):
        """Paste an image onto this key's surface."""
        if self.image is None:
            raise ValueError("KeyContext needs a base image to paste onto")
        src = pil_image.convert("RGBA")
        alpha = src.getchannel("A") if "A" in src.getbands() else None
        rgb = src.convert("RGB")
        self.image.paste(rgb, (x, y), mask=alpha)

    def center_text(self, text, y=None, fill="white", font=None, **kwargs):
        fill = kwargs.pop('color', fill)
        font = font or self.font
        bbox = self.draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (self.width - w) // 2 - bbox[0]
        calc_y = ((self.height - h) // 2 - bbox[1]) if y is None else (y - bbox[1])
        self.text(x, calc_y, text, fill=fill, font=font, **kwargs)

    def fill(self, fill="black", **kwargs):
        fill = kwargs.pop('color', fill)
        self.rectangle(0, 0, self.width, self.height, fill=fill, **kwargs)

    def clear(self):
        self.fill("black")

    def apply_alpha_mask(self, alpha_mask: Image.Image):
        """Apply an alpha mask to the key's image surface."""
        if self.image is None:
            raise ValueError("KeyContext needs a base image to apply alpha mask onto")
        if alpha_mask.size != (self.width, self.height):
            alpha_mask = alpha_mask.resize((self.width, self.height))
        key_area = self.image.convert("RGBA")
        key_area.putalpha(alpha_mask)
        self.image.paste(key_area, (0, 0))

    def textbbox(self, text, font=None, **kwargs):
        font = font or self.font
        return self.draw.textbbox((0, 0), text, font=font, **kwargs)

    def __getattr__(self, name: str):
        """Forward any unrecognized ImageDraw method calls to self.draw."""
        if hasattr(self.draw, name):
            return getattr(self.draw, name)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")