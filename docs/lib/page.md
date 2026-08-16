# Multi-Page Navigation and Layout Engine (`Page` & `PageManager`)

Developer documentation for `displaypad_lib.page` module, providing multi-page layout management, stack navigation, and automatic timeout transitions.

## Overview

The paging system allows organizing DisplayPad layouts into multiple named pages (e.g. `Main`, `Media`, `Tools`, `Settings`). Pages can be switched dynamically or automatically timed out back to home/previous screens after inactivity or fixed delays.

## Core Classes

### 1. `Page`

Represents a single 12-key (2x6 grid) screen layout with optional auto-timeout behavior.

```python
from displaypad_lib import Page, LoggerKey

# Create a basic page
media_page = Page(name="Media")
media_page[0] = LoggerKey(0)  # Assign to slot 0 (0-11)
```

#### Auto-Timeout Modes

`Page` supports automatic page switching using the `timeout_mode` parameter:

| `timeout_mode` | Behavior |
| :--- | :--- |
| `"off"` *(default)* | Page remains active indefinitely until explicitly switched. |
| `"after"` | Switches to `timeout_target` after `timeout_seconds` elapsed since arriving on this page. |
| `"idle"` | Switches to `timeout_target` after `timeout_seconds` of user inactivity (no key presses). |

```python
# Auto-return to "Main" after 10 seconds of user inactivity
sub_page = Page(
    name="SubMenu",
    timeout_mode="idle",
    timeout_seconds=10,
    timeout_target="Main"
)

# Return to previous page ("prev") 5 seconds after opening
info_page = Page(
    name="Info",
    timeout_mode="after",
    timeout_seconds=5,
    timeout_target="prev"
)
```

### 2. `PageManager`

Manages page registration, current/previous page tracking, and timeout evaluation.

```python
from displaypad_lib import DisplayPad, Page, LabelKey

pad = DisplayPad()

# Create pages
main_page = Page(name="Main")
settings_page = Page(name="Settings")

# Key on Main page to open Settings page
class OpenSettingsKey(LabelKey):
    def __init__(self):
        super().__init__("Settings", bg_color="purple")
    def on_press(self):
        pad.switch_to_page("Settings")

# Key on Settings page to go Back
class BackKey(LabelKey):
    def __init__(self):
        super().__init__("Back", bg_color="gray")
    def on_press(self):
        pad.page_manager.back()

main_page[0] = OpenSettingsKey()
settings_page[0] = BackKey()

# Register pages with DisplayPad
pad.add_page("Settings", settings_page)
```

## `DisplayPad` Integration APIs

- `pad.add_page(page_id, page)`: Registers a `Page` under `page_id` (string or int).
- `pad.switch_to_page(page_id)`: Switches the active page, marks all key slots for re-sync, and pushes a full-panel update (`push_image()`).
- `pad.page_manager.back()`: Switches back to the previously active page.
- `pad.update(timeout=20)`: Automatically checks `check_timeout()` on every loop tick and handles page transitions when a timeout expires.

## Complete Usage Example

See **[examples/page_example.py](../../examples/page_example.py)** for a fully runnable multi-page application.

```python
from displaypad_lib import DisplayPad, Page, LabelKey, LoggerKey


pad = DisplayPad()

# 1. Main Page
main_page = Page(name="Main")
main_page[0] = LoggerKey(0)

class OpenSubKey(LabelKey):
    def __init__(self):
        super().__init__("Open Sub", bg_color="blue")
    def on_press(self):
        pad.switch_to_page("SubMenu")

main_page[1] = OpenSubKey()

# 2. SubMenu Page with 5-second inactivity timeout
sub_page = Page(name="SubMenu", timeout_mode="idle", timeout_seconds=5, timeout_target="Main")
sub_page[0] = LabelKey("Sub Item 1", bg_color="green")

class BackKey(LabelKey):
    def __init__(self):
        super().__init__("Back", bg_color="red")
    def on_press(self):
        pad.page_manager.back()

sub_page[11] = BackKey()

# 3. Register pages
pad.add_page("SubMenu", sub_page)

# 4. Main Event Loop
try:
    while True:
        pad.update(20)
except KeyboardInterrupt:
    pass
finally:
    pad.disable()
```

## Acknowledgments

Multi-page layout engine design and auto-timeout transitions inspired by [ramisotti13-eng/BaseCamp-Linux](https://github.com/ramisotti13-eng/BaseCamp-Linux).
