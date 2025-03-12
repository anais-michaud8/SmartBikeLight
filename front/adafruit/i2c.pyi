

from typing import Protocol, Optional, TypeAlias, Any, Literal
from machine import I2C
import time

Buffer: TypeAlias = bytearray | bytes | memoryview
WriteableBuffer: TypeAlias = Buffer
ReadableBuffer: TypeAlias = Buffer


class I2CDevice:
    """ Micropython I2C Device """
    i2c: I2C
    address: int
    device_address: int

    def __init__(self, i2c: I2C, device_address: int, **kwargs) -> None:
        ...

    def readinto(
        self, buf: WriteableBuffer, *, start: int = 0, end: int | None = None
    ) -> None:
        if end is None:
            end = len(buf)
        buffer = buf[start:end]
        self.i2c.readfrom_into(self.device_address, buffer)

    def write(
        self, buf: ReadableBuffer, *, start: int = 0, end: int | None = None
    ) -> None:
        if end is None:
            end = len(buf)
        buffer = buf[start:end]
        self.i2c.writeto(self.device_address, buffer)

    # pylint: disable-msg=too-many-arguments
    def write_then_readinto(
        self,
        out_buffer: ReadableBuffer,
        in_buffer: WriteableBuffer,
        *,
        out_start: int = 0,
        out_end: int | None = None,
        in_start: int = 0,
        in_end: int | None = None
    ) -> None:
        if out_end is None:
            out_end = len(out_buffer)
        out_buffer = out_buffer[out_start:out_end]
        if in_end is None:
            in_end = len(in_buffer)
        in_buffer = in_buffer[in_start:in_end]
        self.i2c.readfrom_mem_into(self.device_address, out_buffer, in_buffer)

    def __enter__(self) -> "I2CDevice":
        return self

    def __exit__(
        self,
        exc_type: type[type] | None,
        exc_val: BaseException | None,
        exc_tb: None,
    ) -> bool:
        return False



class I2CDeviceDriver(Protocol):
    """Describes classes that are drivers utilizing `I2CDevice`"""

    i2c_device: I2CDevice


class RWBit:
    """ Single bit register that is readable and writeable. """
    register: int
    byte: int
    bit: int
    buffer: bytearray

    def __init__(
        self,
        register_address: int,
        bit: int,
        register_width: int = 1,
        lsb_first: bool = True,
    ) -> None:
        ...

    def __get__(self, obj: Optional[I2CDeviceDriver], objtype: Optional[type[I2CDeviceDriver]] = None) -> bool:
        ...

    def __set__(self, obj: I2CDeviceDriver, value: bool) -> None:
        ...


class ROBit(RWBit):
    def __set__(self, obj: I2CDeviceDriver, value: bool) -> None:
        ...



class RWBits:
    """ Multi-bit register (less than a full byte) that is readable and writeable. """

    register: int
    byte: int
    bit: int
    mask: int
    buffer: bytearray
    lsb_first: int
    sign_bit: int

    def __init__(
        self,
        num_bits: int,
        register_address: int,
        lowest_bit: int,
        register_width: int = 1,
        lsb_first: bool = True,
        signed: bool = False,
    ) -> None:
        ...

    def __get__(self, obj: Optional[I2CDeviceDriver], objtype: Optional[type[I2CDeviceDriver]] = None) -> int:
        ...

    def __set__(self, obj: I2CDeviceDriver, value: int) -> None:
        ...


class ROBits(RWBits):
    def __set__(self, obj: I2CDeviceDriver, value: int) -> None:
        ...


class Struct:
    """ Arbitrary structure register that is readable and writeable. """
    register: int
    format: str

    def __init__(self, register_address: int, struct_format: str) -> None:
        ...

    def __get__(self, obj: I2CDeviceDriver, objtype: Optional[I2CDeviceDriver] = None) -> tuple:
        ...

    def __set__(self, obj: I2CDeviceDriver, value: tuple) -> None:
        ...




class UnaryStruct:
    """ Arbitrary single value structure register that is readable and writeable. """
    register: int
    format: str

    def __init__(self, register_address: int, struct_format: str):
        ...

    def __get__(self, obj: I2CDeviceDriver, objtype: Optional[I2CDeviceDriver] = None) -> Any:
        ...

    def __set__(self, obj: I2CDeviceDriver, value: Any) -> None:
        ...


class ROUnaryStruct(UnaryStruct):
    def __set__(self, obj: I2CDeviceDriver, value: Any) -> None:
        ...



def _bcd2bin(value: int) -> int:
    """ Convert binary coded decimal to Binary. """
    return value - 6 * (value >> 4)


def _bin2bcd(value: int) -> int:
    """ Convert a binary value to binary coded decimal. """
    return value + 6 * (value // 10)


class BCDDateTimeRegister:
    """ Date and time register using binary coded decimal structure. """
    buffer: bytearray
    register: int
    weekday_offset: Literal[0, 1] | int
    weekday_start: Literal[0, 1] | int
    mask_datetime: bytes

    def __init__(self, register_address: int, weekday_first: bool = True, weekday_start: Literal[0, 1] | int = 1) -> None:
        ...

    def __get__(self, obj: I2CDeviceDriver | None, objtype: type[I2CDeviceDriver] | None = None) -> time.struct_time:
        ...

    def __set__(self, obj: I2CDeviceDriver, value: time.struct_time) -> None:
        ...


FREQUENCY_T = Literal[
        "monthly", "weekly", "daily", "hourly", "minutely", "secondly"
    ]


class BCDAlarmTimeRegister:
    """
    Alarm date and time register using binary coded decimal structure.

    The byte order of the registers must* be: [second], minute, hour, day,
    weekday. Each byte must also have a high enable bit where 1 is disabled and
    0 is enabled.

    * If weekday_shared is True, then weekday and day share a register.
    * If has_seconds is True, then there is a seconds register.

    Values are a tuple of (`time.struct_time`, `str`) where the struct represents
    a date and time that would alarm. The string is the frequency:

    * "secondly", once a second (only if alarm has_seconds)
    * "minutely", once a minute when seconds match (if alarm doesn't seconds then when seconds = 0)
    * "hourly", once an hour when ``tm_min`` and ``tm_sec`` match
    * "daily", once a day when ``tm_hour``, ``tm_min`` and ``tm_sec`` match
    * "weekly", once a week when ``tm_wday``, ``tm_hour``, ``tm_min``, ``tm_sec`` match
    * "monthly", once a month when ``tm_mday``, ``tm_hour``, ``tm_min``, ``tm_sec`` match

    :param int register_address: The register address to start the read
    :param bool has_seconds: True if the alarm can happen minutely.
    :param bool weekday_shared: True if weekday and day share the same register
    :param int weekday_start: 0 or 1 depending on the RTC's representation of the first day of the
      week (Monday)
    """

    has_seconds: bool
    buffer: bytearray
    register: int
    weekday_shared: bool
    weekday_start: int

    # Defaults are based on alarm1 of the DS3231.
    def __init__(self, register_address: int, has_seconds: bool = True,
                 weekday_shared: bool = True, weekday_start: int | Literal[0, 1] = 1) -> None:
        ...

    def __get__(self, obj: I2CDeviceDriver | None, objtype: Optional[type[I2CDeviceDriver]] = None) -> tuple[time.struct_time, FREQUENCY_T]:
        ...

    def __set__(self, obj: I2CDeviceDriver, value: tuple[time.struct_time, FREQUENCY_T]) -> None:
        ...

