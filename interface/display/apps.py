

import gc
gc.collect()

from interface.display.display import Display, Colours, Colour
from interface.display.widgets import Row, Column, Horizontal, Vertical, Text, Icon, Widget, Label

from interface.features.settings import UNIT_SPEED, UNIT_DISTANCE, UNIT_TEMP
from interface.basic.converters import temperature_converter, time_formatter, date_formatter, duration_formatter, speed_converter, distance_converter


_DEGREE = chr(248)


def needs_visible(func):
    def wrapper(self, *args, **kwargs):
        res = func(self, *args, **kwargs)
        if self.visible:
            if isinstance(res, tuple):
                for c in res:
                    if isinstance(c, Widget):
                        c.show()
            elif isinstance(res, Widget):
                res.show()

    return wrapper


def needs_visible_dynamic(*dynamic: int | None):
    dynamic = dynamic[0] if len(dynamic) == 1 else dynamic
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            res = func(self, *args, **kwargs)
            if not self.auto_show:
                return
            if self.visible and (True if isinstance(dynamic, tuple) else self.dynamic == dynamic):
                if isinstance(res, tuple):
                    for i, c in enumerate(res):
                        if (isinstance(c, Widget)
                                and (not isinstance(dynamic, tuple) or self.dynamic == dynamic[i] or dynamic[i] is None)):
                            c.show()
                elif isinstance(res, Widget):
                    res.show()
        return wrapper
    return decorator


gc.collect()

# =========================== #
#           Sections          #
# =========================== #


class Appbar(Row):
    def __init__(self, display: Display, x: int = 0, y: int = 0, wf: int = 0, hf: int = 0,
                 icon_size: int = 16, text_size: int = 8):

        self.icon_keys = Icon(
            display, colour=Colours.MAGENTA, initial=None, size=text_size,
        )

        # Connections
        self.icon_wifi = Icon(
            display, colour=Colours.GREEN, initial=None, size=icon_size,
        )
        self.icon_bluetooth = Icon(
            display, colour=Colours.BLUE, initial=None, size=icon_size,
        )
        self.icon_sending = Icon(
            display, colour=Colours.WHITE, initial=None, size=text_size,
        )

        # Lights
        self.icon_rear = Icon(
            display, colour=Colours.RED, initial=None, size=icon_size,
        )
        self.icon_direction = Icon(
            display, colour=Colours.ORANGE, initial=None, size=icon_size,
        )
        self.icon_brake = Icon(
            display, colour=Colours.RED, initial=None, size=icon_size,
        )

        # Battery
        self.text_battery_front = Text(
            display, colour=Colours.WHITE, anchor=6,
            length=4, formatter="{}", rounding=0, size=text_size
        )
        self.icon_battery_front = Icon(
            display, colour=Colours.WHITE, initial=None, size=icon_size,
        )

        self.text_battery_back = Text(
            display, colour=Colours.WHITE, anchor=6,
            length=4, formatter="{}", rounding=0, size=text_size
        )
        self.icon_battery_back = Icon(
            display, colour=Colours.WHITE, initial=None, size=icon_size,
        )

        super().__init__(display, controls=[
            self.text_battery_back, self.icon_battery_back,
            Vertical(display, thickness=1),
            self.icon_keys,
            self.icon_wifi, self.icon_bluetooth, self.icon_sending,
            self.icon_rear, self.icon_direction, self.icon_brake,
            Vertical(display, thickness=1),
            self.text_battery_front, self.icon_battery_front,
        ], x=x, y=y, wf=wf, hf=hf, margin=3)


gc.collect()


class Settings(Column):
    def __init__(self, display: Display, x: int = 0, y: int = 0, wf: int = 0, hf: int = 0,
                 icon_size: int = 16, text_size: int = 16):
        self.text_title = Label(
            display=display, colour=Colours.WHITE, bold=True, underline=True,
            length=13, text_size=text_size, icon_size=icon_size,
            padding=3, length_includes_icons=True, uses_prefix=True,
        )
        self.icon_up = Icon(display=display, colour=Colours.WHITE, initial="arrow_up", size=icon_size)
        self.text_value = Label(
            display=display, colour=Colours.WHITE, length=13, text_size=text_size, icon_size=icon_size,
            border=Colours.WHITE, padding=3, margin=3, length_includes_icons=True, uses_prefix=True,
        )
        self.icon_down = Icon(display=display, colour=Colours.WHITE, initial="arrow_down", size=icon_size)

        # Layout
        super().__init__(display, x=x, y=y, wf=wf, hf=hf, controls=[
            self.text_title, self.icon_up, self.text_value, self.icon_down,
        ])


