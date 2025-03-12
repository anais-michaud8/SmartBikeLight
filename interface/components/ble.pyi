
# Built-in
import asyncio
from micropython import const
from typing import Protocol, Optional, Any, TypeAlias, Callable, Literal

# Local -> Interface
from interface.basic.logger import Logging
from interface.basic.encoding import Encoder, ArrayEncoder, BOOLEAN_ENCODER
from interface.operational.triggers import Refresher
from interface.operational.triggers import ActionEvents, ActionCoroutines


Value: TypeAlias = Optional[int | float | bool | str]
ListedVal: TypeAlias = list[Value] | Value

CharActionFunction: TypeAlias = Callable[[ListedVal], ...]
CharActionFuncs: TypeAlias = list[CharActionFunction]
CharActionFuncsArg: TypeAlias = Optional[CharActionFuncs | CharActionFunction]


InfActionFunction: TypeAlias = Callable[[Value], ...]
InfActionFuncs: TypeAlias = list[CharActionFunction]
InfActionFuncsArg: TypeAlias = Optional[CharActionFuncs | CharActionFunction]


class DeviceProtocol(Protocol):
    name: str
    connected: bool


class ConnectionProtocol(Protocol):
    connected: bool


# =========================== #
#          Constants          #
# =========================== #


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
    name: str
    address: Optional[str]
    services: list[str]

    def __init__(self, name: str | None, address: str | None, services: list[str] | None):
        ...

    def __repr__(self) -> str:
        ...


class BluetoothConnection:
    device: DeviceProtocol
    connection: Optional[ConnectionProtocol]

    name: str
    address: str

    def __init__(self, device: DeviceProtocol):
        ...

    @property
    def connected(self) -> bool:
        ...

    def connect(self, connection = None) -> BluetoothConnection:
        ...

    def __repr__(self) -> str:
        ...


class Bluetooth:
    """ **Bluetooth Interface**

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

    GATT
    ----
    - Use register to register the services
    - This should be done before advertising...
    - Then use the characteristics to read, write, notify, indicate...

    """

    logging: Logging
    gap: int
    target: Optional[BluetoothTarget]
    connection: Optional[BluetoothConnection]
    is_connecting: asyncio.Event
    is_disconnecting: asyncio.Event
    connection_interval: int | float
    services: list[Service]
    status: asyncio.Event

    connected: bool
    peripheral: bool
    central: bool

    def __init__(self, name: str | None = None, connection_interval: int | float = 1,
                 logging_name: str | None = None, is_logging: bool | None = None, style: str | None = None):
        ...

    async def _errors(self, context: str, obj, wait: int | float, func, *args, **kwargs):
        ...

    def _check(self, connection: BluetoothConnection) -> bool:
        """ Check if the connection fits with the device object."""
        ...

    """ GAP: User inputs """

    def connect(self) -> 'Bluetooth':
        ...

    def disconnect(self) -> 'Bluetooth':
        ...

    def set_as_peripheral(self, peripheral_device: BluetoothTarget = None,
                          address: str | None = None, name: str | None = None, services: list[str] = None) -> 'Bluetooth':
        """ Set device as peripheral by setting a device. """
        ...

    def set_as_central(self, peripheral_device: BluetoothTarget = None,
                       address: str | None = None, name: str | None = None, services: list[str] = None) -> 'Bluetooth':
        """ Set device as central by setting a device. """
        ...

    def reset(self) -> 'Bluetooth':
        ...

    """ GAP: Properties and async """

    async def connecting(self):
        ...

    async def disconnecting(self):
        ...

    def on_disconnected(self):
        ...

    def on_connected(self):
        ...

    async def refreshing(self):
        ...

    """ GAP: Advertising: Peripheral (server) / Scanning: Central (client) """

    async def advertise(self):
        """ Advertise once, waits for connection to be established by a central."""
        ...

    async def _scan(self, device: BluetoothConnection) -> bool:
        """ Scans for devices with specific name/mac address/services. """
        ...

    """ GATT: Server / Client """

    async def server(self):
        """ Set the service.service and characteristic.characteristic objects. """
        ...

    async def client(self, connection: BluetoothConnection):
        """ Set the service.service and characteristic.characteristic objects from the connection. """
        ...

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


# =========================== #
#             GATT            #
# =========================== #


class Service:
    characteristics: list['Characteristic']

    uuid: str
    bluetooth: Bluetooth
    service: Any

    def __init__(self, uuid: str | int, bluetooth: Bluetooth):
        ...

    async def refreshing(self):
        ...


