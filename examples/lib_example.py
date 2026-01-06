import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from displaypad import DisplayPad, Icon
import logging
import random

logging.basicConfig(level=logging.INFO)

def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

with DisplayPad() as dp:
    for button in dp.buttons:
        icon = Icon.fill_color((button.id * 20 % 256, button.id * 40 % 256, button.id * 60 % 256))
        icon.set_label(f"Btn {button.id}", position=('center', 'center'))
        button.set_icon(icon)
        def make_on_down(b):
            def on_down(btn):
                print(f"Button {b.id} pressed")
                new_icon = Icon.fill_color(random_color())
                new_icon.set_label(f"Btn {b.id}", position=('center', 'center'))
                b.set_icon(new_icon)
            return on_down
        button.on_down(make_on_down(button))
        button.on_up(lambda btn: print(f"Button {btn.id} released"))
    
    print("Starting DisplayPad interaction. Press Ctrl+C to exit.")

    while True:
        try:
            dp.update()
        except KeyboardInterrupt:
            print("Exiting DisplayPad interaction.")
            break