from . import Switches

class TCA9555(Switches):
    """
    Switches connected via TCA9555 IO expander on i2c
    """
    def __init__(self, i2c, count):
        self._count = count
        self._i2c = i2c

    def num_switches(self):
        return self._count

    def switch_state(self, idx):
        buffer = bytearray(self._count // 8)
        buffer[0] = 0x0
        while not self._i2c.try_lock():
            pass
        self._i2c.writeto_then_readfrom(0x20, buffer, buffer, out_end=1)
        self._i2c.unlock()
        b = buffer[0] | buffer[1] << 8 # up to 16 buttons supported now
        return not (1 << idx) & b
