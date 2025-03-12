
import gc
gc.collect()
import board
import digitalio


class Button:
    def __init__(self, pin: board.Pin, pull: bool = True, inverse: bool = False,):
        self.source = digitalio.DigitalInOut(pin)
        self.inverse = inverse
        if pull:
            self.source.switch_to_input(pull=digitalio.Pull.UP)
        else:
            self.source.switch_to_input(pull=digitalio.Pull.DOWN)

    @property
    def value(self):
        return not self.source.value if self.inverse else self.source.value