gc.collect()


class AppMain(Column):
    def __init__(self, display: Display, x: int = 0, y: int = 0, wf: int = 0, hf: int = 0, pad_x: int | None = None):
        icon_size = 32
        text_size = 32
        unit_size = 16

        # Time
        self.icon_clock = Icon(display, colour=Colours.WHITE, initial="clock", size=icon_size)
        self.text_clock = Text(display, colour=Colours.WHITE, length=8, size=text_size, anchor=5)

        # Speed
        self.icon_speed = Icon(display, colour=Colours.WHITE, initial="speedometer", size=icon_size)
        self.text_speed = Text(display, colour=Colours.WHITE, length=5, rounding=2, anchor=6, size=text_size)
        self.unit_speed = Text(display, colour=Colours.WHITE, length=3, anchor=8, initial="", hf=text_size, size=unit_size)

        # Distance and duration
        icon_size = 16
        text_size = 16
        unit_size = 8
        self.icon_distance = Icon(display, colour=Colours.WHITE, initial="distance", size=icon_size)
        self.text_distance = Text(display, colour=Colours.WHITE, length=4, anchor=6, size=text_size)
        self.unit_distance = Text(display, colour=Colours.WHITE, length=2, anchor=8, initial="", hf=text_size, size=unit_size)
        self.text_duration = Text(display, colour=Colours.WHITE, length=7, anchor=6, size=text_size)

        # Layout
        thickness = 1
        rows = [32, 32, 16]
        total = hf - (len(rows)+1) * thickness
        row = total // 5
        extra = total % 5
        super().__init__(display, x=x, y=y, wf=wf, hf=hf, pad_x=pad_x, controls=[
            Row(display, wf=wf, hf=row*2, pad_x=pad_x, controls=[
                self.icon_clock, self.text_clock
            ]),
            Horizontal(display, thickness=thickness),
            Row(display, wf=wf, hf=row*2, pad_x=pad_x, controls=[
                self.icon_speed, self.text_speed, self.unit_speed
            ]),
            Horizontal(display, thickness=thickness),
            Row(display, wf=wf, hf=row+extra, pad_x=pad_x, controls=[
                self.icon_distance, self.text_distance, self.unit_distance, self.text_duration
            ]),
        ])


gc.collect()


class AppRear(Column):
    def __init__(self, display: Display, x: int = 0, y: int = 0, wf: int = 0, hf: int = 0, pad_x: int | None = None):

        icon_size = 32
        text_size = 32

        # Rear
        self.text_rear = Label(
            display, colour=Colours.WHITE, length=4, text="Rear", bold=True, text_size=text_size,
            icon_size=icon_size, uses_prefix=True, uses_suffix=True
        )

        # Modes, types, beep, dark, night, enable/sense
        self.icon_modes = Icon(display, colour=Colours.WHITE, initial=None, size=icon_size)
        self.icon_types = Icon(display, colour=Colours.WHITE, initial=None, size=icon_size)
        self.icon_manual = Icon(display, colour=Colours.WHITE, initial=None, size=icon_size)

        self.icon_dark = Icon(display, colour=Colours.WHITE, initial=None, size=icon_size)
        self.icon_night = Icon(display, colour=Colours.WHITE, initial=None, size=icon_size)

        icon_size = 16
        text_size = 16
        # Brightness / Volume
        self.icon_brightness = Icon(display, colour=Colours.WHITE, initial="brightness", size=icon_size)
        self.text_brightness = Text(display, colour=Colours.WHITE, length=4, formatter="{}%", rounding=0, size=text_size)

        # Frequency
        self.icon_frequency = Icon(display, colour=Colours.WHITE, initial="frequency", size=icon_size)
        self.text_frequency = Text(display, colour=Colours.WHITE, length=4, formatter="{}s", rounding=2, size=text_size)

        # Layout
        thickness = 1
        rows = [32, 32, 16]
        total = hf - (len(rows)+1) * thickness
        row = total // 5
        extra = total % 5
        self.text_rear.wf = wf
        self.text_rear.hf = row * 2
        super().__init__(display, x=x, y=y, wf=wf, hf=hf, pad_x=pad_x, controls=[
            self.text_rear,
            Horizontal(display, thickness=thickness),
            Row(display, wf=wf, hf=row*2, controls=[
                self.icon_modes, self.icon_types, self.icon_manual, self.icon_dark, self.icon_night
            ]),
            Horizontal(display, thickness=thickness),
            Row(display, wf=wf, hf=row + extra, controls=[
                self.icon_brightness, self.text_brightness, self.icon_frequency, self.text_frequency,
            ]),
        ])


