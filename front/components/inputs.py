

from machine import Pin, ADC


class Button:
    def __init__(self, pin: int | Pin, pull: bool = True, inverse: bool = True):
        self.inverse = inverse
        self.pin = pin if isinstance(pin, Pin) else Pin(pin, Pin.IN, Pin.PULL_UP if pull else Pin.PULL_DOWN)

    @property
    def value(self):
        return not self.pin.value() if self.inverse else bool(self.pin.value())

    def irq(self, activated: bool, handler):
        if activated:
            self.pin.irq(handler=handler, trigger=Pin.IRQ_FALLING)
        else:
            self.pin.irq(handler=handler, trigger=0)


class Potentiometer:
    def __init__(self, pin: int | Pin, start: int = 0, end: int = 100, rounded: int | None = None, inverse: bool = False):
        self.pin = ADC(pin if isinstance(pin, Pin) else Pin(pin), atten=ADC.ATTN_11DB)
        self.start = start
        self.end = end
        self.rounded = rounded
        self.inverse = inverse

    @property
    def raw(self) -> int:
        return 65535 - self.pin.read_u16()

    @property
    def value(self) -> int | float:
        val = self.start + (self.raw / 65535) * (self.end - self.start)
        return round(val, self.rounded) if self.rounded else int(val)

