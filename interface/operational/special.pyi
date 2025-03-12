

# Built-in
import asyncio
from typing import Optional, Callable, TypeAlias, Any, Union, Protocol
from machine import Pin

# Local -> Interface
from interface.basic.scale import Scale
from interface.operational.triggers import Trigger

from interface.operational.triggers import ActionEvents, ActionCoroutines

# =========================== #
#          Functions          #
# =========================== #


def debounce(inputted: bool, value: bool) -> bool:
    ...

def scaled(inputted: bool, state: bool, scale: Scale, down: bool = False) -> tuple[bool, Scale]:
    ...

def comparison(inputted: float, operator, lower: float, higher: float | None = None) -> bool:
    ...

def ranging(value: int | float, from_low: int | float, from_high: int | float,
            to_low: int | float, to_high: int | float, step: int | float | None = None, inverse: bool = False) -> int | float:
    ...


class Input:
    value: Optional[Any]
    def __init__(self, initial: Optional[Any] = None):
        ...


# =========================== #
#            Button           #
# =========================== #

ButtonInput: bool
ButtonValue: bool

ButtonActionFunction: TypeAlias = Callable[[ButtonValue], ...]
ButtonActionFuncs: TypeAlias = list[ButtonActionFunction]
ButtonActionFuncsArg: TypeAlias = Optional[ButtonActionFuncs | ButtonActionFunction]

class ButtonSourceProtocol(Protocol):
    value: ButtonInput


class ButtonIrqSource(Protocol):
    value: ButtonInput
    pin: Pin

    def irq(self, activated: bool, handler: Optional[ButtonActionFunction]):
        ...


ButtonSource: TypeAlias = ButtonSourceProtocol | ButtonIrqSource


class TriggerButton(Trigger):
    # Action
    funcs: ButtonActionFuncs
    # Refresher
    irq: ButtonIrqSource
    # Trigger
    source: ButtonSource
    _value: ButtonValue
    _inputted: ButtonInput
    _get_input: Optional[Callable[[ButtonSource], Any]]
    _check_value: bool
    _check_input: bool
    inputted: ButtonInput
    value: ButtonValue

    def __init__(self, *,
                 source: ButtonSource,
                 irq: bool = False,
                 initial: Optional[ButtonValue] = None,
                 get_input: Optional[Callable[[ButtonSource], Any]] = None,
                 check_value: bool = True,
                 check_input: bool = True,
                 funcs: ButtonActionFuncsArg = None,
                 events: Optional[ActionEvents] = None,
                 coroutines: Optional[ActionCoroutines] = None,
                 event_loop: Optional[asyncio.AbstractEventLoop] = None,
                 name: Optional[str] = None,
                 is_logging: Optional[bool] = None,
                 style: Optional[str] = None,
                 wait_refresh: int | float = 0.05,
                 wait_change: Optional[int | float] = None,
                 initially_active: bool = True,
                 uses_active: bool = True,
                 ):
        ...

    def get_value(self) -> ButtonValue:
        ...

    def add(self,
            funcs: Optional[ButtonActionFuncsArg] = None,
            events: Optional[ActionEvents] = None,
            coroutines: Optional[ActionCoroutines] = None,
            event_loop: Optional[asyncio.AbstractEventLoop] = None,
            ):
        ...

    def call_as_empty(self):
        ...


# =========================== #
#            Scale            #
# =========================== #


ScaleInput: bool
ScaleValue: int | float

ScaleActionFunction: TypeAlias = Callable[[ScaleValue], ...]
ScaleActionFuncs: TypeAlias = list[ScaleActionFunction]
ScaleActionFuncsArg: TypeAlias = Optional[ScaleActionFuncs | ScaleActionFunction]

class ScaleSourceProtocol(Protocol):
    value: ScaleInput


class ScaleIrqSource(Protocol):
    value: ScaleValue
    pin: Pin

    def irq(self, activated: bool, handler: Optional[ScaleActionFunction]):
        ...


