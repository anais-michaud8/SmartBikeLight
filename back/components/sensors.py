

import gc
gc.collect()

import board
import busio
# import time
import digitalio
import adafruit_thermistor
import adafruit_lis3dh
from adafruit_lc709203f import LC709203F


class TemperatureSensor:
    def __init__(self):
        self.sensor = adafruit_thermistor.Thermistor(
            board.TEMPERATURE, 10000, 10000, 25, 3950
        )

    @property
    def value(self) -> float:
        return self.sensor.temperature


gc.collect()


class AccelerometerSensor:
    def __init__(self, shaking: int = 30):
        self.shaking = shaking
        self.interrupt = digitalio.DigitalInOut(board.ACCELEROMETER_INTERRUPT)
        self.acceleration_sensor = adafruit_lis3dh.LIS3DH_I2C(
            busio.I2C(board.ACCELEROMETER_SCL, board.ACCELEROMETER_SDA), address=0x19, int1=self.interrupt
        )

    @property
    def shake(self) -> bool:
        return self.acceleration_sensor.shake(shake_threshold=self.shaking)


gc.collect()

class BatteryMonitor:
    def __init__(self):
        self.i2c = board.I2C()
        # counter = 0
        # while not self.i2c.try_lock() or counter > 10:
        #     counter += 1
        #     time.sleep(0.1)
        # print(f"I2C Addresses: {self.i2c.scan()}")
        try:
            self.sensor = LC709203F(self.i2c, 0x0b)
        except Exception:
            pass

    @property
    def value(self) -> int:
        return int(self.sensor.cell_percent if hasattr(self, "sensor") else 0)


gc.collect()

