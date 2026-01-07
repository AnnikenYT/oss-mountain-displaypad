"""Base Key class for DisplayPad keys, and some useful subclasses."""

from abc import ABC, abstractmethod
from .keycontext import KeyContext
from logging import getLogger

log = getLogger(__name__)

class Key(ABC):
    def __init__(self):
        # Users can store state here, e.g., self.is_muted = False
        self._needs_redraw = True

    def request_redraw(self):
        """Call this when state changes to trigger a screen update"""
        self._needs_redraw = True

    # --- Lifecycle Hooks ---

    def on_mount(self, index):
        """Called when the key is assigned to the board"""
        pass

    def on_press(self):
        """Called when the hardware reports a press"""
        pass

    def on_release(self):
        """Called when the hardware reports a release"""
        pass

    def on_tick(self):
        """Called every loop. Useful for animations (gifs/clocks).
        The frequency is by no means stable, If a poll ends early, the next tick will be sooner.
        For more stable timing, consider using FramerateLimitedKey."""
        pass

    @abstractmethod
    def render(self, ctx: KeyContext):
        """
        draw_context: A wrapper around PIL ImageDraw 
        (or similar) tied to this key's coordinates.
        """
        pass
    
class FramerateLimitedKey(Key):
    """A Key that requests redraws at a limited framerate."""
    def __init__(self, fps=10):
        super().__init__()
        self.fps = fps
        self._last_render_time = 0

    def on_tick(self):
        import time
        current_time = time.time()
        if current_time - self._last_render_time >= 1 / self.fps:
            self.request_redraw()
            self._last_render_time = current_time
            
class LoggerKey(Key):
    """A Key that logs presses and releases"""
    
    def __init__(self, idx):
        super().__init__()
        self.idx = idx
        
    def on_press(self):
        log.info(f"Key {self.idx} Pressed!")
    
    def on_release(self):
        log.info(f"Key {self.idx} Released!")

    def render(self, ctx):
        ctx.fill("blue")
        ctx.center_text(f"LOG KEY {self.idx}", color="white")
        
class IconKey(Key):
    """A Key that displays a static icon image with optional margin and resizing."""
    
    def __init__(self, pil_image, margin=10):
        super().__init__()
        self.pil_image = pil_image
        self.margin = margin

    def render(self, ctx):
        ctx.fill("black")
        # Calculate available space considering the margin
        available_width = ctx.width - 2 * self.margin
        available_height = ctx.height - 2 * self.margin

        # Resize the image to fit within the available space
        iw, ih = self.pil_image.size
        aspect_ratio = iw / ih
        if iw > available_width or ih > available_height:
            if aspect_ratio > 1:
                # Width is the limiting factor
                iw = available_width
                ih = int(iw / aspect_ratio)
            else:
                # Height is the limiting factor
                ih = available_height
                iw = int(ih * aspect_ratio)
            self.pil_image = self.pil_image.resize((iw, ih))

        # Center the image within the available space
        x = self.margin + (available_width - iw) // 2
        y = self.margin + (available_height - ih) // 2
        ctx.paste_image(self.pil_image, x, y)