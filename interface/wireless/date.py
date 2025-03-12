
import time

from interface.wireless.api import API
from interface.wireless.wifi import WifiManager
from interface.components.clock import WEEKDAYS


URL = "https://timeapi.io"


class DateAPI(API):
    def __init__(self, wifi: WifiManager,
                 name: str | None = None, is_logging: bool | None = None, style: str | None = None):
        super().__init__(URL, wifi=wifi, name=name, is_logging=is_logging, style=style)

        self.datetime = time.localtime()
        self.timezone = ""

    def get_from_ip(self):
        try:
            return self.get(f"api/time/current/ip", f"ipAddress={self.wifi.ip}")
        except Exception as e:
            self.logging(f"Error when trying to access the ClockAPI, .get_gmt(): {e}", "ERROR")
            return ""

    def make_date_from_ip(self):
        try:
            data = self.get_from_ip().json()
            if data is not None:
                self.timezone = data["timeZone"]
                self.datetime = (
                    data['year'], data['month'], data['day'],
                    data['hour'], data['minute'], data['seconds'],
                    WEEKDAYS.index(data['dayOfWeek']) if data["dayOfWeek"] in WEEKDAYS else -1,
                    int(data['timeZone'] == "UTC"),
                    int(data['dstActive'] == "True")
                )
        except Exception as e:
            self.logging(f"Error when trying to access the {self.__class__.__name__}, make_date_from_ip.(): {e}", "ERROR")
        return self.datetime

    def read(self):
        """ Returns the datetime. Timezone available as self.timezone. """
        self.make_date_from_ip()
        return self.datetime
