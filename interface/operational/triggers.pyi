

# Built-in
import asyncio
from typing import Optional, Callable, TypeAlias, Any, Coroutine, Protocol

from machine import Pin

# Local -> Interface
from interface.basic.logger import Logging
from interface.basic.average import Average


# Action
ActionFunction: TypeAlias = Callable[[], ...]
ActionFuncs: TypeAlias = list[ActionFunction]
ActionFuncsArgs: TypeAlias = ActionFuncs | ActionFunction
ActionEvents: TypeAlias = list[asyncio.Event] | asyncio.Event
ActionCoroutines: TypeAlias = list[Coroutine] | Coroutine

# Trigger

class SourceProtocol(Protocol):
    value: Any


class IrqSource(Protocol):
    value: Any
    pin: Pin

    def irq(self, activated: bool, handler: Optional[ActionFunction]):
        ...

Source: TypeAlias = SourceProtocol | IrqSource


class Action:
    funcs: ActionFuncs
    events: ActionEvents
    coroutines: ActionCoroutines
    event_loop: asyncio.AbstractEventLoop
    logging: Logging

    def __init__(self, *,
                 funcs: Optional[ActionFuncsArgs] = None,
                 events: Optional[ActionEvents] = None,
                 coroutines: Optional[ActionCoroutines] = None,
                 event_loop: Optional[asyncio.AbstractEventLoop] = None,
                 name: Optional[str] = None,
                 is_logging: Optional[bool] = None,
                 style: Optional[str] = None,
                 ):
        ...

    def callback(self, *args, **kwargs):
        """ Call all functions, set events and schedule coroutines """
        ...

    def __call__(self, *args, **kwargs):
        ...

    def add(self,
            funcs: Optional[ActionFuncsArgs] = None,
            events: Optional[ActionEvents] = None,
            coroutines: Optional[ActionCoroutines] = None,
            event_loop: Optional[asyncio.AbstractEventLoop] = None,
            ):
        ...


class Refresher(Action):
    wait_refresh: int | float
    wait_change: Optional[int | float]
    irq: IrqSource
    _active: bool
    active: asyncio.Event
    is_active: bool

    def __init__(self, *,
                 irq: IrqSource = None,
                 funcs: Optional[ActionFuncsArgs] = None,
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

    def update(self):
        ...

    def pause(self):
        ...

    def resume(self):
        ...

    def set_activation(self, value: bool):
        ...

    def toggle_activation(self, _=None):
        ...

    async def refreshing(self):
        """ (Async) Continuously refreshes. When paused waits for active """
        ...


# Trigger
TriggerFunction: TypeAlias = Callable[[Any], ...]
TriggerFuncs: TypeAlias = list[TriggerFunction]
TriggerFuncsArgs: TypeAlias = Optional[TriggerFuncs | TriggerFunction]


class Trigger(Refresher):
    funcs: TriggerFuncs
    source: Source
    _value: Any
    _inputted: Any
    _get_input: Optional[Callable[[Source], Any]]
    _check_value: bool
    _check_input: bool
    inputted: Any
    value: Any
    avg_input: Average
    avg_value: Average

    def __init__(self, *,
                 source: Source,
                 irq: bool = False,
                 initial: Optional[Any] = None,
                 get_input: Optional[Callable[[Source], Any]] = None,
                 check_value: bool = True,
                 check_input: bool = True,
                 funcs: TriggerFuncsArgs = None,
                 events: Optional[ActionEvents] = None,
                 coroutines: Optional[ActionCoroutines] = None,
                 event_loop: Optional[asyncio.AbstractEventLoop] = None,
                 name: Optional[str] = None,
                 is_logging: Optional[bool] = None,
                 style: Optional[str] = None,
                 wait_refresh: int | float = 0.05,
                 wait_change: Optional[int | float] = None,
                 avg_input: int | None = None, avg_value: int | None = None,
                 initially_active: bool = True,
                 uses_active: bool = True,
                 ):
        ...

    def set_input(self, value: Any, callback: bool = True) -> bool:
        ...

    def get_input(self) -> Any:
        """ Get the input from the source """
        ...

    def set_value(self, value: Any, callback: bool = True) -> bool:
        ...

    def get_value(self) -> Any:
        """ Get the value from the input"""
        ...

    def check(self, value: Any, attr: str, average: str, checking: bool = True) -> bool:
        ...

    def update(self) -> bool:
        ...

    def add(self,
            funcs: TriggerFuncsArgs = None,
            events: Optional[ActionEvents] = None,
            coroutines: Optional[ActionCoroutines] = None,
            event_loop: Optional[asyncio.AbstractEventLoop] = None,
            ):
        ...

