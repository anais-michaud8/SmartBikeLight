

from machine import Pin, SPI, PWM
from micropython import const

from front.components import st7789

_BAUDRATE = const(24000000)
_PIN_SCK = const(36)
_PIN_MOSI = const(35)

_PIN_RESET = const(41)
_PIN_CS = const(42)
_PIN_DC = const(40)
_PIN_BACKLIGHT = const(45)
_PIN_POWER = const(7)

_ROTATION = const(1)
_WIDTH = const(135)
_HEIGHT = const(240)


class TFT(st7789.ST7789):
    def __init__(self, width: int = _WIDTH, height: int = _HEIGHT, landscape: bool = False, inverse: bool = True,
                 activation: bool = True, brightness: int = 0, baudrate: int = _BAUDRATE, frequency: int = 1000,
                 ):
        rotation = 0
        if landscape:
            if inverse:
                rotation = 3
            else:
                rotation = 1
        elif inverse:
            rotation = 2

        super().__init__(
            spi=SPI(1, baudrate=baudrate, sck=Pin(_PIN_SCK), mosi=Pin(_PIN_MOSI), miso=None),
            width=width,
            height=height,
            reset=Pin(_PIN_RESET, Pin.OUT),
            cs=Pin(_PIN_CS, Pin.OUT),
            dc=Pin(_PIN_DC, Pin.OUT),
            # backlight=Pin(_PIN_BACKLIGHT, Pin.OUT),
            rotation=rotation,
        )
        self.power = Pin(_PIN_POWER, Pin.OUT)
        if activation:
            self.power.value(1)
        else:
            self.power.value(0)
        self.bright = PWM(Pin(_PIN_BACKLIGHT, Pin.OUT), freq=frequency, duty_u16=int(65535 * brightness/100))

    def set_brightness(self, value: int):
        self.bright.duty_u16(int(65535 * value/100))

    def sleep_ms(self, value):
        super().sleep_mode(value)
        if value:
            self.power.value(0)
        else:
            self.power.value(1)
        super().sleep_mode(value)
