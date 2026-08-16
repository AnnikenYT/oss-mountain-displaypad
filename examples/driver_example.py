import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../packages/driver/src')))
from displaypad_driver import DisplayPad, split_image_to_tiles

# Set up logging
logging.basicConfig(level=logging.INFO)

panel_image_path = os.path.join(os.path.dirname(__file__), 'assets/panelimage.png')

initial_screen_path = os.path.join(os.path.dirname(__file__), 'assets/initial_screen.png')

with DisplayPad() as dp:
    if os.path.exists(panel_image_path):
        tiles = split_image_to_tiles(panel_image_path)
        dp.upload_panel(tiles)

    print("Listening for key events... Press Ctrl+C to exit.")
    try:
        while True:
            key_events = dp.poll_key()

            # Handle newly pressed keys
            if key_events['pressed']:
                print(f"Keys pressed: {key_events['pressed']}")

            # Handle newly released keys
            if key_events['released']:
                print(f"Keys released: {key_events['released']}")

            # Show all currently pressed keys
            if key_events['current']:
                print(f"Currently pressed: {key_events['current']}")

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print("Error polling key:", e)
    finally:
        if os.path.exists(initial_screen_path):
            tiles = split_image_to_tiles(initial_screen_path)
            dp.upload_panel(tiles)