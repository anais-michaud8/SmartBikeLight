
import gc
gc.collect()

import time
import asyncio

from interface.basic.converters import float_to_hm, date_formatter, time_formatter

# Constants

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


class SimulatedClock:
    def __init__(self):
        self._time_diff = 0

    @property
    def datetime(self) -> tuple[int, int, int, int, int, int, int, int, int]:
        """ Date: tuple(year, month, day, hours, minutes, seconds, wday, yday, isdst) """
        current_time = time.localtime(time.time() + self._time_diff)
        return (current_time.tm_year, current_time.tm_mon, current_time.tm_mday,
                current_time.tm_hour, current_time.tm_min, current_time.tm_sec,
                current_time.tm_wday, current_time.tm_yday, current_time.tm_isdst)

    @datetime.setter
    def datetime(self, value: tuple[int, int, int, int, int, int, int, int, int]):
        """ Date: tuple(year, month, day, hours, minutes, seconds, wday, yday, isdst) """
        # Calculate the difference between the new time and the current system time
        new_time = time.mktime(value)
        current_system_time = time.time()
        self._time_diff = new_time - current_system_time


gc.collect()


class ClockProperty:
    def __init__(self, n: int = 0):
        self.n = n

    def __get__(self, instance: 'Clock', owner: type['Clock'] = None):
        return instance.datetime[self.n]

    def __set__(self, instance: 'Clock', value: 'Clock'):
        if self.n != 8:
            instance.datetime = instance.datetime[0:self.n] + (value,) + instance.datetime[self.n+1:]
        else:
            instance.datetime = instance.datetime[0:self.n] + (value,)


gc.collect()


class Clock:

    years = ClockProperty(0)
    months = ClockProperty(1)
    days = ClockProperty(2)
    hours = ClockProperty(3)
    minutes = ClockProperty(4)
    seconds = ClockProperty(5)
    wday = ClockProperty(6)
    yday = ClockProperty(7)
    isdst = ClockProperty(8)

    def __init__(self, rtc=None, api = None, use_change: bool = True,
                 initialise_from_rtc: bool = False, initialise_from_api: bool = False) -> None:
        self.rtc = rtc
        self.api = api
        self.clock = SimulatedClock() if rtc is None else rtc

        if use_change:
            self.change = self.clock.change if hasattr(self.clock, "change") else asyncio.Event()

        if initialise_from_rtc and rtc is not None:
            self.initialise_from_rtc()
        elif initialise_from_api and api is not None:
            self.initialise_from_api()

    # Initialisation and datetime

    def initialise_from_rtc(self):
        self.datetime = self.rtc.datetime

    def initialise_from_api(self):
        self.api.make_date_from_ip()
        self.datetime = self.api.datetime

    @property
    def datetime(self) -> tuple[int, int, int, int, int, int, int, int, int]:
        """ Date: tuple(year, month, day, hours, minutes, seconds, wday, yday, isdst) """
        return self.clock.datetime

    @datetime.setter
    def datetime(self, value: tuple[int, int, int, int, int, int, int, int, int]):
        """ Date: tuple(year, month, day, hours, minutes, seconds, wday, yday, isdst) """
        self.clock.datetime = value
        if hasattr(self, "change"):
            self.change.set()

    @property
    def unix(self) -> float:
        return time.mktime(self.datetime)

    # Date

    @property
    def date(self):
        return f"{self.years:04}-{self.months:02}-{self.days:02}"

    def date_with_unit(self, unit: int = 0):
        return date_formatter(self.years, self.months, self.days, unit)

    # Time

    @property
    def full_time(self):
        return f"{self.hours}:{self.minutes}:{self.seconds}"

    @property
    def time(self):
        return f"{self.hours}:{self.minutes}"

    def time_with_unit(self, unit: int = 0):
        return time_formatter(self.value, unit)

    # Datetime

    @property
    def iso(self):
        return f"{self.years:04}-{self.months:02}-{self.days:02}T{self.hours}:{self.minutes}:{self.seconds}Z"

    @property
    def weekday(self):
        return WEEKDAYS[self.wday] if 0 < self.wday < 7 else "Unknown"

    @property
    def nth(self) -> str:
        if self.days == 1 or self.days == 21 or self.days == 31:
            return "st"
        elif self.days == 2 or self.days == 22:
            return "nd"
        elif self.days == 3 or self.days == 23:
            return "rd"
        return "th"

    @property
    def month(self) -> str:
        return MONTHS[self.months] if 0 < self.months < 12 else "Unknown"

    @property
    def english(self):
        return f"{self.weekday} {self.days}{self.nth} of {self.month} {self.years}"

    # Time in hours (+minutes)

    @property
    def value(self) -> float:
        return self.hours + self.minutes / 60

    @value.setter
    def value(self, value: float) -> None:
        self.hours, self.minutes = float_to_hm(value)

    # Dunder

    def __repr__(self) -> str:
        return self.english

    def __str__(self) -> str:
        return self.iso


gc.collect()