gc.collect()


class AppDirection(Column):
    def __init__(self, display: Display, x: int = 0, y: int = 0, wf: int = 0, hf: int = 0, pad_x: int | None = None):
        icon_size = 32
        text_size = 32

        # Rear
        self.text_direction = Label(
            display, colour=Colours.WHITE, length=4, text="Direction", bold=True, text_size=text_size,
            icon_size=icon_size, uses_prefix=True, uses_suffix=True
        )

        icon_size = 16
        text_size = 16

        # Beep
        self.icon_beep = Icon(display, colour=Colours.WHITE, initial=None, size=icon_size)

        # Brightness / Volume
        self.icon_volume = Icon(display, colour=Colours.WHITE, initial="volume", size=icon_size)
        self.text_volume = Text(display, colour=Colours.WHITE, length=4, formatter="{}%", rounding=0, size=text_size)
        self.icon_brightness = Icon(display, colour=Colours.WHITE, initial="brightness", size=icon_size)
        self.text_brightness = Text(display, colour=Colours.WHITE, length=4, formatter="{}%", rounding=0, size=text_size)

        # Layout
        thickness = 1
        rows = [32, 16, 16]
        total = hf - (len(rows) + 1) * thickness
        row = total // 4
        extra = total % 4
        self.text_direction.wf = wf
        self.text_direction.hf = row * 2
        super().__init__(display, x=x, y=y, wf=wf, hf=hf, pad_x=pad_x, controls=[
            self.text_direction,
            Horizontal(display, thickness=thickness),
            Row(display, wf=wf, hf=row + extra, controls=[
                self.icon_beep, self.icon_volume, self.text_volume,
            ]),
            Horizontal(display, thickness=thickness),
            Row(display, wf=wf, hf=row + extra, controls=[
                self.icon_brightness, self.text_brightness,
            ]),
        ])


gc.collect()


