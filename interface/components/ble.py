
# Built-in
import gc
gc.collect()
import asyncio
from micropython import const

# Local -> Interface
from interface.basic.logger import Logging
from interface.basic.encoding import Encoder, ArrayEncoder, BOOLEAN_ENCODER
from interface.operational.triggers import Refresher

APPEARANCE = const(0x1440)
TFT_MAC_ADDRESS = "24:58:7C:DC:4F:92"
TFT_NAME = "BikeLight"

BLUEFRUIT_MAC_ADDRESS = "EB:16:79:96:96:30"
BLUEFRUIT_NAME = "Bluefruit"

ESP32_MAC_ADDRESS = "34:B7:DA:5B:78:B2"
ESP32_NAME = "ESP32"

_DISCONNECTING_ERROR_WAIT = const(2)
_CONNECTING_ERROR_WAIT = const(2)

_READING_ERROR_WAIT = 0.1
_WRITING_ERROR_WAIT = 0.1

# =========================== #
#             GAP             #
# =========================== #


class BluetoothTarget:
    def __init__(self, name: str | None, address: str | None, services: list[str] | None):
        self.name = name
        self.address = address.lower() if isinstance(address, str) else None
        self.services = services

    def __repr__(self):
        return f"<BluetoothConnection '{self.name}' at '{self.address}'>"


gc.collect()


class BluetoothConnection:
    def __init__(self, device):
        self.device = device
        self.connection = None

    @property
    def connected(self) -> bool:
        return self.connection.connected if self.connection is not None else False

    @property
    def name(self) -> str:
        return self.device.name

    @property
    def address(self) -> str:
        return self.device.address

    def connect(self, connection = None) -> 'BluetoothConnection':
        if connection is None:
            self.connection = self.device
        else:
            self.connection = connection
        return self

    def __repr__(self):
        return f"<BluetoothConnection '{self.name}' at '{self.address}' ({'' if self.connected else 'not '}connected)>"


gc.collect()


