"""Multi-page layout management and page auto-timeout engine for DisplayPad."""

import time
from typing import Dict, List, Optional, Union
from .key import Key


class Page:
    """Represents a single 12-key page layout with optional auto-timeout behavior."""

    def __init__(self, name: str = "Main",
                 timeout_mode: str = "off",
                 timeout_seconds: int = 10,
                 timeout_target: Union[str, int] = "prev"):
        self.name = name
        self.keys: List[Optional[Key]] = [None] * 12
        self.timeout_mode = timeout_mode  # "off", "after", "idle"
        self.timeout_seconds = timeout_seconds
        self.timeout_target = timeout_target

    def __getitem__(self, index: int) -> Optional[Key]:
        if 0 <= index < 12:
            return self.keys[index]
        raise IndexError(f"Key index {index} out of range (0..11)")

    def __setitem__(self, index: int, key_instance: Optional[Key]):
        if 0 <= index < 12:
            self.keys[index] = key_instance
            if key_instance is not None:
                key_instance.on_mount(index)
                key_instance.request_redraw()
        else:
            raise IndexError(f"Key index {index} out of range (0..11)")


class PageManager:
    """Manages page registration, active page switching, and auto-timeout transitions."""

    def __init__(self, main_page: Optional[Page] = None):
        self.pages: Dict[Union[str, int], Page] = {}
        self.current_page_id: Union[str, int] = "Main"
        self.previous_page_id: Union[str, int] = "Main"

        self.last_switch_time: float = time.time()
        self.last_activity_time: float = time.time()

        default_main = main_page or Page(name="Main")
        self.add_page("Main", default_main)

    def add_page(self, page_id: Union[str, int], page: Page):
        self.pages[page_id] = page
        if page.name and page.name not in self.pages:
            self.pages[page.name] = page

    def get_current_page(self) -> Page:
        return self.pages.get(self.current_page_id) or self.pages.get("Main") or list(self.pages.values())[0]

    def switch_to(self, page_id: Union[str, int]) -> bool:
        if page_id not in self.pages:
            return False

        if page_id == self.current_page_id:
            return True

        self.previous_page_id = self.current_page_id
        self.current_page_id = page_id
        now = time.time()
        self.last_switch_time = now
        self.last_activity_time = now

        current_page = self.get_current_page()
        for idx, key in enumerate(current_page.keys):
            if key:
                key.request_redraw()

        return True

    def back(self) -> bool:
        return self.switch_to(self.previous_page_id)

    def note_activity(self):
        """Reset the inactivity timer for 'idle' mode timeouts."""
        self.last_activity_time = time.time()

    def check_timeout(self) -> Optional[Union[str, int]]:
        """Check if current page timeout condition has expired.

        Returns target page_id to switch to, or None.
        """
        page = self.get_current_page()
        if not page or page.timeout_mode == "off" or page.timeout_seconds <= 0:
            return None

        now = time.time()
        target = page.timeout_target
        if target == "prev":
            resolved_target = self.previous_page_id
        else:
            resolved_target = target

        if resolved_target == self.current_page_id:
            return None

        if page.timeout_mode == "after":
            if now - self.last_switch_time >= page.timeout_seconds:
                return resolved_target
        elif page.timeout_mode == "idle":
            if now - self.last_activity_time >= page.timeout_seconds:
                return resolved_target

        return None
