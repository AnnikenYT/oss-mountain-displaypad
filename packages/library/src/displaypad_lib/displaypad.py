from PIL import Image, ImageDraw
from .key import Key
from .keycontext import KeyContext
from displaypad_driver import DisplayPad as Driver
from logging import getLogger

log = getLogger(__name__)

class DisplayPad:
    """Main DisplayPad class managing keys, multi-page layouts, and async display rendering."""

import logging
import queue
import threading
import time
from typing import Dict, List, Optional, Union
from PIL import Image, ImageDraw

from displaypad_driver import DisplayPad as Driver, ICON_SIZE, KEYS_PER_ROW, NUM_KEYS
from displaypad_driver.image import image_to_bgr102, split_image_to_tiles
from .key import Key
from .keycontext import KeyContext
from .page import Page, PageManager

log = logging.getLogger(__name__)


class DisplayPad:
    """Main DisplayPad high-level manager class.

    Usage:
    ```python
    pad = DisplayPad()
    pad[0] = LoggerKey(0)
    while True:
        pad.update()
    ```
    """

    def __init__(self, rotation: int = 0, debounce_sec: float = 0.01, dc_window: float = 0.6):
        self.driver = Driver()
        self.width = 612
        self.height = 204
        self.rotation = rotation
        self.debounce_sec = debounce_sec
        self.dc_window = dc_window
        self.dc_antibounce = 0.02

        self.image_buffer = Image.new("RGB", (self.width, self.height))

        self.page_manager = PageManager()
        self._synced_keys: List[Optional[object]] = [object()] * NUM_KEYS
        self._key_down_state: List[bool] = [False] * NUM_KEYS

        # Input timing state
        self._last_fire_time: Dict[int, float] = {}
        self._press_start_time: Dict[int, float] = {}
        self._dc_timers: Dict[int, float] = {}  # key_index -> timer_start_time
        self._dc_pending_single: Dict[int, bool] = {}

        # Async tile render queue & lock
        self._render_queue: queue.Queue = queue.Queue()
        self._queue_worker_stop = threading.Event()
        self._worker_thread = threading.Thread(target=self._async_render_loop, daemon=True)
        self._worker_thread.start()

    # --- Property Shortcuts ---

    @property
    def keys(self) -> List[Optional[Key]]:
        return self.page_manager.get_current_page().keys

    def __getitem__(self, index: int) -> Optional[Key]:
        return self.page_manager.get_current_page()[index]

    def __setitem__(self, index: int, key_instance: Optional[Key]):
        self.page_manager.get_current_page()[index] = key_instance
        self._synced_keys[index] = object()  # Force re-sync on next update

    def add_page(self, page_id: Union[str, int], page: Page):
        """Register a new Page layout. If adding/updating the active page, repaints the panel."""
        self.page_manager.add_page(page_id, page)
        current = self.page_manager.current_page_id
        if page_id == current or page.name == current:
            # Force re-sync of active page keys
            self._synced_keys = [object()] * NUM_KEYS
            current_page = self.page_manager.get_current_page()
            draw = ImageDraw.Draw(self.image_buffer)
            draw.rectangle([0, 0, self.width, self.height], fill=(0, 0, 0))
            for idx in range(NUM_KEYS):
                key = current_page.keys[idx]
                if key:
                    key.on_mount(idx)
                    self._render_key_to_buffer(idx, key)
                    key._needs_redraw = False
            self.push_image()


    def switch_to_page(self, page_id: Union[str, int]) -> bool:
        """Switch active page and request full panel redraw."""
        success = self.page_manager.switch_to(page_id)
        if success:
            current_page = self.page_manager.get_current_page()
            # Render all keys of new page onto image_buffer
            draw = ImageDraw.Draw(self.image_buffer)
            draw.rectangle([0, 0, self.width, self.height], fill=(0, 0, 0))
            for idx in range(NUM_KEYS):
                key = current_page.keys[idx]
                if key:
                    self._render_key_to_buffer(idx, key)
                    key._needs_redraw = False
            self.push_image()
        return success

    def set_brightness(self, percent: int):
        """Set hardware backlight brightness (0-100%)."""
        self.driver.set_brightness(percent)

    def disable(self):
        """Close driver interfaces and stop worker threads."""
        self._queue_worker_stop.set()
        self.driver.close()

    def _get_key_box(self, index: int) -> tuple[int, int, int, int]:
        """Return (x1, y1, x2, y2) bounding box for key index in 800x240 buffer."""
        row = index // KEYS_PER_ROW
        col = index % KEYS_PER_ROW
        x1 = round(col * self.width / KEYS_PER_ROW)
        x2 = round((col + 1) * self.width / KEYS_PER_ROW)
        y1 = round(row * self.height / 2)
        y2 = round((row + 1) * self.height / 2)
        return (x1, y1, x2, y2)

    def _get_key_coords(self, index: int) -> tuple[int, int]:
        box = self._get_key_box(index)
        return (box[0], box[1])

    def clear(self):
        """Clear the full image buffer to black and update all key tiles on device."""
        self.image_buffer = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        current_page = self.page_manager.get_current_page()
        for idx in range(NUM_KEYS):
            current_page.keys[idx] = None
        self.push_image()

    def screenshot(self, filename: str):
        """Save current buffer to a file for debugging."""
        self.image_buffer.save(filename)

    def update(self, timeout: int = 20):
        """Poll driver for inputs, process key lifecycles, and update display.

        Args:
            timeout: Input polling timeout in milliseconds (default 20ms for high responsiveness).
        """
        now = time.time()

        # 1. Check page auto-timeouts
        timeout_target = self.page_manager.check_timeout()
        if timeout_target:
            self.switch_to_page(timeout_target)

        # 2. Poll Driver for key events
        input_state = self.driver.poll_key(timeout=timeout)

        # 3. Handle key presses
        if input_state['pressed']:
            self.page_manager.note_activity()
            for idx in input_state['pressed']:
                if not self._key_down_state[idx]:
                    self._key_down_state[idx] = True
                    self._last_fire_time[idx] = now
                    self._press_start_time[idx] = now

                    key = self[idx]
                    if key:
                        key.on_press()

                    # Double click check (additionally trigger on_double_press if within window)
                    if idx in self._dc_timers and (now - self._dc_timers[idx] <= self.dc_window):
                        del self._dc_timers[idx]
                        self._dc_pending_single[idx] = False
                        if key:
                            key.on_double_press()
                    else:
                        self._dc_timers[idx] = now
                        self._dc_pending_single[idx] = True

        # 4. Handle key releases
        if input_state['released']:
            for idx in input_state['released']:
                if self._key_down_state[idx]:
                    self._key_down_state[idx] = False
                    start_t = self._press_start_time.pop(idx, None)
                    if start_t and (now - start_t >= 0.8):
                        key = self[idx]
                        if key:
                            key.on_long_press()

                    key = self[idx]
                    if key:
                        key.on_release()
                else:
                    # Released without recorded down event (missed down poll on super fast tap)
                    self.page_manager.note_activity()
                    self._last_fire_time[idx] = now
                    key = self[idx]
                    if key:
                        key.on_press()
                        key.on_release()

        # 5. Handle pending single presses after double-click window elapses
        for idx in list(self._dc_timers.keys()):
            if now - self._dc_timers[idx] > self.dc_window:
                del self._dc_timers[idx]
                self._dc_pending_single.pop(idx, None)

        # 6. Render pass for current page keys
        current_page = self.page_manager.get_current_page()
        dirty_indices = []

        for idx in range(NUM_KEYS):
            key = current_page.keys[idx]
            if key is None:
                if self._synced_keys[idx] is not None:
                    # Clear this slot region to black on buffer
                    self._render_blank_key_to_buffer(idx)
                    dirty_indices.append(idx)
                    self._synced_keys[idx] = None
            else:
                if self._synced_keys[idx] is not key:
                    key._needs_redraw = True
                    self._synced_keys[idx] = key

                key.on_tick()
                if key._needs_redraw:
                    self._render_key_to_buffer(idx, key)
                    key._needs_redraw = False
                    dirty_indices.append(idx)

        # 7. Upload pass: if 3 or more keys are dirty, batch update the whole panel!
        if len(dirty_indices) >= 3:
            self.push_image()
        elif dirty_indices:
            for idx in dirty_indices:
                self._request_tile_upload(idx)

    def _render_key_to_buffer(self, idx: int, key: Key):
        """Render a single key into the global image buffer."""
        box = self._get_key_box(idx)
        w, h = box[2] - box[0], box[3] - box[1]
        key_img = Image.new("RGB", (w, h), (0, 0, 0))
        draw = ImageDraw.Draw(key_img)
        ctx = KeyContext(draw, width=w, height=h, image=key_img)
        key.render(ctx)
        self.image_buffer.paste(key_img, (box[0], box[1]))

    def _render_blank_key_to_buffer(self, idx: int):
        """Render a solid black tile for an unassigned key slot into global image buffer."""
        box = self._get_key_box(idx)
        w, h = box[2] - box[0], box[3] - box[1]
        black_tile = Image.new("RGB", (w, h), (0, 0, 0))
        self.image_buffer.paste(black_tile, (box[0], box[1]))

    def _request_tile_upload(self, idx: int):
        """Extract a key's 102x102 tile from image_buffer and queue for USB transmission."""
        box = self._get_key_box(idx)
        tile_crop = self.image_buffer.crop(box)
        bgr_bytes = image_to_bgr102(tile_crop, rotation=self.rotation)
        self._render_queue.put((idx, bgr_bytes))


    def push_image(self, image_or_path: Optional[Union[str, Image.Image]] = None):
        """Slice full image buffer (or given image/path) into 12 key tiles and push to device immediately."""
        if image_or_path is not None:
            if isinstance(image_or_path, str):
                self.image_buffer = Image.open(image_or_path).convert("RGB")
            else:
                self.image_buffer = image_or_path.convert("RGB")
            if self.image_buffer.size != (self.width, self.height):
                self.image_buffer = self.image_buffer.resize((self.width, self.height), Image.LANCZOS)
            for idx in range(NUM_KEYS):
                self._synced_keys[idx] = "CUSTOM_IMAGE"

        tiles_bgr = split_image_to_tiles(self.image_buffer, rotation=self.rotation)
        try:
            self.driver.upload_panel(tiles_bgr)
            # Mark all slots as in sync
            current_page = self.page_manager.get_current_page()
            for idx in range(NUM_KEYS):
                key = current_page.keys[idx]
                if key:
                    key._needs_redraw = False
                    self._synced_keys[idx] = key
                else:
                    self._synced_keys[idx] = "CUSTOM_IMAGE"
        except Exception as e:
            log.error(f"Failed to push panel image to display: {e}")





    def _async_render_loop(self):
        """Background worker thread draining tile updates to keep key loops responsive."""
        while not self._queue_worker_stop.is_set():
            try:
                latest: Dict[int, bytes] = {}
                # Drain queue items and deduplicate per key index
                while True:
                    try:
                        idx, bgr_bytes = self._render_queue.get(timeout=0.05)
                        latest[idx] = bgr_bytes
                    except queue.Empty:
                        break

                if latest and self.driver.connected:
                    for idx, bgr_bytes in sorted(latest.items()):
                        try:
                            self.driver.upload_button(idx, bgr_bytes)
                        except Exception as e:
                            log.debug(f"Async upload failed for key {idx}: {e}")
            except Exception as e:
                log.debug(f"Error in async render loop: {e}")
            time.sleep(0.01)