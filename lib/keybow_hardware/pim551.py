import board
import busio
from digitalio import DigitalInOut, Direction

from .switches.tca9555 import TCA9555 as Switches
from .display.dotstar import Dotstar as Display

from . import Keybow

NUM_KEYS = 16

# Let's match PIM56X orientation
_ROTATED = {
    0:  12,  1:  8,  2: 4,  3: 0,
    4:  13,  5:  9,  6: 5,  7: 1,
    8:  14,  9: 10, 10: 6, 11: 2,
    12: 15, 13: 11, 14: 7, 15: 3,
}

class PIM551(Keybow):
    def __init__(self):
        self._i2c = busio.I2C(board.GP5, board.GP4)
        self._switches = Switches(self._i2c, NUM_KEYS)
        self._display = Display(board.GP18, board.GP19, NUM_KEYS)
        self._cs = DigitalInOut(board.GP17)
        self._cs.direction = Direction.OUTPUT
        self._cs.value = 1

    def set_pixel(self, idx, r, g, b):
        # https://github.com/pimoroni/pimoroni-pico/blob/main/libraries/pico_rgb_keypad/pico_rgb_keypad.cpp#L20-L45
        # code above sets CS only for the time of updating LEDs, so let's do the same
        self._cs.value = 0
        super().set_pixel(_ROTATED[idx], r, g, b)
        self._cs.value = 1

    def switch_state(self, idx):
        return super().switch_state(_ROTATED[idx])
