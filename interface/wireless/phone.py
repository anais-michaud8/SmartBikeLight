
import json

from interface.wireless.wifi import WifiManager
from interface.wireless.api import API


PORT = 8000
HOST = "192.168.1.128"


class PhoneAPI(API):
    def __init__(self, wifi: WifiManager | None = None, host: str = HOST, port: int = PORT,
                 name: str | None = None, is_logging: bool | None = None, style: str | None = None):
        super().__init__(f"http://{host}:{port}", wifi=wifi, name=name, is_logging=is_logging, style=style)

    def read(self) -> dict:
        try:
            response = self.get()
            if response.status_code == 200:
                return json.loads(response.content.decode("utf-8"))
        except Exception as e:
            self.logging(f"Error when trying to access the {self.__class__.__name__}, .read(): {e}", "ERROR")
        return {}

    def write(self, **kwargs) -> bool:
        try:
            response = self.put(data=kwargs)
            if response.status_code == 200:
                return True
        except Exception as e:
            self.logging(f"Error when trying to access the {self.__class__.__name__}, .write(): {e}", "ERROR")
        return False

    def get_wifi_config(self) -> dict:
        data = self.read()
        if "wifi" in data:
            data = data["wifi"]
            return data if "template" in data and "ssid" in data else {}
        return {}

    def get_data(self, name: str):
        data = self.read()
        if name in data:
            return data[name]
        return {}

    def get_rear_settings(self) -> dict:
        return self.get_data("rear")

    def set_direction_settings(self) -> dict:
        return self.get_data("direction")

    def get_brake_settings(self) -> dict:
        return self.get_data("brake")

    def get_general_settings(self) -> dict:
        return self.get_data("general")

    def get_records(self) -> dict:
        return self.get_data("records")

