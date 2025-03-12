

import gc
gc.collect()


from interface.basic.encoding import PercentageInt, Duration, Uint16
from interface.components.output import Output, OutputSettings


# =========================== #
#            Buzzer           #
# =========================== #


class BuzzerSettings(OutputSettings):
    def __init__(self,
                 file=None,

                 initialize: bool = False,
                 activation: bool = False,
                 tone: Uint16 = 1000,
                 volume: PercentageInt = 10,

                 period: Duration = 0,
                 duty: Duration = 0,
                 expiration: Duration = 0,
                 fade_in: Duration = 0,
                 fade_out: Duration = 0,

                 **kwargs
                 ):

        super().__init__(
            file=file,
            initialize=initialize, activation=activation, data=tone, amplification=volume,
            period=period, duty=duty, expiration=expiration,
            fade_in=fade_in, fade_out=fade_out,
        )


    @property
    def tone(self) -> Uint16:
        return self.data

    @tone.setter
    def tone(self, value: Uint16):
        self.data = value

    @property
    def volume(self) -> PercentageInt:
        return self.amplification

    @volume.setter
    def volume(self, value: PercentageInt):
        self.amplification = value


gc.collect()


class Buzzer(Output):
    data_off = 0
    name_data: str = "Tone"
    name_amplification: str = "Volume"

    def __init__(self, *, initialize: bool = True, containers=None,
                 activation: bool = False, tone: Uint16 = 1000, volume: PercentageInt = 10,
                 period: Duration = 0, duty: Duration = 0, expiration: Duration = 0,
                 fade_in: Duration = 0, fade_out: Duration = 0,
                 does_fade: bool = False, does_blink: bool = False, does_expire: bool = False,
                 funcs=None, events=None, coroutines=None, event_loop=None,
                 name: str = None, is_logging: bool = None, style: str = None, **kwargs
                 ):
        super().__init__(
            activation=activation, containers=containers,
            initialize=initialize, data=tone, amplification=volume, period=period,
            duty=duty, expiration=expiration, fade_in=fade_in, fade_out=fade_out,
            does_fade=does_fade, does_blink=does_blink, does_expire=does_expire,
            funcs=funcs, events=events, coroutines=coroutines, event_loop=event_loop,
            name=name, is_logging=is_logging, style=style,
        )

    # Buzzer properties and set

    @property
    def tone(self) -> Uint16:
        return self.data

    @property
    def volume(self) -> PercentageInt:
        return self.amplification

    def set_tone(self, tone: Uint16):
        self.set_data(tone)

    def set_volume(self, volume: PercentageInt):
        self.set_amplification(volume)

    @classmethod
    def from_settings(cls, settings: BuzzerSettings, containers=None,
                      name: str = None, is_logging: bool = None, style: str = None,
                      funcs=None, events=None, coroutines=None, event_loop=None, **kwargs):
        return cls(**cls.from_settings_args(
            settings, containers=containers, name=name, is_logging=is_logging, style=style,
            funcs=funcs, events=events, coroutines=coroutines, event_loop=event_loop, **kwargs
        ))


gc.collect()

