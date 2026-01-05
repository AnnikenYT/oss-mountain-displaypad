import logging
from displaypad import DisplayPad
import time

# Set up logging
logging.basicConfig(level=logging.DEBUG)

with DisplayPad(0x3282, 0x0009) as dp:
    dp.set_panel_image(imgpath='./panels/assets/panelimage.png')
    while True:
        try:
            key = dp.poll_key()
            if key is not None:
                print("Polled key:", key)
                match key:
                    case 0:
                        dp.set_brightness(10)
                        logging.info("Brightness set to 10")
                    case 6:
                        dp.set_brightness(100)
                        logging.info("Brightness set to 100")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print("Error polling key:", e)