ScaleSource: TypeAlias = ScaleSourceProtocol | ScaleIrqSource


class TriggerScale(Trigger):
    # Action
    funcs: ScaleActionFuncs
    # Refresher
    irq: ScaleIrqSource
    # Trigger
    source: ScaleSource
    _value: ScaleValue
    _inputted: ScaleInput
    _get_input: Optional[Callable[[ScaleSource], Any]]
    inputted: ScaleInput
    value: ScaleValue

    # Special
    _debounced: Optional[bool]
    _scale: Scale
    def __init__(self,
                 source: ScaleSource,
                 irq: bool = False,
                 initial: Optional[ScaleValue] = None,
                 scale: Scale | None = None, start: int = 10, end: int = 100, step: int = 10,
                 get_input: Optional[Callable[[ScaleSource], Any]] = None,
                 check_value: bool = True,
                 check_input: bool = True,
                 avg_value: int | None = None,
                 funcs: ScaleActionFuncsArg = None,
                 events: Optional[ActionEvents] = None,
                 coroutines: Optional[ActionCoroutines] = None,
                 event_loop: Optional[asyncio.AbstractEventLoop] = None,
                 name: Optional[str] = None,
                 is_logging: Optional[bool] = None,
                 style: Optional[str] = None,
                 wait_refresh: int | float = 0.05,
                 wait_change: Optional[int | float] = None,
                 initially_active: bool = True,
                 uses_active: bool = True,
                 ):
        ...

    def get_value(self) -> ScaleValue:
        ...

    def add(self,
            funcs: Optional[ScaleActionFuncsArg] = None,
            events: Optional[ActionEvents] = None,
            coroutines: Optional[ActionCoroutines] = None,
            event_loop: Optional[asyncio.AbstractEventLoop] = None,
            ):
        ...

    def call_as_empty(self):
        ...

# =========================== #
#            Analog           #
# =========================== #


AnalogInput: int | float
AnalogValue: int | float

AnalogActionFunction: TypeAlias = Callable[[AnalogValue], ...]
AnalogActionFuncs: TypeAlias = list[AnalogActionFunction]
AnalogActionFuncsArg: TypeAlias = Optional[AnalogActionFuncs | AnalogActionFunction]

class AnalogSourceProtocol(Protocol):
    value: AnalogInput


class AnalogIrqSource(Protocol):
    value: AnalogValue
    pin: Pin

    def irq(self, activated: bool, handler: Optional[AnalogActionFunction]):
        ...


AnalogSource: TypeAlias = AnalogSourceProtocol | AnalogIrqSource


class TriggerAnalog(Trigger):
    # Action
    funcs: AnalogActionFuncs
    # Refresher
    irq: AnalogIrqSource
    # Trigger
    source: AnalogSource
    _value: AnalogValue
    _inputted: AnalogInput
    _get_input: Optional[Callable[[AnalogSource], Any]]
    inputted: AnalogInput
    value: AnalogValue
    difference: float | None
    from_low: int | float | None
    from_high: int | float | None
    to_low: int | float | None
    to_high: int | float | None
    step: int | float | None
    inverse: bool

    def __init__(self, *,
                 source: AnalogSource,
                 get_input: Optional[Callable[[AnalogSource], Any]] = None,
                 check_value: bool = True,
                 check_input: bool = True,
                 avg_input: int | None = None,
                 avg_value: int | None = None,
                 difference: float | None = None,
                 from_low: int | float | None = None,
                 from_high: int | float | None = None,
                 to_low: int | float | None = None,
                 to_high: int | float| None = None,
                 step: int | float | None = None,
                 inverse: bool = False,
                 funcs: AnalogActionFuncsArg = None,
                 events: Optional[ActionEvents] = None,
                 coroutines: Optional[ActionCoroutines] = None,
                 event_loop: Optional[asyncio.AbstractEventLoop] = None,
                 name: Optional[str] = None,
                 is_logging: Optional[bool] = None,
                 style: Optional[str] = None,
                 wait_refresh: int | float = 0.05,
                 wait_change: Optional[int | float] = None,
                 initially_active: bool = True,
                 uses_active: bool = True,
                 ):
        ...

    def add(self,
            funcs: Optional[AnalogActionFuncsArg] = None,
            events: Optional[ActionEvents] = None,
            coroutines: Optional[ActionCoroutines] = None,
            event_loop: Optional[asyncio.AbstractEventLoop] = None,
            ):
        ...


