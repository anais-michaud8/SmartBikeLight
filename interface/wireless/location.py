

from interface.wireless.api import API
from interface.wireless.wifi import WifiManager

URL = "http://ip-api.com"


class LocationAPI(API):
    def __init__(self, wifi: WifiManager, unit: int = 1,
                 name: str | None = None, is_logging: bool | None = None, style: str | None = None):
        super().__init__(URL, wifi=wifi, name=name, is_logging=is_logging, style=style)

        self.timezone = None
        self.latitude = None
        self.longitude = None

        self.country = None
        self.city = None
        self.zip = None

    def get_from_ip(self):
        try:
            return self.get("json")
        except Exception as e:
            self.logging(f"Error when trying to access the {self.__class__.__name__}, .get_from_ip(): {e}", "ERROR")
            return ""

    def make_from_ip(self):
        try:
            data = self.get_from_ip()
            if data is not None:
                res = data.json()
                self.timezone = res.get("timezone")
                self.latitude = res.get("lat")
                self.longitude = res.get("lon")
                self.country = res.get("country")
                self.city = res.get("city")
                self.zip = res.get("zip")
        except Exception as e:
            self.logging(f"Error when trying to access the {self.__class__.__name__}, .make_from_ip(): {e}", "ERROR")
        return self.latitude, self.longitude

    def read(self) -> tuple[float | None, float | None]:
        """ Returns the lat and long. Other information are retrievable after reading too. """
        self.make_from_ip()
        return self.latitude, self.longitude

