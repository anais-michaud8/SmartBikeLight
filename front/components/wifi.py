
import network

from interface.wireless.wifi import Wifi as _Wifi
from interface.wireless.wifi import WifiManager as _WifiManager
from interface.wireless.wifi import AP_SSID, AP_PASSWORD


class Wifi(_Wifi):
    def __init__(self, protocol, ssid: str | None = None, password: str | None = None,
                 name: str | None = None, is_logging: bool | None = None, style: str | None = None):
        super().__init__(ssid=ssid, password=password, name=name, is_logging=is_logging, style=style)
        self.wifi = network.WLAN(protocol)

    # To implement

    @property
    def ip(self) -> str:
        return self.wifi.ifconfig('addr4')[0]

    @property
    def connected(self) -> bool:
        return self.wifi.isconnected()

    def set_password(self, value: str):
        super().set_password(value)
        self.wifi.config(key=value)

    def set_ssid(self, value: str):
        super().set_ssid(value)
        self.wifi.config(ssid=value)

    # Specific

    def _disconnect(self):
        self.wifi.active = False


class AccessPoint(Wifi):
    def __init__(self, ssid: str = AP_SSID, password: str = AP_PASSWORD,
                 name: str | None = None, is_logging: bool | None = None, style: str | None = None):
        super().__init__(ssid=ssid, protocol=network.WLAN.IF_AP, password=password, is_logging=is_logging, style=style)

    def _connect(self):
        self.wifi.config(essid=self.ssid, password=self.password, authmode=network.AUTH_WPA_WPA2_PSK)
        self.wifi.active(True)
        self.logging(self.wifi.ifconfig())


class WifiStation(Wifi):
    def __init__(self, ssid: str | None = None, password: str | None = None,
                 name: str | None = None, is_logging: bool | None = None, style: str | None = None):
        super().__init__(ssid=ssid, protocol=network.WLAN.IF_STA, password=password, name=name, is_logging=is_logging, style=style)

    def _connect(self):
        self.wifi.active(True)
        self.wifi.connect(self.ssid, self.password)
        self.logging(self.wifi.ifconfig("addr4"))


class WifiManager(_WifiManager):
    _ap: AccessPoint
    _station: WifiStation

