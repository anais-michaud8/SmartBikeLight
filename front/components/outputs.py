
from machine import Pin, PWM

from interface.basic.encoding import PercentageInt, Uint16

# =========================== #
#             LEDs            #
# =========================== #


def make_container(pin: Pin | int | list[Pin | int] | None, _class: type, frequency: int = 1000, ):
    if pin is None:
        return None
    if isinstance(pin, list):
        return [_class(pin, frequency) for pin in pin]
    else:
        return _class(pin, frequency)


class Led:
    def __init__(self, pin: Pin | int, frequency: int = 1000):
        pin = Pin(pin, Pin.OUT) if isinstance(pin, int) else pin
        self.led = PWM(pin, freq=frequency, duty_u16=0)

    def show_data(self, data, amplification: int):
        self.led.duty_u16(int(65535 * amplification/100))

    def hide_data(self):
        self.led.duty_u16(0)


# =========================== #
#            Buzzer           #
# =========================== #


class Piezo:
    def __init__(self, pin: int | Pin, tone: Uint16 = 1000):
        self.buzzer = PWM(pin, freq=tone if tone >= 10 else 10, duty_u16=0)

    def show_data(self, data: Uint16, amplification: PercentageInt):
        self.buzzer.init(freq=data, duty_u16=int(65535 * amplification / 100))

    def hide_data(self):
        self.buzzer.deinit()

