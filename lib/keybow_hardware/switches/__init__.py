class Switches:
    """
    Abstract class providing common interface to the set of switches
    """
    def num_switches(self):
        raise NotImplementedError

    def switch_state(self, idx):
        raise NotImplementedError
