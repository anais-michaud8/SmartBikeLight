
import gc
gc.collect()

import time

import asyncio
import _bleio
import struct

from _bleio import UUID
from _bleio import Service as AdaService

_WRITING_INTERVAL = 0.1
_READING_INTERVAL = 0.1


def decode_data(
        data: bytes, *, key_encoding: str = "B"
):  # -> Dict[Any, Union[bytes, List[bytes]]]:
    """Helper which decodes length encoded structures into a dictionary with the given key
    encoding."""
    i = 0
    data_dict = {}
    key_size = struct.calcsize(key_encoding)
    while i < len(data):
        item_length = data[i]
        i += 1
        if item_length == 0:
            break
        key = struct.unpack_from(key_encoding, data, i)[0]
        value = data[i + key_size: i + item_length]
        if key in data_dict:
            if not isinstance(data_dict[key], list):
                data_dict[key] = [data_dict[key]]
            data_dict[key].append(value)
        else:
            data_dict[key] = value
        i += item_length
    return data_dict


class Device:
    def __init__(self, entry: _bleio.ScanEntry, ble: 'AdafruitBLE'):
        self.entry = entry
        self.connection = None
        self.ble = ble

    @property
    def address(self) -> str:
        return str(self.entry.address)[9:-1] if len(str(self.entry.address)) > 10 else ""

    @property
    def name(self):
        data = decode_data(self.entry.advertisement_bytes)
        return str(data[9], 'utf-8') if 9 in data.keys() else None

    def connect(self, timeout: int | float = 1):
        self.connection = self.ble.connect(self.entry.address, timeout=timeout)
        return self.connection

    def __repr__(self):
        return f"Scanned({self.address}, {self.name})"

gc.collect()

class BLEConnection:
    """ Represents a connection to a peer BLE device. """

    def __init__(self, connection: _bleio.Connection) -> None:
        self.connection = connection

    def service(self, uuid: _bleio.UUID) -> _bleio.Service | None:
        results = self.connection.discover_remote_services((uuid,))
        if results:
            return results[0]
        return None

    @property
    def connected(self) -> bool:
        """True if the connection to the peer is still active."""
        return self.connection.connected

    @property
    def paired(self) -> bool:
        """True if the paired to the peer."""
        return self.connection.paired

    @property
    def connection_interval(self) -> float:
        """Time between transmissions in milliseconds. Will be multiple of 1.25ms. Lower numbers
        increase speed and decrease latency but increase power consumption.

        When setting connection_interval, the peer may reject the new interval and
        `connection_interval` will then remain the same.

        Apple has additional guidelines that dictate should be a multiple of 15ms except if HID
        is available. When HID is available Apple devices may accept 11.25ms intervals.
        """
        return self.connection.connection_interval

    @connection_interval.setter
    def connection_interval(self, value: float) -> None:
        self.connection.connection_interval = value

    def pair(self, *, bond: bool = True) -> None:
        """Pair to the peer to increase security of the connection."""
        return self.connection.pair(bond=bond)

    def disconnect(self) -> None:
        """Disconnect from peer."""
        self.connection.disconnect()

gc.collect()

class AdaCharacteristic:
    def __init__(self, uuid: str | int | _bleio.Characteristic, service: _bleio.Service = None,
                 read: bool = False, write: bool = False, size: int = 1) -> None:
        self.size = size

        self._last_value = b''

        if isinstance(uuid, _bleio.Characteristic):
            self.characteristic = uuid
        else:
            flags = 0
            if read:
                flags |= _bleio.Characteristic.READ | _bleio.Characteristic.NOTIFY
            if write:
                flags |= _bleio.Characteristic.WRITE_NO_RESPONSE

            self.characteristic = _bleio.Characteristic.add_to_service(
                service, UUID(uuid), properties=flags, max_length=size, fixed_length=True
            )
        self.characteristic.set_cccd(notify=write)

    @property
    def uuid(self) -> _bleio.UUID:
        return self.characteristic.uuid

    @property
    def value(self) -> bytes:
        return self.characteristic.value

    @value.setter
    def value(self, value: bytes) -> None:
        self.characteristic.value = value

    async def read(self) -> bytes:
        while self._last_value == self.characteristic.value:
            await asyncio.sleep(_READING_INTERVAL)
        self._last_value = self.characteristic.value
        return self.characteristic.value

    async def write(self, value: bytes):
        self.characteristic.value = value
        while value != self.characteristic.value:
            await asyncio.sleep(_WRITING_INTERVAL)

gc.collect()

class AdafruitBLE:
    def __init__(self):
        self._adapter = _bleio.adapter
        self.name = None

    def start_scan(self, name: str | None = None, address: str | None = None,
             timeout: float = 2, interval: float = 0.1, window: float = 0.1, active: bool = True):
        addresses = []
        for entry in self._adapter.start_scan(timeout=timeout, interval=interval, window=window, active=active):
            scan = Device(entry, self)
            if scan.address in addresses:
                continue
            addresses.append(scan.address)
            if name is not None and address is not None:
                if scan.name == name and scan.address == address.lower():
                    yield scan
            elif name is not None:
                if scan.name == name:
                    yield scan
            elif address is not None:
                if scan.address == address.lower():
                    yield scan
            else:
                yield scan

    def stop_scan(self):
            self._adapter.stop_scan()

    @property
    def connected(self) -> bool:
        return self._adapter.connected

    def connect(self, address: _bleio.Address, timeout: float | None = 2) -> BLEConnection:
        return BLEConnection(self._adapter.connect(address, timeout=timeout))


gc.collect()