class Bluetooth:

    def __init__(self, name: str | None = None, connection_interval: int | float = 1,
                 logging_name: str | None = None, is_logging: bool | None = None, style: str | None = None):

        self.logging = Logging(logging_name, is_logging, self, style=style)

        # 0: Nothing | 1: Peripheral | 2: central
        self.gap: int = 0

        # Device to connect to
        self.target: BluetoothTarget | None = None
        self.connection: BluetoothConnection | None = None

        # GAP -> Connection
        self.is_connecting = asyncio.Event()
        self.is_disconnecting = asyncio.Event()
        self.connection_interval: int | float = connection_interval

        # Connected events
        self.status = asyncio.Event()

        # GATT
        self.services: list['Service'] = []

    async def _errors(self, context: str, obj, wait: int | float, func, *args, **kwargs):
        try:
            self.logging(f"{context} {obj}")
            return await func(*args, **kwargs)
        except Exception as e:
            self.logging(f"Error while {context} {obj}: {e}", "ERROR")
            await asyncio.sleep(wait)
            return None
            # raise

    def _check(self, connection: BluetoothConnection) -> bool:
        """ Check if the connection fits with the device object."""
        if self.target is None:
            return True
        if self.target.name is not None and self.target.name != connection.name:
            return False
        if self.target.address is not None and self.target.address != connection.address:
            return False
        return True

    """ GAP: User inputs """

    def connect(self) -> 'Bluetooth':
        self.is_connecting.set()
        self.is_disconnecting.clear()
        return self

    def disconnect(self) -> 'Bluetooth':
        self.is_disconnecting.set()
        self.is_connecting.clear()
        return self

    def set_as_peripheral(self, peripheral_device: BluetoothTarget = None,
                          address: str | None = None, name: str | None = None, services: list[str] = None) -> 'Bluetooth':
        """ Set device as peripheral by setting a device. """
        self.target = peripheral_device if peripheral_device is not None \
            else BluetoothTarget(name=name, address=address, services=services) if name or address or services else None
        self.gap = 1
        return self

    def set_as_central(self, peripheral_device: BluetoothTarget = None,
                       address: str | None = None, name: str | None = None, services: list[str] = None) -> 'Bluetooth':
        """ Set device as central by setting a device. """
        self.target = peripheral_device if peripheral_device is not None \
            else BluetoothTarget(name=name, address=address, services=services) if name or address or services else None
        self.gap = 2
        return self

    def reset(self) -> 'Bluetooth':
        self.target = None
        self.gap = 0
        return self

    """ GAP: Properties and async """

    @property
    def connected(self) -> bool:
        return self.connection.connected if self.connection is not None else False

    @property
    def peripheral(self) -> bool:
        return self.gap == 1

    @property
    def central(self) -> bool:
        return self.gap == 2

    async def connecting(self):
        while True:
            await self.is_connecting.wait()
            if not self.connected:
                # Has just been disconnected
                if self.connection is not None:
                    self.on_disconnected()
                # Connect as central or peripheral
                if self.central:
                    await self._errors("Scanning for", self.target, _CONNECTING_ERROR_WAIT, self.scan)
                elif self.peripheral:
                    await self._errors("Advertising for", self.target, _CONNECTING_ERROR_WAIT, self.advertise)
            # Wait for a disconnection
            if self.connected and self.connection is not None:
                await self._unconnected(self.connection)
                self.on_disconnected()
            await asyncio.sleep(self.connection_interval)

    async def disconnecting(self):
        while True:
            await self.is_disconnecting.wait()
            if self.connected:
                res = await self._errors("Disconnecting from", self.connection, _DISCONNECTING_ERROR_WAIT,
                               self._disconnect, self.connection)
                if res:
                    self.on_disconnected()
            await asyncio.sleep(self.connection_interval)

    def on_disconnected(self):
        self.logging(f"Disconnected from {self.connection}")
        self.connection = None
        for service in self.services:
            for characteristic in service.characteristics:
                characteristic.set_activation_bluetooth(False)
        self.status.set()

    def on_connected(self):
        self.logging(f"Connected to {self.connection}")
        for service in self.services:
            for characteristic in service.characteristics:
                characteristic.set_activation_bluetooth(True)
        self.status.set()

    async def refreshing(self):
        await asyncio.gather(
            self.connecting(),
            self.disconnecting(),
        )

    """ GAP: Advertising: Peripheral (server) / Scanning: Central (client) """

    async def advertise(self):
        """ Advertise once, waits for connection to be established by a central."""
        await self.server()
        connection = await self._advertise()
        if not self._check(connection):
            await self._disconnect(connection)
        else:
            self.connection = connection
            self.on_connected()

    async def _scan(self, device: BluetoothConnection) -> bool:
        """ Scans for devices with specific name/mac address/services. """
        if self._check(device):
            connection = await self._errors("Connecting to", device, _CONNECTING_ERROR_WAIT,
                                            self._connect, device)
            if connection is not None:
                self.connection = connection
                await self.client(connection)
                self.on_connected()
            return True
        return False

    """ GATT: Server / Client """

    async def server(self):
        """ Set the service.service and characteristic.characteristic objects. """
        await self._server()

    async def client(self, connection: BluetoothConnection):
        """ Set the service.service and characteristic.characteristic objects from the connection. """
        await self._client(connection)

    """ GAP: Specific to language """

    async def _advertise(self) -> BluetoothConnection | None:
        """ Advertise and returns a connection object."""
        ...

    async def scan(self):
        """ Scan and yield devices objects. """
        ...

    async def _disconnect(self, connection: BluetoothConnection) -> bool:
        """ Disconnects this connection from this device. """
        ...

    async def _connect(self, connection: BluetoothConnection) -> BluetoothConnection:
        """ Connect to device (gives a connection object). """
        ...

    async def _unconnected(self, connection: BluetoothConnection):
        """ Wait for connection to be disconnected. """
        ...

    """ GATT: Specific to language """

    async def _server(self):
        ...

    async def _client(self, connection: BluetoothConnection):
        ...


gc.collect()


# =========================== #
#             GATT            #
# =========================== #


