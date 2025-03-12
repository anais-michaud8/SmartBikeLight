

from interface.basic.logger import Logging
from interface.components.files import JsonFile, Settings


AP_SSID = "BikeLight"
AP_PASSWORD = "123456"


class Wifi:
    def __init__(self, ssid: str | None = None, password: str | None = None,
                 name: str | None = None, is_logging: bool | None = None, style: str | None = None):
        self._ssid = ssid
        self._password = password
        self.logging = Logging(name, is_logging=is_logging, obj=self, style=style)

    # User

    def disconnect(self):
        self.logging(f"Disconnecting from wifi {self.ssid}...", "INFO")
        self._disconnect()

    def connect(self):
        self.logging(f"Connecting to wifi {self.ssid}...", "INFO")
        self._connect()
        return self

    # Properties

    @property
    def ssid(self) -> str:
        return self._ssid

    @ssid.setter
    def ssid(self, value: str):
        self.set_ssid(value)

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, value: str):
        self.set_password(value)

    # To implement

    def set_password(self, value: str):
        self._password = value

    def set_ssid(self, value: str):
        self._ssid = value

    @property
    def ip(self) -> str:
        return ""

    @property
    def connected(self) -> bool:
        return True

    # Specific

    def _disconnect(self):
        ...

    def _connect(self):
        ...


class PropSetter:
    def __init__(self, instance: str, attr: str):
        self.instance = instance
        self.attr = attr

    def __get__(self, instance, owner):
        return getattr(getattr(instance, self.instance), self.attr)

    def __set__(self, instance, value):
        setattr(getattr(instance, self.instance), self.attr, value)


class WifiManager(Settings):
    ap_ssid = PropSetter("_ap", "ssid")
    ap_password = PropSetter("_ap", "password")
    station_ssid = PropSetter("_station", "ssid")
    station_password = PropSetter("_station", "password")

    def __init__(self, ap: Wifi | None = None, station: Wifi | None = None, default_is_ap: bool = False,
                 phone=None, file: JsonFile = None, template: str | None = "default",
                 ap_ssid: str | None = None, ap_password: str | None = None,
                 station_ssid: str | None = None, station_password: str | None = None,
                 ):
        self._ap = Wifi() if ap is None else ap
        self._station = Wifi() if station is None else station
        self.default_is_ap = default_is_ap
        super().__init__(
            file=file, phone=phone, template=template, name="creds",
            ap_ssid=ap_ssid, ap_password=ap_password,
            station_ssid=station_ssid, station_password=station_password,
        )

    @property
    def is_station(self):
        return self._station.connected

    @property
    def is_ap(self):
        return self._ap.connected

    @property
    def connected(self):
        return self.is_station or self.is_ap

    @property
    def ip(self) -> str:
        return self._ap.ip if self.is_ap else self._station.ip if self.is_station else ""

    def station(self, _=None):
        self._ap.disconnect()
        self._station.connect()

    def ap(self, _=None):
        self._station.disconnect()
        self._ap.connect()

    def connect(self, _=None):
        if self.default_is_ap:
            self.ap()
        else:
            self.station()

    def disconnect(self, _=None):
        self._ap.disconnect()
        self._station.disconnect()

    @property
    def value(self):
        return 1 if self.is_ap else 2 if self.is_station else 0

