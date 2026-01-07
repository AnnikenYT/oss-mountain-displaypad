from abc import ABC, abstractmethod

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
        """Called every loop. Useful for animations (gifs/clocks)"""
        pass

    @abstractmethod
    def render(self, draw_context):
        """
        draw_context: A wrapper around PIL ImageDraw 
        (or similar) tied to this key's coordinates.
        """
        pass