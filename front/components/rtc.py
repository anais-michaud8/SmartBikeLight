
from machine import I2C

from front.adafruit.stemma.pcf8523.pcf8523 import PCF8523
from interface.components.clock import Clock
from interface.wireless.wifi import WifiManager
from interface.wireless.date import DateAPI


class ClockRTC(Clock):
    def __init__(self, i2c: I2C, wifi: WifiManager, initialize_wifi: bool = False, initialize_i2c: bool = True,
                 name: str | None = None, is_logging: bool | None = None, style: str | None = None):
        self.sensor = PCF8523(i2c)
        self.wifi = wifi
        self.api = DateAPI(wifi, name=name, is_logging=is_logging, style=style)
        super().__init__()

        if initialize_wifi:
            self.set_from_wifi()
        elif initialize_i2c:
            self.set_from_i2c()

    def set_from_wifi(self):
        # Connect to wifi
        if not self.wifi.connected:
            self.wifi.connect()

        # Get date from api
        self.datetime = self.api.datetime

        # Update rtc
        self.sensor.datetime = self.datetime

    def set_from_i2c(self):
        self.datetime = self.sensor.datetime