class Service:
    characteristics: list['Characteristic']

    def __init__(self, uuid: str | int, bluetooth: Bluetooth):
        self.uuid = uuid.lower() if isinstance(uuid, str) else uuid
        self.characteristics = []
        self.bluetooth = bluetooth
        self.bluetooth.services.append(self)
        self.service = None

    async def refreshing(self):
        await asyncio.gather(
            *[char.refreshing() for char in self.characteristics]
        )


gc.collect()


class Characteristic(Refresher):

    null = "_"
    informations: list['Information']

    def __init__(self, uuid: str | int, service: Service, initial=None,
                 server: int = 2, encoder: Encoder | None = None,
                 name: str = None, is_logging: bool = None, style: str = None,
                 funcs=None, events=None, coroutines=None, event_loop=None,
                 wait_refresh: int | float = 5, wait_change: int | float = None, check_value: bool = True,
                 initially_active: bool = False,
                 **kwargs):

        # Refresher / Trigger
        self._check_value = check_value
        self._value = initial

        # Service
        self.uuid = uuid.lower() if isinstance(uuid, str) else uuid
        self.service: Service = service
        self.service.characteristics.append(self)
        self.characteristic = None

        # Characteristics
        self.server = server
        self.flag_write = server == 2 or server == 3
        self.flag_read = server == 1 or server == 3
        if (not self.service.bluetooth.peripheral and self.flag_write) or (self.service.bluetooth.peripheral and self.flag_read):
            self.is_writing = asyncio.Event()

        # Active
        self.char_is_active = initially_active
        self.active_based_on_information = wait_refresh is not None

        # Information
        self.informations = []

        # Encoding
        self.encoder = encoder

        # No encoder -> Information
        if encoder is None:
            self.change = asyncio.Event()

        super().__init__(
            funcs=funcs, events=events, coroutines=coroutines, event_loop=event_loop,
            name=name, is_logging=is_logging, style=style,
            wait_refresh=wait_refresh, wait_change=wait_change, initially_active=False, uses_active=True,
        )

    def add_information(self, information: 'Information'):
        self.informations.append(information)
        self.encoder = ArrayEncoder(*[info.encoder for info in self.informations])
        self._value = self.encoder.decode(b'\x00' * self.encoder.size)

    """ User """

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.set_value(value)

    def set_value(self, value):
        if hasattr(self, 'is_writing'):
            self._value = value
            self.is_writing.set()

    """ Encoding """

    def encode(self, value: int | float | bool | str) -> bytes:
        res = self.encoder.encode(value)
        return res

    def decode(self, value: bytes) -> int | float | bool | str:
        return self.encoder.decode(value)

    @property
    def size(self) -> int:
        return self.encoder.size

    """ GATT """

    @property
    def connections(self) -> BluetoothConnection:
        return self.service.bluetooth.connection

    async def read(self) -> bool:
        # Read
        try:
            raw = await self._read()
            val = self.decode(raw)
        except Exception as e:
            self.logging(f"Error while reading: {e}", "ERROR")
            return False
            # raise e

        # Not active any more -> Cancel update
        if not self.is_active:
            return False

        # Update value if different and checking
        if not self._check_value or (self.value != val and self._check_value):
            self._value = val
            self.logging(f"Received: {self.value}")
            return True
        return False

    async def write(self) -> bool:
        self.logging(f"Sending: {self.value}")
        try:
            return await self._write()
        except Exception as e:
            self.logging(f"Error while writing: {e}", "ERROR")
            # return False
            raise e

    """ Refresher """

    async def checking(self):
        while True:
            if all([not info.is_active for info in self.informations]):
                if self.is_active:
                    self.pause()
            else:
                if not self.is_active:
                    self.resume()
            await asyncio.sleep(self.wait_refresh)

    async def reading(self):
        while True:
            if hasattr(self, "active"):
                await self.active.wait()
            res = await self.read()
            if res:
                self.update()
                if self.wait_change is not None:
                    await asyncio.sleep(self.wait_change)
            else:
                await asyncio.sleep(_READING_ERROR_WAIT)  # To avoid blocking when disconnection which causes an error

    async def writing(self):
        while True:
            if hasattr(self, "active"):
                await self.active.wait()
            await self.is_writing.wait()
            if self.is_active:
                res = await self.write()
                if res:
                    self.update()
                    self.is_writing.clear()
                else:
                    await asyncio.sleep(_WRITING_ERROR_WAIT)  # To avoid blocking when disconnection which causes an error

    async def refreshing(self):
        """ (Async) Continuously refreshes the value when changed. When paused waits for active """
        is_server = self.service.bluetooth.peripheral
        write = (not is_server and self.flag_write) or (is_server and self.flag_read)
        read = (not is_server and self.flag_read) or (is_server and self.flag_write)

        tasks = []

        if read:
            tasks.append(asyncio.create_task(self.reading()))
        if write:
            tasks.append(asyncio.create_task(self.writing()))
        if self.active_based_on_information:
            tasks.append(asyncio.create_task(self.checking()))

        await asyncio.gather(*tasks)

    """ Specific to language """

    async def _read(self) -> bytes:
        ...

    async def _write(self) -> bool:
        ...

    """ Refresher """

    def update(self):
        self.callback(self.value)
        for information in self.informations:
            information.update()

    def set_activation_bluetooth(self, value: bool):
        if self.char_is_active or len(self.informations) > 0:
            self.logging("Pausing" if not value else "Resuming", level="INFO")
            if value:
                self.active.set()
            else:
                self.active.clear()
            for information in self.informations:
                information.set_activation_bluetooth(value)

    def set_activation(self, value: bool):
        if value:
            self.resume()
        else:
            self.pause()

    def pause(self):
        self.logging("Pausing", level="INFO")
        self.char_is_active = False
        self.active.clear()
        for information in self.informations:
            if information.is_active:
                information.pause()

    def resume(self):
        self.logging("Resuming", level="INFO")
        self.char_is_active = True
        if self.service.bluetooth.connected:
            self.active.set()
            for information in self.informations:
                if information.char_is_active and not information.is_active:
                    information.resume()