class Characteristic(Refresher):
    # Action
    funcs: CharActionFuncs

    """

    Usage
    -----
    - Async run refreshing()
    - Use set_value() and/or self.value = ... to set read / write characteristic

    Limitations
    -----------
    - Whether the characteristic is for a server (peripheral) or a client (central) must be set before making the characteristics.
    - The write and read at initiation determines if reading and writing will be run in refreshing.
    - The write flag can be changed after initiation but will only change whether the is_writing gets activated after setting the value.

    Flags
    -----
    - Broadcast:         Allowed in advertising packets
    - Indicate:          Server will indicate to the client when the value is set and wait for a response
    - Notify:            Server will notify the client when the value is set
    - Read:              Clients may read this characteristic
    - Write:             Clients may write this characteristic; a response will be sent back
    - Write no response: Clients may write this characteristic; no response will be sent back
    - Capture:           Set as true to use written() (meaning server reads)


    **Server flags:**

    - 0: Not used
    - 1: Read-only    ->   Write as server | Read  as client   ->   Notify + Read
        - Flags: READ
        - Server (peripheral): Write
        - Client (central): Read
    - 2: Write-only   ->   Read  as server | Write as client   ->   Capture + Write no response
        - Flags: WRITE
        - Server (peripheral): Read
        - Client (central): Write
    - 3: Read-Write
        - Flags: READ & WRITE
        - Server (peripheral): Read & Write
        - Client (central): Read & Write

    """

    null = "_"
    informations: list['Information']

    _check_value: bool
    _value: ListedVal
    uuid: str
    service: Service
    characteristic: Any
    server: int | Literal[0, 1, 2]
    flag_write: bool
    flag_read: bool
    is_writing: asyncio.Event
    char_is_active: bool
    active_based_on_information: bool
    informations: list[Information]
    encoder: Optional[Encoder | ArrayEncoder]
    change: asyncio.Event

    size: int
    connections: BluetoothConnection

    def __init__(self,
                 uuid: str | int,
                 service: Service,
                 initial: ListedVal = None,
                 server: int | Literal[0, 1, 2] = 2,
                 encoder: Optional[Encoder | ArrayEncoder] = None,
                 funcs: CharActionFuncsArg = None,
                 events: Optional[ActionEvents] = None,
                 coroutines: Optional[ActionCoroutines] = None,
                 event_loop: Optional[asyncio.AbstractEventLoop] = None,
                 name: Optional[str] = None,
                 is_logging: Optional[bool] = None,
                 style: Optional[str] = None,
                 wait_change: Optional[int | float] = None,
                 check_value: bool = True,
                 initially_active: bool = False,
                 wait_refresh: int | float = 5,
                 **kwargs):
        """

        Args:
            uuid (str | int):
                The uuid of the characteristic.
            service (Service):
                The service object, parent to the characteristic.
            initial (Optional[Any]):
                The (optional) initial value of the characteristic.
            server (int):
                The server flags. 0 (/), 1 (RO), 2 (WO) or 3 (RW).
            output ():
                The type of the characteristic. Can be int, float, bool, str.
            size ():
                The maximum size of the string of the value of the characteristic.
            name ():
                The name of the characteristic for logging purposes.
            is_logging ():
                Whether to log.
            style ():
                The style of to log.
            funcs ():
                A or many function(s) to call on change.
            events ():
                A or many events to set on change.
            coroutines ():
                A or many coroutines to run on change.
            event_loop ():
                The event loop to add the coroutines to.
            wait_change (Optional[int]):
                The (optional) time to wait after a change.
            check_value ():
                Whether to check if the value is different to last or not.
            active ():
                Whether the characteristic is active or not. This will not mean that the refreshing is run if the connection is not on.
            **kwargs ():
        """
        ...

    def add_information(self, information: 'Information'):
        ...

    """ User """

    def set_value(self, value: ListedVal):
        ...

    @property
    def value(self) -> ListedVal:
        ...

    @value.setter
    def value(self, value: ListedVal):
        ...

    """ Encoding """

    def encode(self, value: ListedVal) -> bytes:
        ...

    def decode(self, value: bytes) -> ListedVal:
        ...

    """ GATT """

    async def read(self) -> bool:
        ...

    async def write(self) -> bool:
        ...

    """ Refresher """

    async def checking(self):
        ...

    async def reading(self):
        ...

    async def writing(self):
        ...

    async def refreshing(self):
        """ (Async) Continuously refreshes the value when changed. When paused waits for active """
        ...

    """ Specific to language """

    async def _read(self) -> bytes:
        ...

    async def _write(self) -> bool:
        ...

    """ Refresher """

    def update(self):
        ...

    def set_activation(self, value: bool):
        ...

    def pause(self):
        ...

    def resume(self):
        ...

    def set_activation_bluetooth(self, value: bool):
        ...

    def add(self,
            funcs: InfActionFuncsArg = None,
            events: Optional[ActionEvents] = None,
            coroutines: Optional[ActionCoroutines] = None,
            event_loop: Optional[asyncio.AbstractEventLoop] = None,
            ):
        ...



class Information(Refresher):
    funcs: InfActionFuncs
    value: Value

    char_is_active: bool
    encoder: Encoder
    characteristic: Characteristic
    last: Value
    size: int

    def __init__(self,
                 characteristic: Characteristic,
                 encoder: Encoder = BOOLEAN_ENCODER,
                 initial: Value = None,
                 funcs: InfActionFuncsArg = None,
                 events: Optional[ActionEvents] = None,
                 coroutines: Optional[ActionCoroutines] = None,
                 event_loop: Optional[asyncio.AbstractEventLoop] = None,
                 name: Optional[str] = None,
                 is_logging: Optional[bool] = None,
                 style: Optional[str] = None,
                 initially_active: bool = False,
                 ) -> None:
        ...

    """ User """

    def set_value(self, value: ListedVal):
        ...

    @property
    def value(self) -> ListedVal:
        ...

    @value.setter
    def value(self, value: ListedVal):
        ...

    """ Encoding """

    def encode(self, value: int | float | bool | str) -> bytes:
        ...

    def decode(self, value: bytes) -> int | float | bool | str:
        ...

    """ Refresher """

    def update(self):
        ...

    def set_activation_bluetooth(self, value: bool):
        ...

    def set_activation(self, value: bool):
        ...

    def pause(self):
        ...

    def resume(self):
        ...

    def add(self,
            funcs: InfActionFuncsArg = None,
            events: Optional[ActionEvents] = None,
            coroutines: Optional[ActionCoroutines] = None,
            event_loop: Optional[asyncio.AbstractEventLoop] = None,
            ):
        ...
