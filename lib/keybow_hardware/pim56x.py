import board

from .switches.gpio import GPIO as Switches
from .display.keybow2040 import Keybow2040 as Display

from . import Keybow

# These are the 16 switches on Keybow, with their board-defined names.
_PINS = [board.SW0,
        board.SW1,
        board.SW2,
        board.SW3,
        board.SW4,
        board.SW5,
        board.SW6,
        board.SW7,
        board.SW8,
        board.SW9,
        board.SW10,
        board.SW11,
        board.SW12,
        board.SW13,
        board.SW14,
        board.SW15]

class PIM56X(Keybow):
    def __init__(self):
        self._i2c = board.I2C()
        self._switches = Switches(_PINS)
        self._display = Display(self._i2c)
