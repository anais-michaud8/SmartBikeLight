
# Memory
import gc
gc.collect()

# Built-in
import asyncio

# Local -> Interface
from interface.operational.triggers import Refresher
from interface.basic.operators import get_operator
from interface.components.clock import Clock
from interface.operational.special import comparison
from interface.basic.average import Average


class TriggerTimer(Refresher):
    def __init__(self, initial: bool = False, switch: bool = False,
                 name: str = None, is_logging: bool = None, style: str = None,
                 funcs=None, events=None, coroutines=None, event_loop=None,
                 wait_refresh: int | float = 0.05,
                 initially_active: bool = True, uses_active: bool = True,):
        super().__init__(
            funcs=funcs, events=events, coroutines=coroutines, event_loop=event_loop,
            name=name, is_logging=is_logging, style=style,
            wait_refresh=wait_refresh, initially_active=initially_active, uses_active=uses_active,
        )
        self._value = initial if switch else None

    @property
    def value(self):
        return self._value

    async def refreshing(self):
        """ (Async) Continuously refreshes. When paused waits for active """
        while True:
            if hasattr(self, "active"):
                await self.active.wait()
            await asyncio.sleep(self.wait_refresh)
            if self.is_active:
                self.update()
                if self.value is not None:
                    self._value = not self.value


gc.collect()


class TriggerClock(Refresher):
    def __init__(self, source: Clock,
                 lower: float, upper: float | None = None, operator: str = "==",
                 name: str = None, is_logging: bool = None, style: str = None,
                 funcs=None, events=None, coroutines=None, event_loop=None,
                 initially_active: bool = True, uses_active: bool = True, ):
        self.source = source
        self._lower = lower
        self._upper = upper
        self._operator = get_operator(operator, self._upper is not None)

        super().__init__(
            funcs=funcs, events=events, coroutines=coroutines, event_loop=event_loop,
            name=name, is_logging=is_logging, style=style,
            initially_active=initially_active, uses_active=uses_active,
        )

    def update(self):
        self.callback(self.value)

    @property
    def inputted(self):
        return self.source.value

    @property
    def value(self):
        return comparison(self.inputted, self._operator, self._lower, self._upper)

    @property
    def next_change(self) -> float:
        if self.inputted < self._lower:
            return self._lower - self.inputted
        if isinstance(self._upper, float) or isinstance(self._upper, int):
            if self.inputted < self._upper:
                return self._upper - self.inputted
        return 24 - self.inputted + self._lower

    @property
    def change(self) -> asyncio.Event:
        return self.source.change

    async def refreshing(self):
        """ (Async) Continuously refreshes. When paused waits for active """
        last = self.value
        self.change.clear()
        while True:
            if hasattr(self, "active"):
                await self.active.wait()
            # Send update if the value has changed otherwise wait for next change
            if last != self.value:
                last = self.value
                self.update()
            try:
                # Wait for next change or change in clock
                await asyncio.wait_for(self.change.wait(), self.next_change * 3600)
                # Change in clock -> Repeat process
                self.change.clear()
            # Next change
            except asyncio.TimeoutError:
                if hasattr(self, "active"):
                    if self.is_active:
                        self.update()


gc.collect()


class ContinuousAverage(TriggerTimer):
    def __init__(self, *, source, points: int = 100,
                 name: str = None, is_logging: bool = None, style: str = None,
                 wait_refresh: int | float = 0.05, initially_active: bool = True, uses_active: bool = True,):
        self.source = source
        self.average = Average(points)

        super().__init__(
            funcs=self.collect, name=name, is_logging=is_logging, style=style,
            wait_refresh=wait_refresh, initially_active=initially_active, uses_active=uses_active,
        )

    @property
    def value(self):
        return self.average.value

    def collect(self, _=None):
        self.average(self.source.value)


gc.collect()

