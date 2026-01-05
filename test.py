import logging
from displaypad import DisplayPad

# Set up logging
logging.basicConfig(level=logging.DEBUG)

dp = DisplayPad(0x3282, 0x0009)

""" while True:
    try:
        key = dp.poll_key()
        print("Polled key:", key)
    except KeyboardInterrupt:
        break
    except Exception as e:
        print("Error polling key:", e) """