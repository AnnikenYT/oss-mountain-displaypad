"""DisplayPad Library Package"""

from .displaypad import DisplayPad
from .key import Key, FramerateLimitedKey, LoggerKey, IconKey, GifKey, LabelKey
from .page import Page, PageManager

__version__ = "1.0.1"


__all__ = [
    '__version__',
    'DisplayPad',

    'Key',
    'FramerateLimitedKey',
    'LoggerKey',
    'IconKey',
    'GifKey',
    'LabelKey',
    'Page',
    'PageManager',
]