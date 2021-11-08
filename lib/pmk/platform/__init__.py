class PMK:
    """
    Abstract class providing common interface to RGB-backlit keyboard
    Subclasses should fill _switches and _display properties.
    Filling _i2c is optional, unless you want to use i2c() accessor.
    """

    def set_pixel(self, idx, r, g, b):
        self._display.set_pixel(idx, r, g, b)

    def num_keys(self):
        return self._switches.num_switches()

    def switch_state(self, idx):
        return self._switches.switch_state(idx)

    def i2c(self):
        return self._i2c
