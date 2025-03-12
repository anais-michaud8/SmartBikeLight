import asyncio

import aioble
import bluetooth
from micropython import const

from interface.components import ble as _ble


_ADVERTISEMENT_INTERVAL_US = const(25000)
_ADVERTISEMENT_TIMEOUT_MS = None
_SCANNING_INTERVAL_US = None  # const(30000)
_SCANNING_DURATION_MS = const(10000)
_SCANNING_WINDOW_US = None  # const(30000)
_CONNECTING_TIMEOUT_MS = const(10000)
_READING_TIMEOUT_MS = const(10000)


# =========================== #
#             GAP             #
# =========================== #


class BluetoothConnection(_ble.BluetoothConnection):
    # device: aioble.device.Device
    # connection: aioble.device.DeviceConnection | None

    def __init__(self, device):
        super().__init__(device)

    @property
    def connected(self):
        return self.connection.is_connected if self.connection is not None else False

    @property
    def name(self) -> str | None:
        return None

    @property
    def address(self) -> str | None:
        return self.device.addr_hex()


class Bluetooth(_ble.Bluetooth):
    """ **Bluetooth Interface for MicroPython**

    Limitations
    -----------
    - As a central: Can ONLY specify the address of the Bluetooth device
    - As a peripheral: Can ONLY specify the address of the Bluetooth device

    GAP
    ---
    - Use set_as_central(device...) or set_as_peripheral(device...) to set the specification for the device required and gap type.
    - Otherwise, the first device found will be used.
    - Use reset to set no specification and no gap type.

    Connection
    ----------
    - Use connect() to connect to the device.
    - Use disconnect() to disconnect from the device.
    - The following async functions must be running:
      - connecting()
      - disconnecting()
      - advertising()
      - scanning()

    GATT
    ----
    - Use register to register the services
    - This should be done before advertising...
    - Then use the characteristics to read, write, notify, indicate...

    """

    connection: BluetoothConnection
    services: list['Service']

    def __init__(self, name: str = _ble.TFT_NAME,
                 connection_interval: int | float = 1,
                 logging_name: str | None = None, is_logging: bool | None = None, style: str | None = None):
        super().__init__(name=name, connection_interval=connection_interval,
                         logging_name=logging_name, is_logging=is_logging, style=style)

        self.name = name

    """ GAP: Specific to language """

    # TODO: Fix _scan not working: generator as no __aiter__ or smt like that

    async def _advertise(self) -> BluetoothConnection | None:
        """ Advertise and returns a connection object (connection: aioble.device.DeviceConnection). """
        connection = await aioble.advertise(
            _ADVERTISEMENT_INTERVAL_US,
            name=self.name,
            services=[bluetooth.UUID(service.uuid) for service in self.services], # List of UUIDs
            # appearance=_GENERIC_THERMOMETER,
            # manufacturer=(0xabcd, b"1234"),
            timeout_ms=_ADVERTISEMENT_TIMEOUT_MS,
        )
        return BluetoothConnection(connection.device).connect(connection)

    async def scan(self):
        """ Scans for devices with specific name/mac address/services. """
        async with aioble.scan(
                duration_ms=_SCANNING_DURATION_MS, interval_us=_SCANNING_INTERVAL_US, window_us=_SCANNING_WINDOW_US, active=True
        ) as scanner:
            async for result in scanner:
                device = BluetoothConnection(result.device)
                res = await self._scan(device)
                if res:
                    break

    async def _disconnect(self, connection: BluetoothConnection) -> bool:
        """ Disconnects this connection from this device. """
        await connection.connection.disconnect()
        return True

    async def _connect(self, connection: BluetoothConnection) -> BluetoothConnection:
        """ Connects connection to this device (from device -> connection: aioble.device.DeviceConnection). """
        conn = await connection.device.connect(timeout_ms=_CONNECTING_TIMEOUT_MS)
        return connection.connect(conn)

    async def _unconnected(self, connection: BluetoothConnection):
        """ Wait for connection to be disconnected. """
        if connection is not None and connection.connection is not None:
            await connection.connection.disconnected()

    """ GATT: Specific to language """

    async def _server(self):
        for service in self.services:
            service.service = aioble.Service(bluetooth.UUID(service.uuid))
            for characteristic in service.characteristics:
                characteristic.characteristic = aioble.Characteristic(
                    service.service, bluetooth.UUID(characteristic.uuid),
                    read=characteristic.read, write=characteristic.write, capture=characteristic.read, notify=characteristic.write
                )
            aioble.register_services(service.service)

    async def _client(self, connection: BluetoothConnection):
        for service in self.services:
            if connection is not None and connection.connection is not None:
                service.service = await connection.connection.service(bluetooth.UUID(service.uuid))
                for characteristic in service.characteristics:
                    characteristic.characteristic = await service.service.characteristic(bluetooth.UUID(characteristic.uuid))


# =========================== #
#             GATT            #
# =========================== #


class Service(_ble.Service):
    # service: aioble.Service | aioble.ClientService
    bluetooth: Bluetooth


class Characteristic(_ble.Characteristic):
    # characteristic: aioble.Characteristic | aioble.ClientCharacteristic
    service: Service

    async def _read(self) -> bytes:
        if self.service.bluetooth.central: # Client
            try:
                return await self.characteristic.read(timeout_ms=_READING_TIMEOUT_MS)
            except asyncio.TimeoutError:
                return await self._read()
        elif self.service.bluetooth.peripheral: # Server
            try:
                connection, data = await self.characteristic.written(timeout_ms=_READING_TIMEOUT_MS)
                return data
            except asyncio.TimeoutError:
                return await self._read()
        return self.value

    async def _write(self) -> bool:
        if self.service.bluetooth.central: # Client
            try:
                await self.characteristic.write(self.encode(self.value), timeout_ms=_READING_TIMEOUT_MS)
                return True
            except asyncio.TimeoutError:
                return False
        elif self.service.bluetooth.peripheral: # Server -> Works !
            self.characteristic.write(self.encode(self.value), send_update=True)
            return True
        return False

class Information(_ble.Information):
    characteristic: 'Characteristic'
