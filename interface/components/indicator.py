

import gc
gc.collect()


from interface.basic.encoding import PercentageInt, Colour, Duration, Uint16
from interface.components.lights import YELLOW, LightSettings, OFF
from interface.components.output import Output


class IndicatorSettings(LightSettings):
    def __init__(self, file = None,

                 initialize: bool = False,

                 activation: bool = False,
                 light_activation: bool = False,
                 buzzer_activation: bool = False,

                 colour: Colour = YELLOW,
                 brightness: PercentageInt = 10,

                 tone: Uint16 = 1000,
                 volume: PercentageInt = 10,

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

        super().__init__(
            file=file,
            initialize=initialize,
            activation=activation, colour=colour, brightness=brightness,
            period=period, duty=duty, expiration=expiration,
            fade_in=fade_in, fade_out=fade_out,
            does_blink=does_blink, does_expire=does_expire, does_fade=does_fade,
        )

        self.volume = volume
        self.tone = tone
        self.light_activation = light_activation
        self.buzzer_activation = buzzer_activation


gc.collect()


class Indicator(Output):
    def __init__(self, *, initialize: bool = True, activation: bool = False,
                 light_containers=None, buzzer_containers=None,
                 light_activation: bool = False, buzzer_activation: bool = False,
                 colour: Colour = YELLOW, brightness: PercentageInt = 10,
                 tone: Uint16 = 1000, volume: PercentageInt = 10,
                 period: Duration = 0, duty: Duration = 0, expiration: Duration = 0,
                 fade_in: Duration = 0, fade_out: Duration = 0,
                 does_fade: bool = False, does_blink: bool = False, does_expire: bool = False,
                 funcs=None, events=None, coroutines=None, event_loop=None,
                 name: str = None, is_logging: bool = None, style: str = None, **kwargs
                 ):

        super().__init__(
            initialize=initialize, activation=activation,
            period=period, duty=duty, expiration=expiration, fade_in=fade_in, fade_out=fade_out,
            does_fade=does_fade, does_blink=does_blink, does_expire=does_expire,
            funcs=funcs, events=events, coroutines=coroutines, event_loop=event_loop,
            name=name, is_logging=is_logging, style=style,
        )

        self.buzzer_containers = buzzer_containers
        self.light_containers = light_containers

        self._light_activation = light_activation
        self._buzzer_activation = buzzer_activation

        self._tone = tone
        self._volume = volume
        self._colour = colour
        self._brightness = brightness

    # Buzzer

    @property
    def volume(self):
        return self._volume

    @property
    def tone(self) -> Uint16:
        return self._tone

    def set_volume(self, volume: PercentageInt):
        self._set_property("Volume", min(int(volume), 100),
                           "_volume", lambda x: x > 0)

    def set_tone(self, tone: Uint16):
        self._set_property("Tone", tone, "_tone", lambda x: x >= 1)

    def set_buzzer_activation(self, buzzer_activation: bool):
        self._buzzer_activation = buzzer_activation
        if self.activation:
            if buzzer_activation:
                self._show_data(self.buzzer_containers, self._buzzer_activation, self.tone, self.volume)
            else:
                self._hide_data(self.buzzer_containers)

    # Light

    @property
    def brightness(self):
        return self._brightness

    @property
    def colour(self) -> Colour:
        return self._colour

    def set_brightness(self, brightness: PercentageInt):
        self._set_property("Brightness", min(int(brightness), 100),
                           "_brightness", lambda x: x > 0)

    def set_colour(self, colour: Colour):
        self._set_property("Colour", colour, "_colour", lambda x: x != OFF)

    def set_light_activation(self, light_activation: bool):
        self._light_activation = light_activation
        self.reset_activation(self.activation)

    # Show / Hide

    def show_data(self):
        self._show_data(self.light_containers, self._light_activation, self.colour, self.brightness)
        self._show_data(self.buzzer_containers, self._buzzer_activation, self.tone, self.volume)

    def _show_data(self, containers, activation: bool, data, amplification):
        if containers is not None and activation:
            if isinstance(containers, list):
                for c in containers:
                    c.show_data(data, amplification)
            else:
                containers.show_data(data, amplification)
        else:
            self._hide_data(containers)

    def hide_data(self):
        self._hide_data(self.light_containers)
        self._hide_data(self.buzzer_containers)

    @staticmethod
    def _hide_data(containers):
        if containers is not None:
            if isinstance(containers, list):
                for c in containers:
                    c.hide_data()
            else:
                containers.hide_data()

    @classmethod
    def from_settings(cls, settings: IndicatorSettings,
                      light_containers=None, buzzer_containers=None,
                      name: str = None, is_logging: bool = None, style: str = None,
                      funcs=None, events=None, coroutines=None, event_loop=None, **kwargs):
        kwargs.update({
            "tone": settings.tone, "volume": settings.volume,
            "colour": settings.colour, "brightness": settings.brightness,
            "light_activation": settings.light_activation, "buzzer_activation": settings.buzzer_activation,
        })
        return cls(**cls.from_settings_args(
            settings, light_containers=light_containers, buzzer_containers=buzzer_containers,
            name=name, is_logging=is_logging, style=style,
            funcs=funcs, events=events, coroutines=coroutines, event_loop=event_loop, **kwargs
        ))


gc.collect()

