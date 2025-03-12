
# Memory
import gc
gc.collect()

# Built-in
import time

# Local -> Interface
from interface.basic.scale import Scale
from interface.basic.operators import get_operator, get_operator_expand
from interface.operational.triggers import Trigger

# =========================== #
#          Functions          #
# =========================== #


def debounce(inputted: bool, value: bool) -> bool:
    return not value if inputted else bool(value)

def scaled(inputted: bool, last: bool, scale: Scale, down: bool = False) -> tuple[bool, Scale]:
    new = debounce(inputted, last)
    if new != last:
        if down:
            scale.down()
        else:
            scale.up()
    return new, scale

def comparison(inputted: float, operator, lower: float, higher: float | None = None) -> bool:
    return operator(lower, higher, inputted) if higher is not None else operator(lower, inputted)


def ranging(value: int | float, from_low: int | float, from_high: int | float,
            to_low: int | float, to_high: int | float, step: int | float | None = None, inverse: bool = False) -> int | float:
    # Clamp the value to the from range
    value = max(min(value, from_high), from_low)

    # Calculate the mapped value
    mapped_value = (value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low

    # Adjust the mapped value to the nearest step if step is provided
    if step is not None:
        mapped_value = ((mapped_value - to_low) // step + (1 if (mapped_value - to_low) % step != 0 else 0)) * step + to_low

    return mapped_value if not inverse else to_high-mapped_value

gc.collect()


class Input:
    def __init__(self, initial=None):
        self.value = initial


# =========================== #
#           Specific          #
# =========================== #


class TriggerButton(Trigger):
    def __init__(self, *, source, irq: bool = False, initial: bool = False,
                 get_input=None, check_value: bool = True, check_input: bool = True,
                 name: str = None, is_logging: bool = None, style: str = None,
                 funcs=None, events=None, coroutines=None, event_loop=None,
                 wait_refresh: int | float = 0.05, wait_change: int | float = None,
                 initially_active: bool = True, uses_active: bool = True,
                 ):
        super().__init__(
            source=source, irq=irq, initial=initial, get_input=get_input, check_value=check_value, check_input=check_input,
            funcs=funcs, events=events, coroutines=coroutines, event_loop=event_loop,
            name=name, is_logging=is_logging, style=style,
            wait_refresh=wait_refresh, wait_change=wait_change, initially_active=initially_active, uses_active=uses_active,
        )

    def get_value(self) -> bool:
        return debounce(self.inputted, self.value)

    def set_value(self, value, callback: bool = True) -> bool:
        return super().set_value(bool(value))

    def call_as_empty(self, _=None):
        self.inputted = not self.inputted

gc.collect()


class TriggerScale(Trigger):
    def __init__(self, *, source, irq: bool = False, initial: int | float | None = None,
                 scale: Scale | None = None, start: int = 10, end: int = 100, step: int = 10,
                 get_input=None, check_value: bool = True, check_input: bool = True,
                 avg_value: int | None = None,
                 name: str = None, is_logging: bool = None, style: str = None,
                 funcs=None, events=None, coroutines=None, event_loop=None,
                 wait_refresh: int | float = 0.05, wait_change: int | float = None,
                 initially_active: bool = True, uses_active: bool = True,
                 ):
        self._debounced = False
        self._scale = scale if isinstance(scale, Scale) else Scale(start, end, step, initial)
        if initial is not None:
            self._scale.value = initial
        super().__init__(
            source=source, irq=irq, initial=None, get_input=get_input, check_value=check_value, check_input=check_input,
            avg_value=avg_value,
            funcs=funcs, events=events, coroutines=coroutines, event_loop=event_loop,
            name=name, is_logging=is_logging, style=style,
            wait_refresh=wait_refresh, wait_change=wait_change, initially_active=initially_active, uses_active=uses_active,
        )
        self._value = self._scale.value

    def get_value(self):
        self._debounced, self._scale = scaled(self.inputted, self._debounced, self._scale)
        return self._scale.value

    def call_as_empty(self, _=None):
        self.inputted = not self.inputted


gc.collect()


class TriggerAnalog(Trigger):
    def __init__(self, *, source,
                 get_input=None, check_value: bool = True, check_input: bool = True,
                 avg_input: int | None = None, avg_value: int | None = None,
                 difference: float | None = None,
                 from_low: int | float | None = None, from_high: int | float | None = None, inverse: bool = False,
                 to_low: int | float | None = None, to_high: int | float | None = None, step: int | float | None = None,
                 name: str = None, is_logging: bool = None, style: str = None,
                 funcs=None, events=None, coroutines=None, event_loop=None,
                 wait_refresh: int | float = 0.05, wait_change: int | float = None,
                 initially_active: bool = True, uses_active: bool = True,
                 ):
        self.difference = difference
        if from_low is not None and from_high is not None and to_low is not None and to_high is not None:
            self.from_low = from_low
            self.from_high = from_high
            self.to_low = to_low
            self.to_high = to_high
            self.step = step
            self.inverse = inverse
        super().__init__(
            source=source, initial=None, get_input=get_input, check_value=check_value, check_input=check_input,
            avg_input=avg_input, avg_value=avg_value,
            funcs=funcs, events=events, coroutines=coroutines, event_loop=event_loop,
            name=name, is_logging=is_logging, style=style,
            wait_refresh=wait_refresh, wait_change=wait_change, initially_active=initially_active, uses_active=uses_active,
        )

    def get_value(self):
        if hasattr(self, 'from_low'):
            value = ranging(
                self.inputted, self.from_low, self.from_high,
                self.to_low, self.to_high, step=self.step, inverse=self.inverse,
            )
        else:
            value = self.inputted
        if self.difference is not None and value is not None and self.value is not None:
            return value if abs(value - self.value) > self.difference else self.value
        return value


gc.collect()


class TriggerComparison(Trigger):
    def __init__(self, *, source, initial: bool = False, switch: bool = False,
                 difference: bool = False, every: int | float | None = None,
                 lower: int | float = 1, upper: int | float | None = None, operator: str = "==",
                 expansion_lower: int | float = 0, expansion_upper: int | float = 0,
                 get_input=None, check_value: bool = True, check_input: bool = True,
                 avg_input: int | None = None,
                 name: str = None, is_logging: bool = None, style: str = None,
                 funcs=None, events=None, coroutines=None, event_loop=None,
                 wait_refresh: int | float = 0.05, wait_change: int | float = None,
                 initially_active: bool = True, uses_active: bool = True,
                 ):
        # Comparison
        self._lower = lower
        self._upper = upper
        self._operator = get_operator(operator, self._upper is not None)

        # Treat as switch or button ?
        if not switch:
            self._raw = initial

        # Compare the difference between last and current input instead of just the input
        if difference:
            self._last_input = None
            self._every = every if every is not None and every >= wait_refresh else wait_refresh
            self._last_time = time.time()

        # Expansion
        if expansion_lower > 0 or expansion_upper > 0:
            factor_lower, factor_upper = get_operator_expand(operator, self._upper is not None)
            self._lower_expanded = self._lower + expansion_lower * factor_lower
            self._upper_expanded = self._upper + expansion_upper * factor_upper if self._upper is not None else None

        super().__init__(
            source=source, initial=initial, get_input=get_input, check_value=check_value, check_input=check_input,
            avg_input=avg_input,
            funcs=funcs, events=events, coroutines=coroutines, event_loop=event_loop,
            name=name, is_logging=is_logging, style=style,
            wait_refresh=wait_refresh, wait_change=wait_change, initially_active=initially_active, uses_active=uses_active,
        )

    def get_value(self):
        # Use raw (aka inputted of a button) to debounce if not a switch
        value = self._raw if hasattr(self, '_raw') else self.value

        # Use difference ?
        if hasattr(self, '_last_input'):
            inputted = self.inputted - self._last_input if self._last_input is not None else 0
            if time.time() - self._last_time >= self._every:
                self._last_time = time.time()
                self._last_input = self.inputted
        else:
            inputted = self.inputted

        # If OFF or no expansion -> Use normal limits
        if not value or not hasattr(self, "_lower_expanded"):
            val = comparison(inputted, self._operator, self._lower, self._upper)
        # If ON -> Use expanded limits
        else:
            val = comparison(inputted, self._operator, self._lower_expanded, self._upper_expanded)

        # Debounce ?
        if hasattr(self, '_raw'):
            self._raw = val
            return debounce(self._raw, self.value)
        return val


gc.collect()

