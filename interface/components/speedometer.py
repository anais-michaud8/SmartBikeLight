
import gc
gc.collect()

import time

from interface.basic.utils import rounder
from interface.basic.converters import linear_speed_to_period, kmh_to_ms, ms_to_kmh, period_to_linear_speed, acceleration, displacement, km_to_miles
from interface.basic.average import Average
from interface.operational.timer import TriggerTimer


# =========================== #
#           Classes           #
# =========================== #


class Speedometer(TriggerTimer):
    """ Uses a Timer to reset the counter to 0 each _ seconds. Before resetting it gets the speed from the counts. """
    def __init__(self, radius: float = 0.25, min_speed: float = 1,
                 unit: int = 0, rounding: int = 2, points: int = 5,
                 max_speed: float = 0, odometer: float = 0, total_duration: float = 0,
                 attr: str = "acceleration", wait_refresh: int | float = 0.1,
                 name: str = None, is_logging: bool = None, style: str = None,
                 initially_active: bool = True, uses_active: bool = True,):
        """

        Args:
            radius ():
                The radius of the wheel in meters.
            min_speed ():
                The minimum speed possible in m/s.
            unit ():
                Unit for the speed (value). 0 for m/s, 1 for km/h and 1 for mph.
            rounding ():
                The decimal place to round the data.
            max_speed ():
                The maximum speed (from records).
            odometer ():
                The current distance (from records).
            attr ():
                The attribute to compare.
            wait_refresh ():
            name ():
            is_logging ():
            style ():
            initially_active ():
            uses_active ():
        """

        # Specifications
        self._radius = radius
        self._period_at_min_speed = linear_speed_to_period(min_speed, self._radius)
        self.rounding = rounding
        self.attr = attr
        self.unit = unit

        # Hall Sensor
        self._time_last = None
        self._period_last = None

        # Data
        self._estimated_period = 0
        self._period = 0
        self._speed = 0
        self._acceleration = 0
        self._distance = 0

        # Records
        self._max_speed = kmh_to_ms(max_speed) if self.unit == 1 else ms_to_kmh(kmh_to_ms(max_speed)) if self.unit == 2 else max_speed
        self._odometer = kmh_to_ms(odometer) if self.unit == 1 else ms_to_kmh(kmh_to_ms(odometer)) if self.unit == 2 else odometer
        self._total_duration = total_duration
        self.start = self.now

        # Average
        self.average_speed = Average(points)

        super().__init__(
            name=name, is_logging=is_logging, style=style,
            funcs=self.calculate, wait_refresh=wait_refresh, initially_active=initially_active, uses_active=uses_active,
        )

    # Radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._period_at_min_speed = linear_speed_to_period(
            period_to_linear_speed(self._period_at_min_speed, self._radius), value
        )
        self._radius = value

    # To edit when using a different way to get time

    @property
    def now(self):
        return rounder(time.time(), self.rounding)

    def diff(self, before=None, now=None):
        return rounder(
            (self.now if now is None else now) - (self._time_last if before is None else before),
            self.rounding
        )

    # Callbacks (Hall sensor and Speedometer)

    def count(self, _=None):
        """ Hall sensor calls this function each time the sensor detects a magnetic field (each revolution). """
        if self._time_last is None:
            self._time_last = self.now
        else:
            self._period_last = self.diff()
            self._time_last = self.now

    def calculate(self, _=None):
        # Not on
        if self._period_last is None or self._time_last is None:
            return

        # New revolution
        if self._period_last != self._period:
            self._period = self._period_last
            self._estimated_period = self._period
        # Speed is at minimum
        elif self._period_at_min_speed <= self.diff():
            self._period = 0
            self._estimated_period = self._period
            self._speed = 0
            self._acceleration = 0
            self._period_last = None
            self._time_last = None
            return
        # Speed is decreasing
        elif self._period_last < self.diff():
            self._estimated_period = self.diff()
        # Same as before
        else:
            return

        # Calculate speed...
        speed = period_to_linear_speed(self._estimated_period, self._radius)

        # Average
        self.average_speed.collect(speed)
        avg = float(self.average_speed)

        # Data
        self._acceleration = rounder(acceleration(self._speed, avg, self._estimated_period), self.rounding)
        self._distance += rounder(displacement(avg, self._speed, self._estimated_period), self.rounding)
        self._speed = rounder(avg, self.rounding)

        # Records
        self._max_speed = max(self._max_speed, self._speed)
        gc.collect()

    # Speed (SI units, European, Imperial)

    @property
    def max_speed(self):
        return rounder(
            ms_to_kmh(km_to_miles(self._max_speed)) if self.unit == 2
                else ms_to_kmh(self._max_speed) if self.unit == 1 else self._max_speed,
            self.rounding
        )

    @property
    def speed(self):
        return self.mph if self.unit == 2 else self.kmh if self.unit == 1 else self.ms

    @property
    def kmh(self):
        return rounder(ms_to_kmh(self._speed), self.rounding)

    @property
    def mph(self):
        return rounder(km_to_miles(self.kmh), self.rounding)

    @property
    def ms(self):
        return rounder(self._speed, self.rounding)

    # Distance (SI units, European, Imperial)

    @property
    def distance(self):
        return self.miles if self.unit == 2 else self.kilometers if self.unit == 1 else self.meters

    @property
    def kilometers(self):
        return rounder(self._distance / 1000, self.rounding)

    @property
    def miles(self):
        return rounder(km_to_miles(self._distance / 1000), self.rounding)

    @property
    def meters(self):
        return rounder(self._distance, self.rounding)

    # Acceleration (only in SI units)

    @property
    def acceleration(self):
        return rounder(self._acceleration, self.rounding)

    # Duration / Odometer

    @property
    def duration(self) -> int:
        return int(self.diff(before=self.start))

    @property
    def total_duration(self) -> int:
        return int(self._total_duration + self.duration)

    @property
    def odometer(self) -> float:
        return rounder(
            km_to_miles((self._odometer + self._distance)/1000) if self.unit == 2
                else (self._odometer + self._distance)/1000 if self.unit == 1 else self._odometer + self._distance,
            self.rounding
        )

    # Value

    @property
    def value(self):
        return getattr(self, self.attr)


gc.collect()

