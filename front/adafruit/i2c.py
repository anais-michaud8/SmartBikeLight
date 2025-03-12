
import gc
gc.collect()

from machine import I2C
import struct
import time

# =========================== #
#          I2C Device         #
# =========================== #


class I2CDevice:
    def __init__(self, i2c: I2C, device_address: int, **kwargs) -> None:
        self.i2c = i2c
        self.address = device_address
        self.device_address = device_address

    def readinto(
        self, buf, *, start: int = 0, end: int | None = None
    ) -> None:
        if end is None:
            end = len(buf)
        buffer = buf[start:end]
        self.i2c.readfrom_into(self.device_address, buffer)

    def write(
        self, buf, *, start: int = 0, end: int | None = None
    ) -> None:
        if end is None:
            end = len(buf)
        buffer = buf[start:end]
        self.i2c.writeto(self.device_address, buffer)

    def write_then_readinto(
        self,
        out_buffer,
        in_buffer,
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


gc.collect()


# =========================== #
#             Bit             #
# =========================== #


class RWBit:
    """ Single bit register that is readable and writeable. """

    def __init__(
        self,
        register_address: int,
        bit: int,
        register_width: int = 1,
        lsb_first: bool = True,
    ) -> None:
        self.register = register_address
        self.byte = bit // 8 if lsb_first else register_width - (bit // 8) - 1
        self.bit = bit % 8
        self.buffer = bytearray(register_width)

    def __get__(self, obj, objtype=None) -> bool:
        obj.i2c_device.i2c.readfrom_mem_into(obj.i2c_device.address, self.register, self.buffer)
        return bool((self.buffer[self.byte] >> self.bit) & 1)

    def __set__(self, obj, value: bool) -> None:
        # Get buffer
        obj.i2c_device.i2c.readfrom_mem_into(obj.i2c_device.address, self.register, self.buffer)

        # Change bit
        self.buffer[self.byte] = (self.buffer[self.byte] & ~(1 << self.bit)) | ((value & 1) << self.bit)

        # Write
        obj.i2c_device.i2c.writeto_mem(obj.i2c_device.address, self.register, self.buffer)


class ROBit(RWBit):
    def __set__(self, obj, value: bool) -> None:
        raise AttributeError()

gc.collect()


# =========================== #
#             Bits            #
# =========================== #


# TODO: Add LSB functionality

class RWBits:

    def __init__(
        self,
        num_bits: int,
        register_address: int,
        lowest_bit: int,
        register_width: int = 1,
        lsb_first: bool = True,
        signed: bool = False,
    ) -> None:
        self.register = register_address
        self.byte = lowest_bit // 8
        self.bit = lowest_bit % 8
        self.mask = ((1 << (num_bits + 1)) - 1) << self.bit
        self.lsb_first = lsb_first
        self.sign_bit = (1 << (num_bits - 1)) if signed else 0
        self.buffer = bytearray(register_width)

    def __get__(self, obj, objtype=None) -> int:
        obj.i2c_device.i2c.readfrom_mem_into(obj.i2c_device.address, self.register, self.buffer)
        reg = self.buffer[self.byte] & self.mask >> self.bit

        # LSB ???

        # Signed
        if reg & self.sign_bit:
            reg -= 2 * self.sign_bit
        return reg

    def __set__(self, obj, value: int) -> None:
        # Get buffer
        obj.i2c_device.i2c.readfrom_mem_into(obj.i2c_device.address, self.register, self.buffer)
        # LSB ???

        # Signed

        # Change bit
        self.buffer[self.byte] = self.buffer[self.byte] & ~self.mask | (value & self.mask << self.bit)
        # Write
        obj.i2c_device.i2c.writeto_mem(obj.i2c_device.address, self.register, self.buffer)


class ROBits(RWBits):
    def __set__(self, obj, value: int) -> None:
        raise AttributeError()

gc.collect()


# =========================== #
#            Bytes            #
# =========================== #


class Struct:
    """ Arbitrary structure register that is readable and writeable. """

    def __init__(self, register_address: int, struct_format: str) -> None:
        self.register = register_address
        self.format = struct_format

    def __get__(self, obj, objtype=None) -> tuple:
        buffer = bytearray(struct.calcsize(self.format))
        obj.i2c_device.i2c.readfrom_mem_into(obj.i2c_device.address, self.register, buffer)
        return struct.unpack_from(self.format, buffer)

    def __set__(self, obj, value: tuple) -> None:
        buffer = bytearray(struct.calcsize(self.format))
        struct.pack_into(self.format, buffer, 0, *value)
        obj.i2c_device.i2c.writeto_mem(obj.i2c_device.address, self.register, buffer)


class UnaryStruct:
    """ Arbitrary single value structure register that is readable and writeable. """
    def __init__(self, register_address: int, struct_format: str):
        self.register = register_address
        self.format = struct_format

    def __get__(self, obj, objtype=None):
        buffer = bytearray(struct.calcsize(self.format))
        obj.i2c_device.i2c.readfrom_mem_into(obj.i2c_device.address, self.register, buffer)
        return struct.unpack_from(self.format, buffer)[0]

    def __set__(self, obj, value) -> None:
        buffer = bytearray(struct.calcsize(self.format))
        struct.pack_into(self.format, buffer, 0, value)
        obj.i2c_device.i2c.writeto_mem(obj.i2c_device.address, self.register, buffer)


class ROUnaryStruct(UnaryStruct):
    def __set__(self, obj, value) -> None:
        raise AttributeError()


gc.collect()


# =========================== #
#           Datetime          #
# =========================== #

def _bcd2bin(value: int) -> int:
    return value - 6 * (value >> 4)


def _bin2bcd(value: int) -> int:
    return value + 6 * (value // 10)


class BCDDateTimeRegister:
    """ Date and time register using binary coded decimal structure. """

    def __init__(self, register_address: int, weekday_first: bool = True, weekday_start: int = 1) -> None:
        self.buffer = bytearray(7)
        self.register = register_address
        self.weekday_offset = int(not weekday_first)
        self.weekday_start = weekday_start
        # Masking value list   n/a  sec min hr day wkday mon year
        self.mask_datetime = b"\xFF\x7F\x7F\x3F\x3F\x07\x1F\xFF"

    def __get__(self, obj, objtype=None) -> tuple:
        obj.i2c_device.i2c.readfrom_mem_into(obj.i2c_device.address, self.register, self.buffer)
        return (
                _bcd2bin(self.buffer[6] & self.mask_datetime[7]) + 2000,
                _bcd2bin(self.buffer[5] & self.mask_datetime[6]),
                _bcd2bin(self.buffer[4 - self.weekday_offset] & self.mask_datetime[3]),
                _bcd2bin(self.buffer[2] & self.mask_datetime[3]),
                _bcd2bin(self.buffer[1] & self.mask_datetime[2]),
                _bcd2bin(self.buffer[0] & self.mask_datetime[1]),
                _bcd2bin(
                    (self.buffer[3 + self.weekday_offset] & self.mask_datetime[4])
                    - self.weekday_start
                ),
                -1,
                -1,
            )

    def __set__(self, obj, value: tuple) -> None:
        self.buffer[0] = _bin2bcd(value[5]) & 0x7F  # format conversions
        self.buffer[1] = _bin2bcd(value[4])
        self.buffer[2] = _bin2bcd(value[3])
        self.buffer[3 + self.weekday_offset] = _bin2bcd(
            value[6] + self.weekday_start
        )
        self.buffer[4 - self.weekday_offset] = _bin2bcd(value[2])
        self.buffer[5] = _bin2bcd(value[1])
        self.buffer[6] = _bin2bcd(value[0] - 2000)
        obj.i2c_device.i2c.writeto_mem(obj.i2c_device.address, self.register, self.buffer)


# =========================== #
#            Alarm            #
# =========================== #

ALARM_COMPONENT_DISABLED = 0x80
FREQUENCY = ["secondly", "minutely", "hourly", "daily", "weekly", "monthly"]

class BCDAlarmTimeRegister:

    def __init__(self, register_address: int, has_seconds: bool = True,
                 weekday_shared: bool = True, weekday_start: int = 1) -> None:
        buffer_size = 4
        if weekday_shared:
            buffer_size -= 1
        if has_seconds:
            buffer_size += 1
        self.has_seconds = has_seconds
        self.buffer = bytearray(buffer_size)
        self.register = register_address
        self.weekday_shared = weekday_shared
        self.weekday_start = weekday_start

    def __get__(self, obj, objtype=None):
        obj.i2c_device.i2c.readfrom_mem_into(obj.i2c_device.address, self.register, self.buffer)
        i = 0

        # Seconds
        seconds = 0
        if self.has_seconds:
            if (self.buffer[i] & 0x80) != 0:
                frequency = "secondly"
            else:
                frequency = "minutely"
                seconds = _bcd2bin(self.buffer[i] & 0x7F)
            i += 1
        else:
            frequency = "minutely"
            seconds = _bcd2bin(self.buffer[i] & 0x7F)

        # Minutes
        minute = 0
        if (self.buffer[i] & 0x80) == 0:
            frequency = "hourly"
            minute = _bcd2bin(self.buffer[i] & 0x7F)

        # Hours
        hour = 0
        if (self.buffer[i + 1] & 0x80) == 0:
            frequency = "daily"
            hour = _bcd2bin(self.buffer[i + 1] & 0x7F)

        # Weekday
        mday = None
        wday = None
        if (self.buffer[i + 2] & 0x80) == 0:
            # day of the month
            if not self.weekday_shared or (self.buffer[i + 2] & 0x40) == 0:
                frequency = "monthly"
                mday = _bcd2bin(self.buffer[i + 2] & 0x3F)
            else:  # weekday
                frequency = "weekly"
                wday = _bcd2bin(self.buffer[i + 2] & 0x3F) - self.weekday_start

        # Weekday
        if not self.weekday_shared and (self.buffer[i + 3] & 0x80) == 0:
            frequency = "monthly"
            mday = _bcd2bin(self.buffer[i + 3] & 0x7F)

        if mday is not None:
            wday = (mday - 2) % 7
        elif wday is not None:
            mday = wday + 2
        else:
            # Jan 1, 2017 was a Sunday (6)
            wday = 6
            mday = 1

        return (
            time.struct_time((2017, 1, mday, hour, minute, seconds, wday, mday, -1)),
            frequency,
        )

    def __set__(self, obj, value) -> None:
        if len(value) != 2:
            raise ValueError("Value must be sequence of length two")
        # Turn all components off by default.
        for i in range(len(self.buffer) - 1):
            self.buffer[i + 1] = ALARM_COMPONENT_DISABLED
        frequency_name = value[1]
        error_message = "%s is not a supported frequency" % frequency_name
        if frequency_name not in FREQUENCY:
            raise ValueError(error_message)

        frequency = FREQUENCY.index(frequency_name)
        if frequency < 1 and not self.has_seconds:
            raise ValueError(error_message)

        # i is the index of the minute byte
        i = 1 if self.has_seconds else 0

        if frequency > 0 and self.has_seconds:  # minutely at least
            self.buffer[0] = _bin2bcd(value[0].tm_sec)

        if frequency > 1:  # hourly at least
            self.buffer[i] = _bin2bcd(value[0].tm_min)

        if frequency > 2:  # daily at least
            self.buffer[i + 1] = _bin2bcd(value[0].tm_hour)

        if value[1] == "weekly":
            if self.weekday_shared:
                self.buffer[i + 2] = (
                    _bin2bcd(value[0].tm_wday + self.weekday_start) | 0x40
                )
            else:
                self.buffer[i + 3] = _bin2bcd(value[0].tm_wday + self.weekday_start)
        elif value[1] == "monthly":
            self.buffer[i + 2] = _bin2bcd(value[0].tm_mday)

        obj.i2c_device.i2c.writeto_mem(obj.i2c_device.address, self.register, self.buffer)