# =========================== #
#          Comparison         #
# =========================== #

Number: TypeAlias = int | float

ComparisonInput: Number
ComparisonValue: bool

ComparisonActionFunction: TypeAlias = Callable[[ComparisonValue], ...]
ComparisonActionFuncs: TypeAlias = list[ComparisonActionFunction]
ComparisonActionFuncsArg: TypeAlias = Optional[ComparisonActionFuncs | ComparisonActionFunction]


class ComparisonSourceProtocol(Protocol):
    value: ComparisonInput


class ComparisonIrqSource(Protocol):
    value: ComparisonValue
    pin: Pin

    def irq(self, activated: bool, handler: Optional[ComparisonActionFunction]):
        ...


ComparisonSource: TypeAlias = ComparisonSourceProtocol | ComparisonIrqSource

SingleOperator: Callable[[Number, ComparisonInput], ComparisonValue]
DoubleOperator: Callable[[Number, Number, ComparisonInput], ComparisonValue]


class TriggerComparison(Trigger):
    # Action
    funcs: ComparisonActionFuncs
    # Refresher
    irq: ComparisonIrqSource
    # Trigger
    source: ComparisonSource
    _value: ComparisonValue
    _inputted: ComparisonInput
    _get_input: Optional[Callable[[ComparisonSource], Any]]
    inputted: ComparisonInput
    value: ComparisonValue

    # Comparison
    _lower: ComparisonInput
    _upper: Optional[ComparisonInput]
    _operator: Union[SingleOperator, DoubleOperator]
    _raw: ComparisonValue
    _lower_expanded: ComparisonInput
    _upper_expanded: Optional[ComparisonInput]
    _last_value: ComparisonInput
    _last_time: float
    _every: Number

    def __init__(self, *,
                 source: ComparisonSource,
                 initial: Optional[ComparisonValue] = False,
                 switch: bool = False,
                 difference: bool = False,
                 every: int | float | None = None,
                 lower: ComparisonInput = 1,
                 upper: Optional[ComparisonInput] = None,
                 operator: str = "==",
                 expansion_lower: int | float = 0,
                 expansion_upper: int | float = 0,
                 get_input: Optional[Callable[[ComparisonSource], Any]] = None,
                 check_value: bool = True,
                 check_input: bool = True,
                 avg_input: int | None = None,
                 funcs: ComparisonActionFuncsArg = None,
                 events: Optional[ActionEvents] = None,
                 coroutines: Optional[ActionCoroutines] = None,
                 event_loop: Optional[asyncio.AbstractEventLoop] = None,
                 name: Optional[str] = None,
                 is_logging: Optional[bool] = None,
                 style: Optional[str] = None,
                 wait_refresh: int | float = 0.05,
                 wait_change: Optional[int | float] = None,
                 initially_active: bool = True,
                 uses_active: bool = True,
                 ):
        ...

    def get_value_expand(self) -> ComparisonValue:
        ...

    def get_value(self) -> ComparisonValue:
        ...

    def add(self,
            funcs: Optional[ComparisonActionFuncsArg] = None,
            events: Optional[ActionEvents] = None,
            coroutines: Optional[ActionCoroutines] = None,
            event_loop: Optional[asyncio.AbstractEventLoop] = None,
            ):
        ...