gc.collect()


class Information(Refresher):
    def __init__(self, characteristic: Characteristic, encoder: Encoder = BOOLEAN_ENCODER, initial=None,
                 name: str = None, is_logging: bool = None, style: str = None,
                 funcs=None, events=None, coroutines=None, event_loop=None,
                 initially_active: bool = False,
                 ) -> None:
        self.char_is_active = initially_active
        self.encoder = encoder
        self.characteristic = characteristic
        self.characteristic.add_information(self)
        if initial is not None:
            self.value = initial
        self.last = self.value

        super().__init__(
            funcs=funcs, events=events, coroutines=coroutines, event_loop=event_loop,
            name=name, is_logging=is_logging, style=style,
            initially_active=False, uses_active=True,
        )

    """ User """

    @property
    def value(self):
        if not self in self.characteristic.informations:
            return None
        i = self.characteristic.informations.index(self)
        return self.characteristic.value[i] if self.characteristic.value is not None and len(self.characteristic.value) > i else None

    @value.setter
    def value(self, value):
        self.set_value(value)

    def set_value(self, value):
        if not self in self.characteristic.informations:
            return
        i = self.characteristic.informations.index(self)
        if self.characteristic.value is None or len(self.characteristic.value) <= i:
            return
        new_value = self.characteristic.value
        new_value[i] = value
        self.characteristic.value = new_value

    """ Encoding """

    def encode(self, value: int | float | bool | str) -> bytes:
        return self.encoder.encode(value)

    def decode(self, value: bytes) -> int | float | bool | str:
        return self.encoder.decode(value)

    @property
    def size(self) -> int:
        return self.encoder.size

    """ Refresher """

    def update(self):
        if self.is_active:
            if self.value != self.last:
                self.last = self.value
                self.logging(f"Update: {self.value}", level="TRACE")
                self.callback(self.value)

    def set_activation_bluetooth(self, value: bool):
        if self.char_is_active:
            self.set_activation(value)
            self.char_is_active = True

    def set_activation(self, value: bool):
        if value:
            self.resume()
        else:
            self.pause()

    def pause(self):
        self.char_is_active = False
        super().pause()

    def resume(self):
        self.char_is_active = True
        if self.characteristic.service.bluetooth.connected:
            super().resume()


gc.collect()