class AppBrake(Column):
    def __init__(self, display: Display, x: int = 0, y: int = 0, wf: int = 0, hf: int = 0, pad_x: int | None = None):
        icon_size = 32
        text_size = 32

        # Brake
        self.text_brake = Label(
            display, colour=Colours.WHITE, length=4, text="Brake", bold=True, text_size=text_size,
            icon_size=icon_size, uses_prefix=True, uses_suffix=True
        )

        icon_size = 16
        text_size = 16
        unit_size = 8

        # Speed and acceleration
        self.icon_speed = Icon(display, colour=Colours.WHITE, initial="speedometer", size=icon_size)
        self.text_speed = Text(display, colour=Colours.WHITE, length=5, rounding=2, anchor=6, size=text_size)
        self.unit_speed = Text(display, colour=Colours.WHITE, length=3, anchor=8, initial="", hf=text_size, size=unit_size)

        # Distance and duration
        self.icon_distance = Icon(display, colour=Colours.WHITE, initial="distance", size=icon_size)
        self.text_distance = Text(display, colour=Colours.WHITE, length=4, anchor=6, size=text_size)
        self.unit_distance = Text(display, colour=Colours.WHITE, length=2, anchor=8, initial="", hf=text_size, size=unit_size)
        self.text_duration = Text(display, colour=Colours.WHITE, length=7, anchor=6, size=text_size)

        # Beep
        self.icon_enable = Icon(display, colour=Colours.WHITE, initial=None, size=icon_size)

        # Brightness
        self.icon_brightness = Icon(display, colour=Colours.WHITE, initial="brightness", size=icon_size)
        self.text_brightness = Text(display, colour=Colours.WHITE, length=4, formatter="{}%", rounding=0, size=text_size)

        # Layout
        thickness = 1
        rows = [32, 16, 16, 16]
        total = hf - (len(rows) + 1) * thickness
        row = total // 5
        extra = total % 5
        self.text_brake.wf = wf
        self.text_brake.hf = row*2
        super().__init__(display, x=x, y=y, wf=wf, hf=hf, pad_x=pad_x, controls=[
            self.text_brake,
            Horizontal(display, thickness=thickness),
            Row(display, wf=wf, hf=row, controls=[
                self.icon_speed, self.text_speed, self.unit_speed,
            ]),
            Horizontal(display, thickness=thickness),
            Row(display, wf=wf, hf=row, controls=[
                self.icon_distance, self.text_distance, self.unit_distance, self.text_duration
            ]),
            Horizontal(display, thickness=thickness),
            Row(display, wf=wf, hf=row + extra, controls=[
                self.icon_brightness, self.text_brightness,
            ]),
        ])


gc.collect()


class AppGeneral(Column):
    def __init__(self, display: Display, x: int = 0, y: int = 0, wf: int = 0, hf: int = 0, pad_x: int | None = None):
        icon_size = 16
        text_size = 16
        unit_size = 8

        # Date
        self.icon_date = Icon(display, colour=Colours.WHITE, initial="calendar", size=icon_size)
        self.text_date = Text(display, colour=Colours.WHITE, length=8, size=text_size)

        # Time
        self.icon_clock = Icon(display, colour=Colours.WHITE, initial="clock", size=icon_size)
        self.text_clock = Text(display, colour=Colours.WHITE, length=8, size=text_size, anchor=5)

        # Brightness
        self.icon_display = Icon(display, colour=Colours.WHITE, initial="display", size=icon_size)
        self.text_display = Text(display, colour=Colours.WHITE, length=4, formatter="{}%", anchor=6, rounding=0, size=text_size)
        self.icon_brightness = Icon(display, colour=Colours.WHITE, initial="brightness", size=icon_size)
        self.text_brightness = Text(display, colour=Colours.WHITE, length=4, formatter="{}%", anchor=6, rounding=0, size=text_size)

        # Temperature Sensor
        self.icon_temperature = Icon(display, colour=Colours.WHITE, initial="temperature", size=icon_size)
        self.text_temperature = Text(display, colour=Colours.WHITE, length=4, anchor=6, rounding=1, size=text_size)
        self.unit_temperature = Text(display, colour=Colours.WHITE, length=2, anchor=8, hf=text_size, size=unit_size)

        # Light Sensor
        self.icon_light = Icon(display, colour=Colours.WHITE, initial="light", size=icon_size)
        self.text_light = Text(display, colour=Colours.WHITE, length=3, anchor=6, rounding=0, size=text_size)
        self.unit_light = Text(display, colour=Colours.WHITE, length=3, anchor=8, initial=" lux", hf=text_size, size=unit_size)

        # Layout
        thickness = 1
        rows = [16, 16, 16, 16]
        total = hf - (len(rows)+1) * thickness
        row = total // 4
        extra = total % 4

        w1 = int(wf * 5/(6.5+5)) - thickness - 6
        w2 = int(wf * 6.5/(6.5+5)) - thickness - 6
        super().__init__(display, x=x, y=y, wf=wf, hf=hf, pad_x=pad_x, controls=[
            Row(display, wf=wf, hf=row, controls=[
                self.icon_date, self.text_date,
            ]),
            Row(display, wf=wf, hf=row+extra, controls=[
                self.icon_clock, self.text_clock,
            ]),
            Horizontal(display, thickness=thickness),
            Row(display, wf=wf, hf=row*2+thickness, controls=[
                Column(display, wf=w1, hf=row*2+thickness, controls=[
                    Row(display, wf=w1, hf=row, controls=[self.icon_display, self.text_display]),
                    Row(display, wf=w1, hf=row,controls=[self.icon_brightness, self.text_brightness]),
                ]),
                Vertical(display, thickness=1),
                Column(display, wf=w2, hf=row*2+thickness, controls=[
                    Row(display, wf=w2, hf=row,controls=[self.icon_light, self.text_light, self.unit_light]),
                    Row(display, wf=w2, hf=row,controls=[self.icon_temperature, self.text_temperature, self.unit_temperature]),
                ]),
            ])
        ])


