

import gc
gc.collect()
import neopixel
import board
import pwmio

from interface.components.lights import OFF


# =========================== #
#          NeoPixels          #
# =========================== #


class NeoPixel:
    def __init__(self, pin: board.Pin, number: int = 10, indices: int | list[int] | None = None, brightness: int = 10):
        self.pixels = neopixel.NeoPixel(pin, number, brightness=brightness / 100, auto_write=False)
        self.pixels.fill(OFF)
        self.pixels.show()
        self.indices = indices

    def show_data(self, data, amplification: int):
        self.change_brightness(amplification)
        self.change_colour(data)

    def hide_data(self):
        self.change_colour(OFF)

    def change_brightness(self, brightness: float | int):
        self.pixels.brightness = abs(brightness / 100 if abs(brightness) > 1 else abs(brightness))

    def change_colour(self, colour: tuple[int, int, int]):
        if isinstance(self.indices, int):
            self.pixels[self.indices] = colour
        elif isinstance(self.indices, list) or isinstance(self.indices, range):
            for index in self.indices:
                self.pixels[index] = colour
        else:
            self.pixels.fill(colour)
        self.pixels.show()


# =========================== #
#             LEDs            #
# =========================== #


class Led:
    def __init__(self, pin: board.Pin, frequency: int = 1000):
        self.pin = pwmio.PWMOut(pin, frequency=frequency, duty_cycle=0)

    def show_data(self, data, amplification: int):
        self.pin.duty_cycle = int(65535 * amplification / 100)

    def hide_data(self):
        self.pin.duty_cycle = 0

gc.collect()

