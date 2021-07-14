import adafruit_dotstar

from . import Display

class Dotstar(Display):
    """
    Display consisting of dotstars
    """
    def __init__(self, clock, data, count):
        self._pixels = adafruit_dotstar.DotStar(clock, data, count)

    def set_pixel(self, idx, r, g, b):
        self._pixels[idx] = (r, g, b)
