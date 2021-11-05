from digitalio import DigitalInOut, Direction, Pull

from . import Switches

class GPIO(Switches):
    """
    Switches connected directly to GPIO
    """
    def __init__(self, pins):
        self._switches = [DigitalInOut(pin) for pin in pins]
        for switch in self._switches:
            switch.direction = Direction.INPUT
            switch.pull = Pull.UP

    def num_switches(self):
        return len(self._switches)

    def switch_state(self, idx):
        return not self._switches[idx].value
