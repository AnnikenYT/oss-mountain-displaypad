import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from displaypad_driver import DisplayPad

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

with DisplayPad(0x3282, 0x0009) as dp:
    dp.set_panel_image(imgpath='examples/assets/panelimage.png')
    while True:
        try:
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
            break
        except Exception as e:
            print("Error polling key:", e)