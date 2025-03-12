
# Built-in
import time

# Interface
from interface.basic.utils import rounder
from interface.components.speedometer import Speedometer as _Speedometer

class Speedometer(_Speedometer):

    # To edit when using a different way to get time

    @property
    def now(self):
        return time.ticks_ms()

    def diff(self, before=None, now=None):
        return rounder(
            time.ticks_diff(
                (self.now if now is None else now), (self._time_last if before is None else before)
            )/1000,
            self.rounding
        )
