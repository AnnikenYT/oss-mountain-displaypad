"""Base Key class for DisplayPad keys, and specialized key implementations."""

import time
from abc import ABC, abstractmethod
from typing import Optional, Union, List, Tuple
from PIL import Image, ImageFont

from .keycontext import KeyContext, get_default_font
from logging import getLogger


log = getLogger(__name__)


class Key(ABC):
    """Base abstract class for a DisplayPad key.

    Subclass this and override `render(ctx)` and lifecycle hooks like `on_press()`.
    """

    def __init__(self):
        self._needs_redraw = True
        self.index: Optional[int] = None

    def request_redraw(self):
        """Call this when state changes to trigger a screen update."""
        self._needs_redraw = True

    # --- Lifecycle Hooks ---

    def on_mount(self, index: int):
        """Called when the key is assigned to a board slot (0..11)."""
        self.index = index

    def on_press(self):
        """Called when the key is pressed down."""
        pass

    def on_release(self):
        """Called when the key is released."""
        pass

    def on_double_press(self):
        """Called when the key is double-tapped within the double-click window."""
        pass

    def on_long_press(self):
        """Called when the key is held down longer than long-press duration."""
        pass

    def on_tick(self):
        """Called every polling iteration. Useful for animations and timer checks."""
        pass

    @abstractmethod
    def render(self, ctx: KeyContext):
        """Render the key contents into the provided KeyContext."""
        pass


class FramerateLimitedKey(Key):
    """A Key that limits redraw requests to a target frame rate (fps)."""

    def __init__(self, fps: float = 10.0):
        super().__init__()
        self.fps = fps
        self._last_render_time = 0.0

    def on_tick(self):
        current_time = time.time()
        if current_time - self._last_render_time >= 1.0 / self.fps:
            self.request_redraw()
            self._last_render_time = current_time


class LoggerKey(Key):
    """A Key that logs presses and releases."""

    def __init__(self, idx: int = 0):
        super().__init__()
        self.idx = idx

    def on_press(self):
        log.info(f"Key {self.idx} Pressed!")

    def on_release(self):
        log.info(f"Key {self.idx} Released!")

    def render(self, ctx: KeyContext):
        ctx.fill("blue")
        ctx.center_text(f"LOG KEY {self.idx}", color="white")


class IconKey(Key):
    """A Key that displays a static icon image (PIL Image or file path)."""

    def __init__(self, image_or_path: Union[str, Image.Image], margin: int = 10):
        super().__init__()
        if isinstance(image_or_path, str):
            self.pil_image = Image.open(image_or_path).convert("RGBA")
        else:
            self.pil_image = image_or_path.convert("RGBA")
        self.margin = margin

    def render(self, ctx: KeyContext):
        ctx.clear()
        available_width = ctx.width - 2 * self.margin
        available_height = ctx.height - 2 * self.margin

        iw, ih = self.pil_image.size
        aspect_ratio = iw / ih if ih > 0 else 1.0

        if iw > available_width or ih > available_height:
            if aspect_ratio > 1:
                iw = available_width
                ih = int(iw / aspect_ratio)
            else:
                ih = available_height
                iw = int(ih * aspect_ratio)
            resized = self.pil_image.resize((max(1, iw), max(1, ih)), Image.LANCZOS)
        else:
            resized = self.pil_image

        x = self.margin + (available_width - iw) // 2
        y = self.margin + (available_height - ih) // 2
        ctx.paste_image(resized, x, y)


class GifKey(Key):
    """A Key that plays an animated GIF at its native frame rate."""

    def __init__(self, gif_path_or_image: Union[str, Image.Image], rotation: int = 0):
        super().__init__()
        self.rotation = rotation
        self.frames: List[Tuple[Image.Image, float]] = []  # (frame_image, duration_seconds)
        self.current_frame_idx = 0
        self.last_frame_time = time.time()
        self.is_playing = True

        self._load_gif(gif_path_or_image)

    def _load_gif(self, src: Union[str, Image.Image]):
        img = Image.open(src) if isinstance(src, str) else src.copy()
        if not getattr(img, 'is_animated', False) and getattr(img, 'n_frames', 1) <= 1:
            frame = img.convert("RGBA").resize((133, 120), Image.LANCZOS)
            if self.rotation:
                frame = frame.rotate(-self.rotation, expand=False)
            self.frames = [(frame, 1.0)]
            return

        try:
            for i in range(img.n_frames):
                img.seek(i)
                duration = max(img.info.get('duration', 100), 20) / 1000.0
                frame = img.convert("RGBA").resize((133, 120), Image.LANCZOS)
                if self.rotation:
                    frame = frame.rotate(-self.rotation, expand=False)
                self.frames.append((frame, duration))
        except EOFError:
            pass

    def on_tick(self):
        if not self.is_playing or not self.frames:
            return

        now = time.time()
        _frame_img, duration = self.frames[self.current_frame_idx]
        if now - self.last_frame_time >= duration:
            self.current_frame_idx = (self.current_frame_idx + 1) % len(self.frames)
            self.last_frame_time = now
            self.request_redraw()

    def render(self, ctx: KeyContext):
        ctx.clear()
        if not self.frames:
            return
        frame_img, _ = self.frames[self.current_frame_idx]
        ctx.paste_image(frame_img, 0, 0)


class LabelKey(Key):
    """A Key that displays a simple text label with background color."""

    def __init__(self, label: str, bg_color: str = "navy", text_color: str = "white", font_size: int = 18):
        super().__init__()
        self.label = label
        self.bg_color = bg_color
        self.text_color = text_color
        self.font_size = font_size
        self._custom_font = None

    def render(self, ctx: KeyContext):
        ctx.fill(self.bg_color)
        font = self._custom_font or get_default_font(self.font_size)
        ctx.center_text(self.label, color=self.text_color, font=font)