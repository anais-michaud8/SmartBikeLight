
# Built-in
import asyncio
from micropython import const
from typing import Protocol, Optional, Any, TypeAlias, Callable

# Interface
from interface.basic.encoding import PercentageInt, Duration
from interface.operational.triggers import ActionEvents, ActionCoroutines
from interface.operational.triggers import Action
from interface.components.files import Settings, JsonFile


_WAIT_FADE_MS = const(50)


class ContainerProtocol(Protocol):
    def show_data(self, data, amplification: int):
        ...

    def hide_data(self):
        ...


Container: TypeAlias = Optional[ContainerProtocol | list[ContainerProtocol]]


OutputActionFunction: TypeAlias = Callable[[bool, bool], ...]
OutputActionFuncs: TypeAlias = list[OutputActionFunction]
OutputActionFuncsArg: TypeAlias = Optional[OutputActionFuncs | OutputActionFunction]



class OutputSettings(Settings):
    def __init__(self,
                 file: JsonFile | None = None,

                 initialize: bool = False,
                 activation: bool = False,
                 data=None,
                 amplification: PercentageInt = 10,

                 period: Duration = 0,
                 duty: Duration = 0,
                 expiration: Duration = 0,
                 fade_in: Duration = 0,
                 fade_out: Duration = 0,

                 does_fade: bool = False,
                 does_blink: bool = False,
                 does_expire: bool = False,

                 **kwargs
                 ):
        self.initialize: bool = initialize
        self.activation: bool = activation
        self.data = data
        self.amplification: PercentageInt = amplification

        self.period: Duration = period
        self.duty: Duration = duty
        self.expiration: Duration = expiration
        self.fade_in: Duration = fade_in
        self.fade_out: Duration = fade_out

        self.does_fade: bool = does_fade
        self.does_blink: bool = does_blink
        self.does_expire: bool = does_expire


