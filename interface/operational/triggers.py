
# Memory
import gc
gc.collect()

# Built-in
import asyncio

# Local -> Interface
from interface.basic.utils import to_list
from interface.basic.average import Average
from interface.basic.logger import Logging


# Memory used to make class: 848 | Collect: 1232
# Memory used to make object: 80 | Collect: 240


class Action:

    def __init__(self, *, funcs=None, events=None, coroutines=None, event_loop=None,
                 name=None, is_logging=None, style=None):
        self.logging = Logging(name, is_logging, self, style=style)

        if funcs is not None:
            self.funcs = to_list(funcs)
        if events is not None:
            self.events = to_list(events)
        if coroutines is not None:
            self.coroutines = to_list(coroutines)
        if event_loop is not None:
            self.event_loop = event_loop

    def callback(self, *args, **kwargs):
        """ Call all functions, set events and schedule coroutines """
        if hasattr(self, "funcs"):
            for func in self.funcs:
                func(*args, **kwargs)
        if hasattr(self, "events"):
            for event in self.events:
                event.set()
        if hasattr(self, "coroutines"):
            for coro in self.coroutines:
                self.event_loop.call_soon(coro, *args)

    def __call__(self, *args, **kwargs):
        self.callback(*args, **kwargs)

    def add(self, funcs=None, events=None, coroutines=None, event_loop=None):
        self.logging("Adding to action", level="TRACE")
        if funcs is not None:
            if hasattr(self, "funcs"):
                self.funcs += to_list(funcs)
            else:
                self.funcs = to_list(funcs)
        if events is not None:
            if hasattr(self, "events"):
                self.events += to_list(events)
            else:
                self.events = to_list(events)
        if coroutines is not None:
            if hasattr(self, "coroutines"):
                self.coroutines += to_list(coroutines)
            else:
                self.coroutines = to_list(coroutines)
        if event_loop is not None:
            self.event_loop = event_loop
        return self


gc.collect()


class Refresher(Action):
    def __init__(self, *, irq = None,
                 funcs=None, events=None, coroutines=None, event_loop=None,
                 name=None, is_logging=None, style=None,
                 wait_refresh: int | float = 0.05, wait_change: int | float | None = None,
                 initially_active: bool = True, uses_active: bool = True,
                 ):
        super().__init__(
            funcs=funcs, events=events, coroutines=coroutines, event_loop=event_loop,
            name=name, is_logging=is_logging, style=style
        )

        # Wait times
        self.wait_refresh = wait_refresh
        self.wait_change = wait_change

        # Interrupt
        if irq is not None:
            self.irq = irq

        # Active
        if uses_active:
            if irq is not None:
                self._active = False
            else:
                self.active = asyncio.Event()
            if initially_active:
                self.resume()
        # Always active
        else:
            if irq is not None:
                self.irq.irq(True, self.callback)

    def update(self):
        return self.callback()

    @property
    def is_active(self) -> bool:
        return self.active.is_set() if hasattr(self, "active") else self._active if hasattr(self, "_active") else True

    def pause(self):
        self.logging("Pausing", level="INFO")
        if hasattr(self, "irq"):
            self._active = False
            self.irq.irq(False, self.callback)
        else:
            self.active.clear()

    def resume(self):
        self.logging("Resuming", level="INFO")
        if hasattr(self, "irq"):
            self._active = True
            self.irq.irq(True, self.callback)
        else:
            self.active.set()

    def set_activation(self, value: bool):
        if not value:
            self.pause()
        else:
            self.resume()

    def toggle_activation(self, _=None):
        self.set_activation(not self.is_active)

    async def refreshing(self):
        """ (Async) Continuously refreshes. When paused waits for active """
        while True:
            if hasattr(self, "active"):
                await self.active.wait()
            res = self.update()
            if res is True and self.wait_change is not None:
                await asyncio.sleep(self.wait_change)
            await asyncio.sleep(self.wait_refresh)


gc.collect()


class Trigger(Refresher):
    def __init__(self, *, source, irq: bool = False, initial=None,
                 get_input=None, check_value: bool = True, check_input: bool = True,
                 name: str = None, is_logging: bool = None, style: str = None,
                 funcs=None, events=None, coroutines=None, event_loop=None,
                 wait_refresh: int | float = 0.05, wait_change: int | float = None,
                 avg_input: int | None = None, avg_value: int | None = None,
                 initially_active: bool = True, uses_active: bool = True,
                 ):
        super().__init__(
            irq=source if irq else None,
            funcs=funcs, events=events, coroutines=coroutines, event_loop=event_loop,
            name=name, is_logging=is_logging, style=style,
            wait_refresh=wait_refresh, wait_change=wait_change, initially_active=initially_active, uses_active=uses_active
        )
        gc.collect()

        self.logging(f"Making trigger with initial: '{initial}'")

        self.source = source
        self._value = initial
        self._inputted = None
        if get_input is not None:
            self._get_input = get_input
        self._check_value = check_value
        self._check_input = check_input

        if isinstance(avg_input, int) and avg_input > 0:
            self.avg_input = Average(avg_input)
        if isinstance(avg_value, int) and avg_value > 0:
            self.avg_value = Average(avg_value)
        gc.collect()

    # Inputted (from the source and or get_input)

    @property
    def inputted(self):
        return self._inputted

    @inputted.setter
    def inputted(self, value):
        self.set_input(value)

    def set_input(self, value, callback: bool = True):
        self.logging(f"Update (input setter): {value} | Was: {self.inputted}", level="TRACE")
        if self.check(value, "_inputted",  "avg_input", self._check_input):
            # Check value, if different continue
            if self.check(self.get_value(), "_value", "avg_value",self._check_value):
                # Call action
                if callback:
                    self.callback(self.value)
                return True
        return False

    def get_input(self):
        """ Get the input from the source """
        return self.source.value if not hasattr(self, "_get_input") else self._get_input(self.source)

    # Value (from inputted through func)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.set_value(value)

    def set_value(self, value, callback: bool = True):
        self.logging(f"Update (value setter): {value} | Was: {self.value}", level="TRACE")
        # Check value, if different continue
        if self.check(value, "_value", "avg_value",self._check_value):
            # Call action
            if callback:
                self.callback(self.value)
            return True
        return False

    def get_value(self):
        """ Get the value from the input"""
        return self.inputted

    # Update

    def check(self, value, attr: str, average: str, checking: bool = True):
        if hasattr(self, average):
            getattr(self, average)(value)
            value = float(getattr(self, average))
        if getattr(self, attr) != value:
            setattr(self, attr, value)
            return True
        return False if checking else True

    def update(self) -> bool:
        # Check input from source, if different continue
        if self.check(self.get_input(), "_inputted","avg_input", self._check_input):
            # Check value, if different continue
            if self.check(self.get_value(), "_value", "avg_value",self._check_value):
                self.logging(f"Update: {self.value}", level="TRACE")
                # Call action
                self.callback(self.value)
                return True
        return False



gc.collect()

