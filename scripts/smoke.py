"""Smoke script to verify imports for the refactored displaypad package."""
import sys
from pathlib import Path

# ensure project root is on sys.path when running the script directly
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from displaypad import DisplayPad
from displaypad import load_image_bytes
from PIL import Image
import tempfile
import os


def main():
    print("DisplayPad class available:", DisplayPad)

    # test the image loader by creating a tiny image and loading it
    tdir = tempfile.gettempdir()
    test_path = os.path.join(tdir, 'displaypad_smoke_test.png')
    im = Image.new('RGB', (6, 2), (10, 20, 30))
    im.save(test_path)

    pixels = load_image_bytes(test_path)
    print('loaded pixels:', len(pixels))


if __name__ == '__main__':
    main()
