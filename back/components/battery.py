
import gc
gc.collect()

import board
import time

from micropython import const
from adafruit_bus_device import i2c_device

__version__ = "2.3.5"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_LC709203F.git"

LC709203F_I2CADDR_DEFAULT = const(0x0B)
LC709203F_CMD_INITRSOC = const(0x07)
LC709203F_CMD_CELLITE = const(0x0F)
LC709203F_CMD_CELLVOLTAGE = const(0x09)


class LC709203F:
    """Interface library for LC709203F battery monitoring and fuel gauge sensors

    :param ~busio.I2C i2c_bus: The I2C bus the device is connected to
    :param int address: The I2C device address. Defaults to :const:`0x0B`

    """

    def __init__(self, i2c_bus: board.I2C, address: int = LC709203F_I2CADDR_DEFAULT) -> None:
        value_exc = None
        for _ in range(3):
            try:
                self.i2c_device = i2c_device.I2CDevice(i2c_bus, address)
                break
            except ValueError as exc:
                value_exc = exc
                # Wait a bit for the sensor to wake up.
                time.sleep(0.1)
        else:
            raise value_exc

        self._buf = bytearray(10)
        time.sleep(0.1)
        self.init_RSOC()
        time.sleep(0.1)

    def init_RSOC(self) -> None:  # pylint: disable=invalid-name
        """Initialize the state of charge calculator"""
        self._write_word(LC709203F_CMD_INITRSOC, 0xAA55)

    @property
    def cell_percent(self) -> float:
        """Returns percentage of cell capacity"""
        return self._read_word(LC709203F_CMD_CELLITE) / 10

    @property
    def cell_voltage(self) -> float:
        """Returns floating point voltage"""
        return self._read_word(LC709203F_CMD_CELLVOLTAGE) / 1000

    # pylint: disable=no-self-use
    def _generate_crc(self, data) -> int:
        """8-bit CRC algorithm for checking data"""
        crc = 0x00
        # calculates 8-Bit checksum with given polynomial
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ 0x07
                else:
                    crc <<= 1
                crc &= 0xFF
        return crc

    def _read_word(self, command: int) -> int:
        self._buf[0] = LC709203F_I2CADDR_DEFAULT * 2  # write byte
        self._buf[1] = command  # command / register
        self._buf[2] = self._buf[0] | 0x1  # read byte

        with self.i2c_device as i2c:
            i2c.write_then_readinto(
                self._buf, self._buf, out_start=1, out_end=2, in_start=3, in_end=7
            )
        crc8 = self._generate_crc(self._buf[0:5])
        if crc8 != self._buf[5]:
            raise OSError("CRC failure on reading word")
        return (self._buf[4] << 8) | self._buf[3]

    def _write_word(self, command: int, data: int) -> None:
        self._buf[0] = LC709203F_I2CADDR_DEFAULT * 2  # write byte
        self._buf[1] = command  # command / register
        self._buf[2] = data & 0xFF
        self._buf[3] = (data >> 8) & 0xFF
        self._buf[4] = self._generate_crc(self._buf[0:4])

        with self.i2c_device as i2c:
            i2c.write(self._buf[1:5])



class BatteryMonitor:
    def __init__(self):
        self.i2c = board.I2C()
        try:
            self.sensor = LC709203F(self.i2c, 0x0b)
        except Exception:
            pass

    @property
    def value(self) -> int:
        return int(self.sensor.cell_percent if hasattr(self, "sensor") else 0)


gc.collect()