class Output(Action):
    # Action
    funcs: OutputActionFuncs

    # Output
    data_off: Optional[Any]
    name_data: str
    name_amplification: str

    _amplification: int
    _amplification_fade: int
    _data: Any

    # Behaviour
    _period: float
    _duty: float
    _expiration: float

    # Fade
    fade_in: float
    fade_out: float

    # Events
    _is_blinking: asyncio.Event
    _is_expiring: asyncio.Event
    _is_not_activated: asyncio.Event
    _is_fading: asyncio.Event
    _is_fade_in: bool
    _is_fade_out: bool
    expired: asyncio.Event

    # Activation
    _activation: bool
    _is_on: bool

    # Objects that show the data with amplification. They must have two methods and a property:
    # - show_data(data, amplification: int)
    # - hide_data()
    containers: Container

    def __init__(self, *, initialize: bool = True, containers: Container = None,
                 activation: bool = False, data=None, amplification: PercentageInt = 10,
                 period: Duration = 0, duty: Duration = 0, expiration: Duration = 0,
                 fade_in: Duration = 0, fade_out: Duration = 0,
                 does_fade: bool = False, does_blink: bool = False, does_expire: bool = False,
                 funcs: OutputActionFuncsArg = None,
                 events: ActionEvents = None,
                 coroutines: ActionCoroutines = None,
                 event_loop: asyncio.AbstractEventLoop = None,
                 name: str = None, is_logging: bool = None, style: str = None, **kwargs):
        ...

    @property
    def value(self):
        """ Whether the output is physically showing something. (NOT activation). """
        return self._is_on

    @property
    def current_amplification(self) -> PercentageInt:
        amplification = self._amplification_fade if hasattr(self, "_is_fading") and self._is_fading.is_set() else self._amplification
        return amplification % 101

    # Properties

    @property
    def activation(self) -> bool:
        """ Whether to activate or not the output. """
        return self._activation

    @property
    def amplification(self) -> PercentageInt:
        """ The data shown by the output. """
        return self._amplification

    @property
    def data(self):
        """ The data shown by the output. """
        return self._data

    @property
    def frequency(self) -> float:
        """ The frequency (in Hz) of the show / hide cycle if any. If not set as 0. """
        return 1 / self.period

    @property
    def period(self) -> Duration:
        """ The period (in seconds) of the show / hide cycle if any. If not set as 0."""
        return self._period

    @property
    def duty(self) -> Duration:
        """ The duty cycle (in seconds) of the show part of the cycle. If half then set as 0. """
        return self._duty

    @property
    def duty_on(self) -> Duration:
        """ The duty cycle (in seconds) of the show part of the cycle. """
        if self._duty <= 0:
            return self._period / 2
        return self._duty

    @property
    def duty_off(self) -> Duration:
        """ The duty cycle (in seconds) of the hide part of the cycle."""
        if self._duty <= 0:
            return self._period / 2
        return abs(self._period - self._duty)

    @property
    def expiration(self) -> Duration:
        """ The time (in seconds) after which the output will be turned off after being activated if any. If not set as 0. """
        return self._expiration

    # Set

    def reset_activation(self, activation: bool):
        if activation:
            self._activation = True
            self._set_event("_is_not_activated", False)
        else:
            self._activation = False
            self._set_event("_is_not_activated", True)
        self._change_activation()
        self._update()

    def set_activation(self, activation: bool):
        if self._activation != activation:
            self.reset_activation(activation)

    def set_inv_activation(self, activation: bool):
        self.set_activation(not activation)

    def set_amplification(self, amplification: PercentageInt):
        self._set_property(self.name_amplification, min(int(amplification), 100),
                           "_amplification", lambda x: x > 0)

    def set_data(self, data):
        self._set_property(self.name_data, data, "_data", lambda x: x != self.data_off)

    def set_period(self, period: Duration):
        self._set_property("Period", period, "_period", lambda x: x >= 0)

    def set_duty(self, duty: Duration):
        self._set_property(
            "Duty", duty, "_duty",
            lambda x: 0 <= x < self._period,
            lambda : setattr(self, "_duty", 0)
        )

    def set_expiration(self, expiration: Duration):
        self._set_property("Expiration", expiration, "_expiration", lambda x: x >= 0)

    def _set_property(self, name: str, value, attr: str, not_off, turn_off=None):
        if getattr(self, attr) != value:
            if not_off(value):
                setattr(self, attr, value)
            else:
                if turn_off is None:
                    self.turn_off()
                else:
                    turn_off()
            self.logging(f"{name} set to {value}")
            self._update()

    # Activation

    def toggle(self, _=None):
        self.set_activation(not self.value)

    def turn_on(self, _=None):
        self.set_activation(True)

    def turn_off(self, _=None):
        self.set_activation(False)

    # Update

    def _change_activation(self):
        # Show/hide and set is_blinking
        if self._activation:
            self._set_event("_is_fade_in", self.fade_in > 0, event=False)
            self._set_event("_is_fade_out", False, event=False)
            self._set_event("_is_fading", self.fade_in > 0)
            self._set_event("_is_expiring", self._expiration > 0)
            if hasattr(self, "is_fade_in") and self._is_fade_in:
                self._amplification_fade = 0
            self.callback(self.value, self.activation)
        else:
            self._set_event("_is_fade_in", False, event=False)
            self._set_event("_is_fade_out", self._expiration <= 0 < self.fade_out, event=False)
            self._set_event("_is_fading", self._expiration <= 0 < self.fade_out)
            self._set_event("_is_expiring", False)
            if hasattr(self, "_is_fade_out") and self._is_fade_out:
                self._amplification_fade = self._amplification
            self.callback(self.value, self.activation)

    def _update(self):
        # Show/hide and set is_blinking
        if self._activation:
            self._set_event("_is_blinking", self._period > 0)
            self._show()
        else:
            self._set_event("_is_blinking", False)
            if not hasattr(self, "_is_fade_out") or (hasattr(self, "_is_fade_out") and not self._is_fade_out):
                self._hide()

    def _set_event(self, attr: str, value: bool, event: bool = True):
        if hasattr(self, attr):
            if event:
                if value:
                    getattr(self, attr).set()
                else:
                    getattr(self, attr).clear()
            else:
                setattr(self, attr, value)

    # Show / Hide

    def _show(self):
        self.show_data()  # Outside since it updates brightness !
        if not self._is_on:
            self._is_on = True
            self.callback(self.value, self.activation)
            self.logging(f"Turning {self.__class__.__name__} on", "DEBUG")

    def show_data(self):
        if self.containers is None:
            return
        if isinstance(self.containers, list):
            for container in self.containers:
                container.show_data(self.data, self.current_amplification)
        else:
            self.containers.show_data(self.data, self.current_amplification)

    def _hide(self):
        if self._is_on:
            self.hide_data()
            self._is_on = False
            self.callback(self.value, self.activation)
            self.logging(f"Turning {self.__class__.__name__} off", "DEBUG")

    def hide_data(self):
        if self.containers is None:
            return
        if isinstance(self.containers, list):
            for container in self.containers:
                container.hide_data()
        else:
            self.containers.hide_data()

    def _toggle_visibility(self):
        if self._is_on:
            self._hide()
        else:
            self._show()

    # Async

    async def _expiring_timeout(self, timeout: int | float | None = None):
        timeout = timeout if timeout is not None else self._expiration
        try:
            await asyncio.wait_for(self._is_not_activated.wait(), timeout=timeout)
            return False
        except asyncio.TimeoutError:
            return True

    async def blink(self):
        if self.value:
            await asyncio.sleep(self.duty_on)
        else:
            await asyncio.sleep(self.duty_off)
        if self._is_blinking.is_set():
            self._toggle_visibility()

    async def blinking(self):
        """ Blinks on and off every x seconds... (Show / Hide only) """
        while True:
            await self._is_blinking.wait()
            await self.blink()
            self.logging(f"Blinking: {self._period}", "INFO")

    async def expire(self):
        if hasattr(self, "_is_fade_out"):
            wait = max(self._expiration - self.fade_out, 0)
            res = await self._expiring_timeout(wait)
            if res:
                self._set_event("_is_fade_out", True, event=False)
                self._set_event("_is_fading", True)
                await self.fade()
        else:
            res = await self._expiring_timeout()
        if res:
            self.turn_off()

    async def expiring(self):
        """ After x seconds will turn off. """
        while True:
            await self._is_expiring.wait()
            await self.expire()

    async def fade(self):
        start, end, duration, event = (self._amplification, 0, self.fade_out, "_is_fade_out") if self._is_fade_out \
            else (0, self._amplification, self.fade_in, "_is_fade_in")
        step = int((end - start) // (1000 * duration/_WAIT_FADE_MS))

        self.logging(f"Start: {start} | End: {end} | Step: {step} | Wait: {_WAIT_FADE_MS}ms")

        for brightness in range(start, end, step):
            if brightness == 0:
                brightness = 1
            self._amplification_fade = brightness
            self._show()
            await asyncio.sleep(_WAIT_FADE_MS/1000)

            # Check if not fading any more
            if not getattr(self, event):
                break

        if self._is_fade_out:
            self._hide()

        self._set_event(event, False, event=False)
        if not self._is_fade_out and not self._is_fade_in:
            self._set_event("_is_fading", False)

    async def fading(self):
        """ When turning on/off, the output's amplification will increase/decrease to/from 0 with a certain accentuation (grade). """
        while True:
            await self._is_fading.wait()
            await self.fade()

    async def refreshing(self):
        tasks = []
        if hasattr(self, "_is_blinking"):
            tasks.append(asyncio.create_task(self.blinking()))
        if hasattr(self, "_is_expiring"):
            tasks.append(asyncio.create_task(self.expiring()))
        if hasattr(self, "_is_fading"):
            tasks.append(asyncio.create_task(self.fading()))
        await asyncio.gather(*tasks)

    # Class method

    @classmethod
    def from_settings_args(cls, settings: OutputSettings, containers=None,
                      name: str = None, is_logging: bool = None, style: str = None,
                      funcs=None, events=None, coroutines=None, event_loop=None, **kwargs):
        special = {cls.name_data.lower(): settings.data, cls.name_amplification.lower(): settings.amplification}
        if cls.name_data.lower() in kwargs:
            kwargs.pop(cls.name_data.lower())
        if cls.name_amplification.lower() in kwargs:
            kwargs.pop(cls.name_amplification.lower())

        set_args = {
            "containers": containers,
            "initialize": settings.initialize,
            "activation": settings.activation,
            "period": settings.period,
            "expiration": settings.expiration,
            "fade_in": settings.fade_in,
            "fade_out": settings.fade_out,
            "duty": settings.duty,
            "does_fade": settings.does_fade,
            "does_blink": settings.does_blink,
            "does_expire": settings.does_expire,
            "name": name, "is_logging": is_logging, "style": style,
            "funcs": funcs, "events": events, "coroutines": coroutines, "event_loop": event_loop,
        }

        set_args.update(special)
        set_args.update(kwargs)

        return set_args

    @classmethod
    def from_settings(cls, settings: OutputSettings, containers=None,
                      name: str = None, is_logging: bool = None, style: str = None,
                      funcs=None, events=None, coroutines=None, event_loop=None, **kwargs):
        return cls(**cls.from_settings_args(
            settings, containers=containers,
            name=name, is_logging=is_logging, style=style,
            funcs=funcs, events=events, coroutines=coroutines,
        ))

    def add(self,
            funcs: Optional[OutputActionFuncsArg] = None,
            events: Optional[ActionEvents] = None,
            coroutines: Optional[ActionCoroutines] = None,
            event_loop: Optional[asyncio.AbstractEventLoop] = None,
            ):
        ...


def make_containers(pin: int | object | list[int | object] | None, _class: type, *args, **kwargs):
    if pin is None:
        return None
    if isinstance(pin, list):
        return [_class(pin, *args, **kwargs) for pin in pin]
    else:
        return _class(pin, *args, **kwargs)

