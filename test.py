import logging
from displaypad_driver import DisplayPad
import time

# Set up logging
logging.basicConfig(level=logging.DEBUG)

with DisplayPad(0x3282, 0x0009) as dp:
    dp.set_panel_image(imgpath='./panels/assets/panelimage.png')
    while True:
        try:
            key_events = dp.poll_key()
            
            # Handle newly pressed keys
            if key_events['pressed']:
                print(f"Keys pressed: {key_events['pressed']}")
                for key in key_events['pressed']:
                    match key:
                        case 0:
                            dp.set_brightness(10)
                            logging.info("Brightness set to 10")
                        case 6:
                            dp.set_brightness(100)
                            logging.info("Brightness set to 100")
            
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