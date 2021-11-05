class Display:
    """
    Abstract class providing common interface to the set of pixels
    """
    def set_pixel(self, idx, r, g, b):
        raise NotImplementedError