gc.collect()


class Screen(Column):
    def __init__(self, display: Display, visible: bool = True):

        # Permanent
        self.appbar = Appbar(display, wf=display.width, hf=22)
        self.divider = Horizontal(display, thickness=2, colour=Colours.WHITE)
        self.app = Column(display, x=0, wf=display.width, hf=display.height-2-22)
        super().__init__(display, wf=display.width, hf=display.height, controls=[
            self.appbar, self.divider, self.app
        ])
        self.setup()
        self.controls = [self.appbar, self.divider]

        # Settings
        self._dynamic = 1
        self.auto_show = True

        # 0: Settings
        self.settings = Settings(display, x=self.app.x, y=self.app.y, wf=self.app.wf, hf=self.app.hf)
        self.settings.setup()

        # 1: AppMain -> Clock / Speed / Distance
        self.app_main = AppMain(display, x=self.app.x, y=self.app.y, wf=self.app.wf, hf=self.app.hf)
        self.app_main.setup()

        # 2: AppRear -> Modes / Types / Manual / Dark / Night / Rear / Brightness / Frequency
        self.app_rear = AppRear(display, x=self.app.x, y=self.app.y, wf=self.app.wf, hf=self.app.hf)
        self.app_rear.setup()

        # 3: AppDirection -> Beep / Volume / Brightness / Direction
        self.app_direction = AppDirection(display, x=self.app.x, y=self.app.y, wf=self.app.wf, hf=self.app.hf)
        self.app_direction.setup()

        # 4: AppBrake -> Enable / Brightness / Brake / Speed / Distance / Acceleration
        self.app_brake = AppBrake(display, x=self.app.x, y=self.app.y, wf=self.app.wf, hf=self.app.hf)
        self.app_brake.setup()

        # 5: AppGeneral -> Date / Clock / Light / Temperature / Brightness
        self.app_general = AppGeneral(display, x=self.app.x, y=self.app.y, wf=self.app.wf, hf=self.app.hf)
        self.app_general.setup()

        # Visibility
        self.visible = visible

    def show(self):
        super().show()
        if self.dynamic == 0:
            self.settings.show()
        elif self.dynamic == 1:
            self.app_main.show()
        elif self.dynamic == 2:
            self.app_rear.show()
        elif self.dynamic == 3:
            self.app_direction.show()
        elif self.dynamic == 4:
            self.app_brake.show()
        elif self.dynamic == 5:
            self.app_general.show()
        else:
            self.app_main.show()

    @property
    def dynamic(self) -> int:
        return self._dynamic

    @dynamic.setter
    def dynamic(self, value: int) -> None:
        self.set_dynamic(value)

    def set_dynamic(self, value: int):
        if value != self._dynamic:
            self._dynamic = value
            self.show()

    """ Connectivity """

    @needs_visible
    def wifi(self, value: int):
        """ Update Wi-Fi: [None, Station, AP] """
        if value is None:
            return
        if value == 1:
            self.appbar.icon_wifi.value = "wifi_station"
        elif value == 2:
            self.appbar.icon_wifi.value = "wifi_ap"
        else:
            self.appbar.icon_wifi.value = None
        return self.appbar.icon_wifi

    @needs_visible
    def bluetooth(self, value: bool):
        if value is None:
            return
        if value:
            self.appbar.icon_bluetooth.value = "bluetooth"
        else:
            self.appbar.icon_bluetooth.value = None
        return self.appbar.icon_bluetooth

    @needs_visible
    def sending(self, value: bool):
        if value:
            self.appbar.icon_sending.value = "sending"
        else:
            self.appbar.icon_sending.value = None
        return self.appbar.icon_sending

    @needs_visible
    def keys(self, value: bool):
        if value:
            self.appbar.icon_keys.value = "keys"
        else:
            self.appbar.icon_keys.value = None
        return self.appbar.icon_keys


    """ Lights activation """

    @needs_visible_dynamic(None, 2)
    def rear(self, value: bool):
        if value is None:
            return
        if value:
            self.appbar.icon_rear.value = "rear"
            self.app_rear.text_rear.prefix = "rear"
            self.app_rear.text_rear.suffix = "rear"
        else:
            self.appbar.icon_rear.value = None
            self.app_rear.text_rear.prefix = None
            self.app_rear.text_rear.suffix = None
        return self.appbar.icon_rear, self.app_rear.text_rear

    @needs_visible_dynamic(None, 3)
    def direction(self, value: int):
        if value is None:
            return
        if value == 1:
            self.appbar.icon_direction.value = "left"
            self.app_direction.text_direction.prefix = "left"
            self.app_direction.text_direction.suffix = "left"
        elif value == 2:
            self.appbar.icon_direction.value = "right"
            self.app_direction.text_direction.prefix = "right"
            self.app_direction.text_direction.suffix = "right"
        elif value == 3:
            self.appbar.icon_direction.value = "warning"
            self.app_direction.text_direction.prefix = "warning"
            self.app_direction.text_direction.suffix = "warning"
        else:
            self.appbar.icon_direction.value = None
            self.app_direction.text_direction.prefix = None
            self.app_direction.text_direction.suffix = None
        return self.appbar.icon_direction, self.app_direction.text_direction

    @needs_visible_dynamic(None, 4)
    def brake(self, value: bool):
        if value is None:
            return
        if value:
            self.appbar.icon_brake.value = "brake"
            self.app_brake.text_brake.prefix = "brake"
            self.app_brake.text_brake.suffix = "brake"
        else:
            self.appbar.icon_brake.value = None
            self.app_brake.text_brake.prefix = None
            self.app_brake.text_brake.suffix = None
        return self.appbar.icon_brake, self.app_brake.text_brake

    """ Battery """

    @staticmethod
    def _battery_icon(value: float) -> tuple[Colour, str]:
        if value > 75:
            return Colours.GREEN, "battery_full"
        elif value > 50:
            return Colours.YELLOW, "battery_half"
        elif value > 25:
            return Colours.ORANGE, "battery_low"
        else:
            return Colours.RED, "battery_empty"

    @staticmethod
    def _battery_time_formatter(value: float) -> str:
        if value > 1:
            return f"{str(int(value))[:3]}h"
        else:
            return f"{int(value)}h{round(int(value) - value, 1)}"

    @needs_visible
    def battery_back(self, value: float, percent: bool = True):
        if value is None:
            return
        colour, icon = self._battery_icon(value)
        # Colour
        self.appbar.icon_battery_back.colour = colour
        self.appbar.text_battery_back.colour = colour
        # Icon
        self.appbar.icon_battery_back.value = icon
        # Text
        if percent:
            self.appbar.text_battery_back.value = f"{int(value)}%"
        else:
            self.appbar.text_battery_back.value = self._battery_time_formatter(value)
        return self.appbar.icon_battery_back, self.appbar.text_battery_back

    @needs_visible
    def battery_front(self, value: float, percent: bool = True):
        if value is None:
            return
        colour, icon = self._battery_icon(value)
        # Colour
        self.appbar.icon_battery_front.colour = colour
        self.appbar.text_battery_front.colour = colour
        # Icon
        self.appbar.icon_battery_front.value = icon
        # Text
        if percent:
            self.appbar.text_battery_front.value = f"{int(value)}%"
        else:
            self.appbar.text_battery_front.value = self._battery_time_formatter(value)
        return self.appbar.icon_battery_front, self.appbar.text_battery_front

    """ Sensors """

    @needs_visible_dynamic(5)
    def light(self, value: float):
        if value is None:
            return
        self.app_general.text_light.value = value
        return self.app_general.text_light

    @needs_visible_dynamic(5)
    def temperature(self, value: float, unit: int = 1):
        if value is None:
            return
        self.app_general.text_temperature.value = temperature_converter(value, unit=unit)
        return self.app_general.text_temperature

    @needs_visible_dynamic(5)
    def temperature_unit(self, unit: int):
        self.app_general.unit_temperature.value = UNIT_TEMP[unit].replace("°", _DEGREE)
        return self.app_general.unit_temperature

    """ Datetime """

    @needs_visible_dynamic(5)
    def date(self, year: int, month: int, day: int, unit: int = 1):
        """ Update date: clock.date """
        self.app_general.text_date.value = date_formatter(year, month, day, unit=unit, crop=True)
        return self.app_general.text_date

    @needs_visible_dynamic(1, 5)
    def clock(self, value: float, unit: int = 1):
        if value is None:
            return
        val = time_formatter(value, unit=unit, space=True)
        self.app_main.text_clock.value = val
        self.app_general.text_clock.value = val
        return self.app_main.text_clock, self.app_general.text_clock

    """ Speedometer """

    # Speed

    @needs_visible_dynamic(1, 4)
    def speed(self, value: float, unit: int = 1):
        """ Update speed: speedometer.speed or speedometer.max_speed """
        if value is None:
            return
        val = speed_converter(value, unit=unit)
        self.app_main.text_speed.value = val
        self.app_brake.text_speed.value = val
        return self.app_main.text_speed, self.app_brake.text_speed

    @needs_visible_dynamic(1, 4)
    def speed_unit(self, unit: int = 1):
        """ Set the unit of speed, speedometer.unit """
        self.app_main.unit_speed.value = UNIT_SPEED[unit]
        self.app_brake.unit_speed.value = UNIT_SPEED[unit]
        return self.app_main.unit_speed, self.app_brake.unit_speed

    # Distance

    @needs_visible_dynamic(1, 4)
    def distance(self, value: float, unit: int = 1):
        """ Update distance and duration: speedometer.distance or speedometer.odometer /
                                          speedometer.duration or speedometer.total_duration """
        if value is None:
            return
        val = distance_converter(value, unit=unit)
        self.app_main.text_distance.value = val
        self.app_brake.text_distance.value = val
        return self.app_main.text_distance, self.app_brake.text_distance

    @needs_visible_dynamic(1, 4)
    def distance_unit(self, unit: int = 1):
        """ Set the unit of distance, speedometer.unit """
        val = UNIT_DISTANCE[unit]
        self.app_main.unit_distance.value = val
        self.app_brake.unit_distance.value = val
        return self.app_main.unit_distance, self.app_brake.unit_distance

    # Duration

    @needs_visible_dynamic(1, 4)
    def duration(self, value: int):
        if value is None:
            return
        val = duration_formatter(value)
        self.app_main.text_duration.value = val
        self.app_brake.text_duration.value = val
        return self.app_main.text_duration, self.app_brake.text_duration

    """ Rear """

    @needs_visible_dynamic(2)
    def frequency(self, value: float):
        """ Update rear frequency: frequency.value """
        if value is None:
            return
        self.app_rear.text_frequency.value = value
        return self.app_rear.text_frequency

    @needs_visible_dynamic(2)
    def modes(self, value: int):
        """ Update rear modes: ["Manual", "Auto", "Auto ON", "Auto OFF"] """
        if value is None:
            return
        if value == 0:
            self.app_rear.icon_modes.value = "modes_manual"
        elif value == 1:
            self.app_rear.icon_modes.value = "modes_auto"
        elif value == 2:
            self.app_rear.icon_modes.value = "modes_auto_on"
        else:
            self.app_rear.icon_modes.value = "modes_auto_off"
        return self.app_rear.icon_modes

    @needs_visible_dynamic(2)
    def types(self, value: int):
        """ Update rear types: ["Both", "Light", "Time"] """
        if value is None:
            return
        if value == 0:
            self.app_rear.icon_types.value = "types_both"
        elif value == 1:
            self.app_rear.icon_types.value = "types_light"
        else:
            self.app_rear.icon_types.value = "types_time"
        return self.app_rear.icon_types

    @needs_visible_dynamic(2)
    def manual(self, value: int):
        """ Update rear manual: ["Manual", "Semi", "Auto"] """
        if value is None:
            return
        if value == 0:
            self.app_rear.icon_manual.value = "manual_manual"
        elif value == 1:
            self.app_rear.icon_manual.value = "manual_semi"
        else:
            self.app_rear.icon_manual.value = "manual_auto"
        return self.app_rear.icon_manual

    @needs_visible_dynamic(2)
    def dark(self, value: int):
        """ Update whether it is dark: dark.value and dark.active -> ["Dark", "Not dark", "Deactivated"] """
        if value is None:
            return
        if value == 0:
            self.app_rear.icon_dark.value = "dark_true"
        elif value == 1:
            self.app_rear.icon_dark.value = "dark_false"
        else:
            self.app_rear.icon_dark.value = "dark_off"
        return self.app_rear.icon_dark

    @needs_visible_dynamic(2)
    def night(self, value: int):
        """ Update whether it is night: night.value and night.active -> ["Night", "Not night", "Deactivated"] """
        if value is None:
            return
        if value == 0:
            self.app_rear.icon_night.value = "night_true"
        elif value == 1:
            self.app_rear.icon_night.value = "night_false"
        else:
            self.app_rear.icon_night.value = "night_off"
        return self.app_rear.icon_night

    """ Direction """

    @needs_visible_dynamic(3)
    def beep(self, value: bool):
        """ Update direction beep. """
        if value is None:
            return
        if value:
            self.app_direction.icon_beep.value = "beep_on"
        else:
            self.app_direction.icon_beep.value = "beep_off"
        return self.app_direction.icon_beep

    """ Brake """

    @needs_visible_dynamic(4)
    def enable(self, value: int):
        """ Update speedometer sensing and braking activation: enable.value / acceleration.value -> ["Neither", "Sense", "Both"] """
        if value is None:
            return
        if value == 0:
            self.app_brake.icon_enable.value = "brake_off"
        elif value == 1:
            self.app_brake.icon_enable.value = "brake_sense"
        else:
            self.app_brake.icon_enable.value = "brake_enable"
        return self.app_brake.icon_enable

    """ Brightness / Volume """

    @needs_visible_dynamic(5)
    def brightness_general(self, value: int):
        if value is None:
            self.app_general.text_brightness.value = "X"
        else:
            self.app_general.text_brightness.value = value
        return self.app_general.text_brightness

    @needs_visible_dynamic(5)
    def brightness_auto(self, value: bool):
        if value is None:
            return
        if value:
            self.app_general.icon_brightness.value = "brightness_auto"
        else:
            self.app_general.icon_brightness.value = "brightness_general"
        return self.app_general.icon_brightness

    @needs_visible_dynamic(2)
    def brightness_rear(self, value: int):
        """ Update rear brightness: brightness.value """
        if value is None:
            return
        self.app_rear.text_brightness.value = value
        return self.app_rear.text_brightness

    @needs_visible_dynamic(3)
    def brightness_direction(self, value: int):
        if value is None:
            return
        self.app_direction.text_brightness.value = value
        return self.app_direction.text_brightness

    @needs_visible_dynamic(4)
    def brightness_brake(self, value: int):
        if value is None:
            return
        self.app_brake.text_brightness.value = value
        return self.app_brake.text_brightness

    @needs_visible_dynamic(5)
    def brightness_display(self, value: int):
        if value is None:
            return
        self.app_general.text_display.value = value
        return self.app_general.text_display

    @needs_visible_dynamic(3)
    def volume(self, value: int):
        if value is None:
            return
        self.app_direction.text_volume.value = value
        return self.app_direction.text_volume

    """ Settings """

    @needs_visible_dynamic(0)
    def value(self, value, icon: str | None = None):
        """ Value of setting's value + icon """
        self.settings.text_value.text = value
        self.settings.text_value.prefix = icon
        return self.settings.text_value

    @needs_visible_dynamic(0)
    def title(self, value, icon: str | None = None):
        """ Value of setting's title + icon """
        self.settings.text_title.text = value
        self.settings.text_title.prefix = icon
        return self.settings.text_title


gc.collect()
