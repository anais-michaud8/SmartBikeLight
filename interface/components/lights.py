

import gc
gc.collect()

from interface.basic.encoding import PercentageInt, Colour, Duration
from interface.components.output import Output, OutputSettings


# =========================== #
#           Colours           #
# =========================== #


RED = 0xFF0000
YELLOW = 0xFFC800
ORANGE = 0xFF6400
GREEN = 0x00FF00
AQUA = 0x00FFFF
CYAN = 0x007878
BLUE = 0x0000FF
PURPLE = 0x8C00FF
PINK = 0xFF00C8
WHITE = 0xFFFFFF
OFF = 0x000000
GREY = 0x808080

DARK_GREEN = 0x006400
DARK_BLUE = 0x000064
LIGHT_BLUE = 0x00B4FF


# =========================== #
#            Lights           #
# =========================== #


class LightSettings(OutputSettings):
    def __init__(self, file = None,

                 initialize: bool = False,
                 activation: bool = False,
                 colour: Colour = RED,
                 brightness: PercentageInt = 10,

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
            activation=activation, data=colour, amplification=brightness,
            period=period, duty=duty, expiration=expiration,
            fade_in=fade_in, fade_out=fade_out,
            does_blink=does_blink, does_expire=does_expire, does_fade=does_fade,
        )

    @property
    def colour(self) -> Colour:
        return self.data

    @colour.setter
    def colour(self, colour: Colour):
        self.data = colour

    @property
    def brightness(self) -> PercentageInt:
        return self.amplification

    @brightness.setter
    def brightness(self, brightness: PercentageInt):
        self.amplification = brightness


gc.collect()


class Light(Output):
    data_off = OFF
    name_data: str = "Colour"
    name_amplification: str = "Brightness"

    def __init__(self, *, initialize: bool = True, containers=None,
                 activation: bool = False, colour: Colour = RED, brightness: PercentageInt = 10,
                 period: Duration = 0, duty: Duration = 0, expiration: Duration = 0,
                 fade_in: Duration = 0, fade_out: Duration = 0,
                 does_fade: bool = False, does_blink: bool = False, does_expire: bool = False,
                 funcs=None, events=None, coroutines=None, event_loop=None,
                 name: str = None, is_logging: bool = None, style: str = None, **kwargs
                 ):
        super().__init__(
            initialize=initialize, containers=containers,
            activation=activation, data=colour, amplification=brightness, period=period,
            duty=duty, expiration=expiration, fade_in=fade_in, fade_out=fade_out,
            does_fade=does_fade, does_blink=does_blink, does_expire=does_expire,
            funcs=funcs, events=events, coroutines=coroutines, event_loop=event_loop,
            name=name, is_logging=is_logging, style=style,
        )

    # Light properties and set

    @property
    def colour(self) -> Colour:
        return self.data

    @property
    def brightness(self) -> PercentageInt:
        return self.amplification

    def set_colour(self, colour: Colour):
        self.set_data(colour)

    def set_brightness(self, brightness: PercentageInt):
        self.set_amplification(brightness)

    @classmethod
    def from_settings(cls, settings: LightSettings, containers=None,
                      name: str = None, is_logging: bool = None, style: str = None,
                      funcs=None, events=None, coroutines=None, event_loop=None, **kwargs):
        return cls(**cls.from_settings_args(
            settings, containers=containers, name=name, is_logging=is_logging, style=style,
            funcs=funcs, events=events, coroutines=coroutines, event_loop=event_loop, **kwargs
        ))


gc.collect()

