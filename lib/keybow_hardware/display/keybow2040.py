from adafruit_is31fl3731.keybow2040 import Keybow2040 as Pixels

from . import Display

class Keybow2040(Display):
    """
    Keybow 2040 4x4 display
    """
    def __init__(self, i2c):
        self._pixels = Pixels(i2c)

    def set_pixel(self, idx, r, g, b):
        self._pixels.pixelrgb(idx % 4, idx // 4, r, g, b)
