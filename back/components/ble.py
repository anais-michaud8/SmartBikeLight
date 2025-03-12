
import gc
gc.collect()

import asyncio
from micropython import const

from back.components.adafruit import Device, BLEConnection, AdafruitBLE, AdaService, AdaCharacteristic, UUID
from interface.components import ble as _ble

_ADVERTISEMENT_INTERVAL = 0.1
_SCANNING_INTERVAL = 0.1
_SCANNING_WINDOW = 0.1
_SCANNING_DURATION = 2
_READING_WAIT = 0.05
_WRITING_WAIT = 0.5
_TRANSMISSION_INTERVAL_MS = 30
_CONNECTING_TIMEOUT = const(10)
_CONNECTING_WAIT = 0.5
_CONNECTING_ERROR_WAIT = const(2)

# =========================== #
#             GAP             #
# =========================== #


class BluetoothConnection(_ble.BluetoothConnection):
    device: Device
    connection: BLEConnection


gc.collect()


class Bluetooth(_ble.Bluetooth):
    """ **Bluetooth Interface for CircuitPython**

    Limitations
    -----------
    - As a central: Should work (not tested yet)
    - As a peripheral: Cannot specify

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

    def __init__(self, name: str = _ble.BLUEFRUIT_NAME,
                 connection_interval: int | float = 1,
                 logging_name: str | None = None, is_logging: bool | None = None, style: str | None = None):
        super().__init__(name=name, connection_interval=connection_interval,
                         logging_name=logging_name, is_logging=is_logging, style=style)

        self.ble = AdafruitBLE()
        self.ble.name = name

    @property
    def connected(self) -> bool:
        return self.ble.connected

    @property
    def name(self) -> str:
        return self.ble.name

    @name.setter
    def name(self, value: str):
        self.ble.name = value

    # TODO: Specify services in advertisement directly

    """ GAP: Specific to language """

    async def _advertise(self) -> BluetoothConnection | None:
        """ Advertise and returns a connection object (connection: BLEConnection)."""
        ...
        # try:
        #     self.ble.start_advertising(ProvideServicesAdvertisement(*[service.service for service in self.services]))
        #     while not self.ble.connected:
        #         await asyncio.sleep(_ADVERTISEMENT_INTERVAL)
        # except Exception as e:
        #     raise e
        # finally:
        #     self.ble.stop_advertising()
        # if len(self.ble.connections) >= 1:
        #     return BluetoothConnection(self.ble.connections[0]).connect()
        # return None

    async def scan(self):
        """ Scan and yield devices objects (device: Advertisement). """
        try:
            for adv in self.ble.start_scan(interval=_SCANNING_INTERVAL, window=_SCANNING_WINDOW, timeout=_SCANNING_DURATION):
                device = BluetoothConnection(adv)
                res = await self._scan(device)
                if res:
                    self.ble.stop_scan()
                    break
        except Exception as e:
            raise e

    async def _disconnect(self, connection: BluetoothConnection) -> bool:
        """ Disconnects this connection from this device. """
        try:
            connection.connection.disconnect()
            return True
        except Exception as e:
            self.logging(f"Error: {e}", "ERROR")
            return False

    async def _connect(self, connection: BluetoothConnection) -> BluetoothConnection | None:
        """ Connect to device (gives a connection object). (device: Advertisement ; connection: BLEConnection). """
        gc.collect()
        connection = connection.connect(connection.device.connect(_CONNECTING_TIMEOUT))
        count = 0
        await asyncio.sleep(_CONNECTING_WAIT*5)
        while not connection.connected and count < _CONNECTING_TIMEOUT//_CONNECTING_WAIT:
            await asyncio.sleep(_CONNECTING_WAIT)
            count += 1
        if not connection.connected or not self.connected:
            return None
        connection.connection.connection_interval = _TRANSMISSION_INTERVAL_MS
        self.logging(f"Connection interval: {connection.connection.connection_interval}ms", "INFO")
        gc.collect()
        return connection

    async def _unconnected(self, connection: BluetoothConnection):
        """ Wait for connection to be disconnected. """
        while self.connected and connection.connected:
            await asyncio.sleep(self.connection_interval)

    """ GATT: Specific to language """

    async def _server(self):
        for service in self.services:
            service.service = AdaService(UUID(service.uuid))
            for characteristic in service.characteristics:
                characteristic.characteristic = AdaCharacteristic(
                    characteristic.uuid, service.service,
                    characteristic.flag_read, characteristic.flag_write,
                    size=characteristic.size
                )

    async def _client(self, connection: BluetoothConnection):
        for service in self.services:
            if connection is not None and connection.connection is not None:
                # Make the uuid of the characteristics to register them !
                for characteristic in service.characteristics:
                    UUID(characteristic.uuid)
                # Get the service and characteristics
                try:
                    service.service = connection.connection.service(UUID(service.uuid))
                    if service.service is not None:
                        for char in service.service.characteristics:
                            characteristic = list(filter(lambda s: UUID(s.uuid) == char.uuid, service.characteristics))
                            if len(characteristic) > 0:
                                characteristic = characteristic[0]
                                characteristic.characteristic = AdaCharacteristic(char, size=characteristic.size)
                except Exception as e:
                    self.logging(f"Error while getting services: {e}", "ERROR")
                    await asyncio.sleep(_CONNECTING_ERROR_WAIT)


gc.collect()


# =========================== #
#             GATT            #
# =========================== #


class Service(_ble.Service):
    service: AdaService | None
    bluetooth: Bluetooth | None
    characteristics: list['Characteristic']


gc.collect()


class Characteristic(_ble.Characteristic):
    service: Service
    characteristic: AdaCharacteristic | None

    async def _read(self) -> bytes:
        if self.characteristic is not None:
            return await self.characteristic.read()
        else:
            await asyncio.sleep(_READING_WAIT)
            return b''

    async def _write(self) -> bool:
        if self.characteristic is not None:
            await self.characteristic.write(self.encode(self.value))
            return True
        else:
            await asyncio.sleep(_WRITING_WAIT)
        return False


gc.collect()


class Information(_ble.Information):
    characteristic: 'Characteristic'


gc.collect()
