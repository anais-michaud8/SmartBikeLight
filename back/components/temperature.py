
import gc
gc.collect()
import board
import adafruit_thermistor


class TemperatureSensor:
    def __init__(self):
        self.sensor = adafruit_thermistor.Thermistor(
            board.TEMPERATURE, 10000, 10000, 25, 3950
        )

    @property
    def value(self) -> float:
        return self.sensor.temperature


gc.collect()

