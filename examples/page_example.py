"""Example demonstrating multi-page navigation and auto-timeouts on the DisplayPad."""

import os
import sys
import logging
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../packages/driver/src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../packages/library/src')))

from displaypad_lib import DisplayPad, Page, LabelKey, LoggerKey

logging.basicConfig(level=logging.INFO)

# Initialize DisplayPad
pad = DisplayPad()

# --- Page 1: Main Page ---
main_page = Page(name="Main")

class OpenMediaPageKey(LabelKey):
    def __init__(self):
        super().__init__("Media 🎵", bg_color="navy")
    def on_press(self):
        logging.info("Switching to Media page...")
        pad.switch_to_page("Media")

class OpenSettingsPageKey(LabelKey):
    def __init__(self):
        super().__init__("Settings ⚙️", bg_color="purple")
    def on_press(self):
        logging.info("Switching to Settings page...")
        pad.switch_to_page("Settings")

main_page[0] = LoggerKey(0)
main_page[1] = OpenMediaPageKey()
main_page[2] = OpenSettingsPageKey()

pad.add_page("Main", main_page)



# --- Page 2: Media Page ---
media_page = Page(name="Media")

class BackToMainKey(LabelKey):
    def __init__(self):
        super().__init__("Back ⬅️", bg_color="darkred")
    def on_press(self):
        logging.info("Going back to previous page...")
        pad.page_manager.back()

media_page[0] = LabelKey("Play/Pause", bg_color="darkgreen")
media_page[1] = LabelKey("Next Track", bg_color="darkgreen")
media_page[11] = BackToMainKey()

pad.add_page("Media", media_page)


# --- Page 3: Settings Page with 5-Second Inactivity Timeout ---
# Automatically returns to "Main" after 5 seconds of no key presses.
settings_page = Page(
    name="Settings",
    timeout_mode="idle",
    timeout_seconds=5,
    timeout_target="Main"
)

settings_page[0] = LabelKey("Wifi ON", bg_color="darkblue")
settings_page[1] = LabelKey("BT ON", bg_color="darkblue")
settings_page[5] = LabelKey("Idle 5s ⏳", bg_color="orange", text_color="black")
settings_page[11] = BackToMainKey()

pad.add_page("Settings", settings_page)


# --- Main Event Loop ---
print("DisplayPad Multi-Page Example Running.")
print("Press Key 1 for Media, Key 2 for Settings (auto-times out to Main after 5s idle).")
print("Press Ctrl+C to exit.")

initial_screen_path = os.path.join(os.path.dirname(__file__), 'assets/initial_screen.png')

try:
    while True:
        pad.update(20)
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    if os.path.exists(initial_screen_path):
        pad.push_image(initial_screen_path)
    pad.disable()

