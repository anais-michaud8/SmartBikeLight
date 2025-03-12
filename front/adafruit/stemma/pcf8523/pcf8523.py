# SPDX-FileCopyrightText: 2016 Philip R. Moyer for Adafruit Industries
# SPDX-FileCopyrightText: 2016 Radomir Dopieralski for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`pcf8523` - PCF8523 Real Time Clock module
==========================================

This library supports the use of the PCF8523-based RTC in CircuitPython. It
contains a base RTC class used by all Adafruit RTC libraries. This base
class is inherited by the chip-specific subclasses.

Functions are included for reading and writing registers and manipulating
datetime objects.

Author(s): Philip R. Moyer and Radomir Dopieralski for Adafruit Industries.
Date: November 2016
Affiliation: Adafruit Industries

Implementation Notes
--------------------

**Hardware:**

* Adafruit `Adalogger FeatherWing - RTC + SD Add-on <https://www.adafruit.com/products/2922>`_
  (Product ID: 2922)
* Adafruit `PCF8523 RTC breakout <https://www.adafruit.com/products/3295>`_ (Product ID: 3295)

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

* Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice

**Notes:**

#. Milliseconds are not supported by this RTC.
#. The alarm does not support seconds. It will always fire on full minutes.
#. Datasheet: http://cache.nxp.com/documents/data_sheet/PCF8523.pdf

"""

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_PCF8523.git"

from machine import I2C

from front.adafruit.i2c import I2CDevice, RWBit, RWBits,ROBit, BCDDateTimeRegister, BCDAlarmTimeRegister

STANDARD_BATTERY_SWITCHOVER_AND_DETECTION = 0b000
BATTERY_SWITCHOVER_OFF = 0b111


class PCF8523:
    """Interface to the PCF8523 RTC.

    :param ~busio.I2C i2c_bus: The I2C bus the device is connected to

    **Quickstart: Importing and using the device**

        Here is an example of using the :class:`PCF8523` class.
        First you will need to import the libraries to use the sensor

        .. code-block:: python

            import time
            import board
            import adafruit_pcf8523

        Once this is done you can define your `board.I2C` object and define your sensor object

        .. code-block:: python

            i2c = board.I2C()  # uses board.SCL and board.SDA
            rtc = adafruit_pcf8523.PCF8523(i2c)

        Now you can give the current time to the device.

        .. code-block:: python

            t = time.struct_time((2017, 10, 29, 15, 14, 15, 0, -1, -1))
            rtc.datetime = t

        You can access the current time accessing the :attr:`datetime` attribute.

        .. code-block:: python

            current_time = rtc.datetime

    """

    # True if the device has lost power since the time was set
    lost_power = RWBit(0x03, 7)  # True if the device has lost power since the time was set

    # Power management state that dictates battery switchover, power sources and low battery detection.
    # Defaults to BATTERY_SWITCHOVER_OFF (0b111)
    power_management = RWBits(3, 0x02, 5)

    # Current date and time.
    # The False means that day comes before weekday in the registers. The 0 is that the first day of the week is value 0 and not 1.
    datetime_register = BCDDateTimeRegister(0x03, False, 0)

    # Alarm time for the first alarm. Note that the value of the seconds-fields is ignored
    # i.e. alarms only fire at full minutes. For short-term alarms, use a timer instead.
    # The False means that day and weekday share a register. The 0 is that the first day of the week is value 0 and not 1.
    alarm = BCDAlarmTimeRegister(
        0x0A, has_seconds=False, weekday_shared=False, weekday_start=0
    )

    # True if the interrupt pin will output when alarm is alarming.
    alarm_interrupt = RWBit(0x00, 1)

    # True if alarm is alarming. Set to False to reset.
    alarm_status = RWBit(0x01, 3)

    # True if the battery is low and should be replaced.
    battery_low = ROBit(0x02, 2)

    # True for high oscillator capacitance (12.5pF), otherwise lower (7pF)
    high_capacitance = RWBit(0x00, 7)

    # False to apply the calibration offset every 2 hours (1 LSB = 4.340ppm). True to offset every minute (1 LSB = 4.069ppm).
    # The default, False, consumes less power. See datasheet figures 28-31 for details.
    calibration_schedule_per_minute = RWBit(0x0E, 7)

    # Calibration offset to apply, from -64 to +63. See the PCF8523 datasheet figure 18 for the offset calibration calculation workflow.
    calibration = RWBits(
        7, 0xE, 0, signed=True
    )

    def __init__(self, i2c_bus: I2C):
        self.i2c_device = I2CDevice(i2c_bus, 0x68)

    @property
    def datetime(self) -> tuple[int, int, int, int, int, int, int, int, int]:
        """ Date: tuple(year, month, day, hours, minutes, seconds, wday, yday, isdst) """
        return self.datetime_register

    @datetime.setter
    def datetime(self, value: tuple[int, int, int, int, int, int, int, int, int]):
        """ Date: tuple(year, month, day, hours, minutes, seconds, wday, yday, isdst) """
        # Automatically sets lost_power to false.
        self.power_management = STANDARD_BATTERY_SWITCHOVER_AND_DETECTION
        self.datetime_register = value
