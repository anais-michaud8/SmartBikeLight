

# Built-in
import asyncio
from typing import Optional, Callable, TypeAlias, Protocol

from machine import Pin

# Local -> Interface
from interface.operational.triggers import Refresher
from interface.basic.average import Average
from interface.operational.triggers import ActionEvents, ActionCoroutines


""" Timer """

TimerInput: bool
TimerValue: bool

TimerActionFunction: TypeAlias = Callable[[TimerValue], ...]
TimerActionFuncs: TypeAlias = list[TimerActionFunction]
TimerActionFuncsArg: TypeAlias = Optional[TimerActionFuncs | TimerActionFunction]

class TimerSourceProtocol(Protocol):
    value: TimerInput


class TimerIrqSource(Protocol):
    value: TimerInput
    pin: Pin

    def irq(self, activated: bool, handler: Optional[TimerActionFunction]):
        ...


TimerSource: TypeAlias = TimerSourceProtocol | TimerIrqSource


class TriggerTimer(Refresher):
    # Action
    funcs: TimerActionFuncs
    # Refresher
    irq: None
    # Timer
    _value: Optional[TimerValue]
    value: Optional[TimerValue]
    def __init__(self,
                 initial: bool = False,
                 switch: bool = False,
                 funcs: Optional[TimerActionFuncsArg] = None,
                 events: Optional[ActionEvents] = None,
                 coroutines: Optional[ActionCoroutines] = None,
                 event_loop: Optional[asyncio.AbstractEventLoop] = None,
                 name: Optional[str] = None,
                 is_logging: Optional[bool] = None,
                 style: Optional[str] = None,
                 wait_refresh: int | float = 0.05,
                 initially_active: bool = True,
                 uses_active: bool = True,
                 ):
        ...

    async def refreshing(self):
        """ (Async) Continuously refreshes. When paused waits for active """
        ...

    def add(self,
            funcs: Optional[TimerActionFuncsArg] = None,
            events: Optional[ActionEvents] = None,
            coroutines: Optional[ActionCoroutines] = None,
            event_loop: Optional[asyncio.AbstractEventLoop] = None,
            ):
        ...


""" Clock """

ClockInput: float
ClockValue: bool

ClockActionFunction: TypeAlias = Callable[[ClockValue], ...]
ClockActionFuncs: TypeAlias = list[ClockActionFunction]
ClockActionFuncsArg: TypeAlias = Optional[ClockActionFuncs | ClockActionFunction]

class ClockSourceProtocol(Protocol):
    value: ClockInput
    change: asyncio.Event


class ClockIrqSource(Protocol):
    value: ClockInput
    change: asyncio.Event
    pin: Pin

    def irq(self, activated: bool, handler: Optional[ClockActionFunction]):
        ...


ClockSource: TypeAlias = ClockSourceProtocol | ClockIrqSource



class TriggerClock(Refresher):
    # Action
    funcs: ClockActionFuncs

    # Trigger
    value: ClockValue
    inputted: ClockInput
    next_change: float
    change: asyncio.Event

    source: ClockSource
    _lower: ClockInput
    _upper: Optional[ClockInput]
    _operator: Callable[[ClockInput, ClockInput, ClockInput], ClockValue] | Callable[[ClockInput, ClockInput], ClockValue]

    def __init__(self,
                 source: ClockSource,
                 lower: ClockInput,
                 upper: Optional[ClockInput] = None,
                 operator: str = "==",
                 # irq: bool = False,
                 # get_input: Optional[Callable[[ButtonSource], Any]] = None,
                 # check_value: bool = True,
                 # check_input: bool = True,
                 funcs: ClockActionFuncsArg = None,
                 events: Optional[ActionEvents] = None,
                 coroutines: Optional[ActionCoroutines] = None,
                 event_loop: Optional[asyncio.AbstractEventLoop] = None,
                 name: Optional[str] = None,
                 is_logging: Optional[bool] = None,
                 style: Optional[str] = None,
                 initially_active: bool = True,
                 uses_active: bool = True,
                 ):
        ...

    async def refreshing(self):
        """ (Async) Continuously refreshes. When paused waits for active """
        ...

    def add(self,
            funcs: Optional[ClockActionFuncsArg] = None,
            events: Optional[ActionEvents] = None,
            coroutines: Optional[ActionCoroutines] = None,
            event_loop: Optional[asyncio.AbstractEventLoop] = None,
            ):
        ...


""" Average """

AverageInput: float
AverageValue: float

AverageActionFunction: TypeAlias = Callable[[AverageValue], ...]
AverageActionFuncs: TypeAlias = list[AverageActionFunction]
AverageActionFuncsArg: TypeAlias = Optional[AverageActionFuncs | AverageActionFunction]

class AverageSourceProtocol(Protocol):
    value: AverageInput


class AverageIrqSource(Protocol):
    value: AverageInput
    pin: Pin

    def irq(self, activated: bool, handler: Optional[AverageActionFunction]):
        ...


AverageSource: TypeAlias = AverageSourceProtocol | AverageIrqSource


class ContinuousAverage(TriggerTimer):
    # Action
    funcs: AverageActionFuncs
    # Refresher
    irq: AverageIrqSource
    # Timer
    _value: Optional[AverageInput]
    value: Optional[AverageValue]
    # Average
    source: TimerSource
    average: Average

    def __init__(self, *,
                 source: AverageSource,
                 points: int = 100,
                 name: str = None,
                 is_logging: bool | None = None,
                 style: str | None = None,
                 wait_refresh: int | float = 0.05,
                 initially_active: bool = True,
                 uses_active: bool = True,
                 ):
        ...

    def collect(self, _=None):
        ...

