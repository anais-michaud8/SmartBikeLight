
# Basic
# from interface.basic.scale import Scale

# Operational
from interface.operational.special import TriggerButton, TriggerScale, TriggerAnalog, ranging
from interface.operational.triggers import Trigger

# Features
from interface.features.settings import (SETTINGS_BRIGHTNESS, SETTINGS_SOURCE, GeneralSettings, MODES_TEXT, TYPES_TEXT,
                                         ENABLE_TEXT, MANUAL_TEXT, PERIOD_SCALE, FileSettings)
from interface.features.wireless import RearBluetooth, DirectionBluetooth, BrakeBluetooth
from interface.features.front import Front

# Components
from interface.components.indicator import Indicator
from interface.components.files import Settings

# Interface -> Wireless
from interface.wireless.wifi import WifiManager

# Display
from interface.display.display import Colours, Colour
from interface.display.widgets import Widget
from interface.display.menu import Menu, State, Function, CheckBox
from interface.display.apps import Screen


# =========================== #
#          Brightness         #
# =========================== #


class Brightness(Menu):
    def __init__(self, screen: Screen,
                 rear: RearBluetooth, direction: DirectionBluetooth, brake: BrakeBluetooth,
                 output_left: Indicator, output_right: Indicator, output_warning: Indicator,
                 settings: GeneralSettings, amplification: TriggerAnalog | None = None, automatic: TriggerAnalog | None = None,
                 ):

        # Outputs
        self.screen = screen
        self.sender_rear = rear
        self.sender_direction = direction
        self.sender_brake = brake
        self.output_left = output_left
        self.output_right = output_right
        self.output_warning = output_warning

        # Inputs
        self.amplification = amplification
        self.automatic = automatic

        settings = GeneralSettings() if settings is None else settings
        self.settings = settings
        self.extra = 0

        # Action
        if self.amplification is not None:
            self.amplification.add(funcs=self.callback_change_general)
            if self.settings.setting_source == 1:
                self.amplification.resume()
        if self.automatic is not None:
            self.automatic.add(funcs=self.callback_change_general)
            if self.settings.setting_source == 0:
                self.automatic.resume()
        if self.sender_rear is not None:
            self.sender_rear.brightness.resume()
        if self.sender_direction is not None:
            self.sender_direction.brightness.resume()
        if self.sender_brake is not None:
            self.sender_brake.brightness.resume()

        # Settings
        self.menu_setting = State(
            screen=screen, title="Settings", iterable=SETTINGS_BRIGHTNESS,
            callback=self.callback_settings, index=settings.setting_brightness,
        )

        # Source
        self.menu_source = State(
            screen=screen, title="Source", iterable=SETTINGS_SOURCE,
            callback=self.callback_source, index=settings.setting_source,
        )

        start = settings.brightness_min
        end = settings.brightness_max
        step = settings.brightness_step

        # Volume
        self.menu_volume = State(
            screen=screen, title="Volume", start=start, end=end, step=step,
            initial=settings.volume, callback=self.set_volume
        )

        # Same
        self.menu_same = State(
            screen=screen, title="General", start=start, end=end, step=step, initial=settings.brightness_general, callback=self.set_all
        )

        # Range
        self.menu_range_gen_bright = State(
            screen=screen, title="Brightness", start=start, end=end, step=step, initial=settings.brightness_general, callback=self.set_all
        )

        self.menu_range_display_lower = State(
            screen=screen, title="Lower", start=0, end=100, step=step, initial=settings.brightness_display_lower,
            callback=self.set_display
        )
        self.menu_range_display_upper = State(
            screen=screen, title="Upper", start=0, end=100, step=step, initial=settings.brightness_display_upper,
            callback=self.set_display
        )

        self.menu_range_rear_lower = State(
            screen=screen, title="Lower", start=0, end=100, step=step, initial=settings.brightness_rear_lower,
            callback=self.set_rear
        )
        self.menu_range_rear_upper = State(
            screen=screen, title="Upper", start=0, end=100, step=step, initial=settings.brightness_rear_upper,
            callback=self.set_rear
        )

        self.menu_range_dir_lower = State(
            screen=screen, title="Lower", start=0, end=100, step=step, initial=settings.brightness_direction_lower,
            callback=self.set_direction
        )
        self.menu_range_dir_upper = State(
            screen=screen, title="Upper", start=0, end=100, step=step, initial=settings.brightness_direction_upper,
            callback=self.set_direction
        )

        self.menu_range_brake_lower = State(
            screen=screen, title="Lower", start=0, end=100, step=step, initial=settings.brightness_brake_lower,
            callback=self.set_brake
        )
        self.menu_range_brake_upper = State(
            screen=screen, title="Upper", start=0, end=100, step=step, initial=settings.brightness_brake_upper,
            callback=self.set_brake
        )

        self.menu_range_list = (
            Menu(screen=screen, title="General", iterable=(
                self.menu_range_gen_bright,
            )),
            Menu(screen=screen, title="Rear", iterable=(
                self.menu_range_rear_lower, self.menu_range_rear_upper,
            )),
            Menu(screen=screen, title="Direction", iterable=(
                self.menu_range_dir_lower, self.menu_range_dir_upper,
            )),
            Menu(screen=screen, title="Brake", iterable=(
                self.menu_range_brake_lower, self.menu_range_brake_upper,
            )),
            Menu(screen=screen, title="Display", iterable=(
                self.menu_range_display_lower, self.menu_range_display_upper,
            )),
        )

        # Separated

        self.menu_sep_rear = State(
            screen=screen, title="Rear", start=start, end=end, step=step, callback=self.set_rear, initial=settings.brightness_rear,
        )
        self.menu_sep_direction = State(
            screen=screen, title="Direction", start=start, end=end, step=step, callback=self.set_direction,
            initial=settings.brightness_direction,
        )
        self.menu_sep_brake = State(
            screen=screen, title="Brake", start=start, end=end, step=step, callback=self.set_brake,
            initial=settings.brightness_brake,
        )
        self.menu_sep_display = State(
            screen=screen, title="Display", start=start, end=end, step=step, callback=self.set_display,
            initial=settings.brightness_display,
        )
        self.func_plus = Function(
            screen=screen, title="Add", callback=self.callback_separated_add
        )
        self.func_minus = Function(
            screen=screen, title="Minus", callback=self.callback_separated_minus
        )
        self.func_reset = Function(
            screen=screen, title="Reset", callback=self.callback_separated_reset
        )

        self.menu_separated_list = (
            self.menu_sep_rear, self.menu_sep_direction, self.menu_sep_brake, self.menu_sep_display,
            self.func_plus, self.func_minus, self.func_reset
        )

        # Overall
        self.current_list = (self.menu_same,) if self.menu_setting.index == 0 \
            else self.menu_range_list if self.menu_setting.index == 1 \
            else self.menu_separated_list

        super().__init__(
            screen=screen, title="Brightness", iterable=self.get_iterable()
        )

        self.set_all()

    def get_iterable(self):
        return (self.menu_setting, self.menu_source) + self.current_list + (self.menu_volume,)

    def crop(self, val: int | None):
        if val is None:
            return self.settings.brightness_min
        return max([min([self.settings.brightness_max, val]), self.settings.brightness_min])

    def calc_sep(self, val: int):
        return val + self.extra * self.settings.brightness_step

    # Properties

    @property
    def brightness_general(self):
        if self.menu_source.index == 0:
            return self.crop(self.automatic.value)
        elif self.menu_source.index == 1:
            return self.crop(self.amplification.value)
        else:
            if self.menu_setting.index == 0:
                return self.crop(self.menu_same.value)
            elif self.menu_setting.index == 1:
                return self.crop(self.menu_range_gen_bright.value)
            return self.crop(None)

    @property
    def brightness_rear(self):
        if self.menu_setting.index == 0:
            value = self.brightness_general
        elif self.menu_setting.index == 1:
            return ranging(
                self.brightness_general, 0, 100,
                self.menu_range_rear_lower.value, self.menu_range_rear_upper.value,
                step=self.settings.brightness_step
            )
        else:
            value = self.calc_sep(self.menu_sep_rear.value)
        return self.crop(value)

    @property
    def brightness_direction(self):
        if self.menu_setting.index == 0:
            value = self.brightness_general
        elif self.menu_setting.index == 1:
            return ranging(
                self.brightness_general, 0, 100,
                self.menu_range_dir_lower.value, self.menu_range_dir_upper.value,
                step=self.settings.brightness_step
            )
        else:
            value = self.calc_sep(self.menu_sep_direction.value)
        return self.crop(value)

    @property
    def brightness_brake(self):
        if self.menu_setting.index == 0:
            value = self.brightness_general
        elif self.menu_setting.index == 1:
            return ranging(
                self.brightness_general, 0, 100,
                self.menu_range_brake_lower.value, self.menu_range_brake_upper.value,
                step=self.settings.brightness_step
            )
        else:
            value = self.calc_sep(self.menu_sep_brake.value)
        return self.crop(value)

    @property
    def brightness_display(self):
        if self.menu_setting.index == 0:
            value = self.brightness_general
        elif self.menu_setting.index == 1:
            return ranging(
                self.brightness_general, 0, 100,
                self.menu_range_display_lower.value, self.menu_range_display_upper.value,
                step=self.settings.brightness_step
            )
        else:
            value = self.calc_sep(self.menu_sep_display.value)
        return self.crop(value)

    @property
    def volume(self):
        return self.crop(self.menu_volume.value)

    # Callbacks

    def callback_change_general(self, _=None):
        self.set_all()

    def callback_source(self, _=None):
        if self.menu_source.index == 0:
            self.amplification.pause()
            self.automatic.resume()
        elif self.menu_source.index == 1:
            self.amplification.resume()
            self.automatic.pause()
        else:
            self.amplification.pause()
            self.automatic.pause()
        self.set_all()

    def callback_settings(self, _=None):
        self.current_list = (self.menu_same,) if self.menu_setting.index == 0 \
            else self.menu_range_list if self.menu_setting.index == 1 \
            else self.menu_separated_list
        self.scale.iterable = self.get_iterable()
        self.set_all()

    # Set values

    def set_general(self, _=None):
        self.screen.brightness_general(self.brightness_general)

    def set_rear(self, _=None):
        self.sender_rear.brightness.set_value(self.brightness_rear)
        self.screen.brightness_rear(self.brightness_rear)

    def set_direction(self, _=None):
        self.sender_direction.brightness.set_value(self.brightness_direction)
        self.output_right.set_brightness(self.brightness_direction)
        self.output_left.set_brightness(self.brightness_direction)
        self.output_warning.set_brightness(self.brightness_direction)
        self.screen.brightness_direction(self.brightness_direction)

    def set_volume(self, _=None):
        self.output_right.set_volume(self.volume)
        self.output_left.set_volume(self.volume)
        self.output_warning.set_volume(self.volume)
        self.screen.volume(self.volume)

    def set_brake(self, _=None):
        self.sender_brake.brightness.set_value(self.brightness_brake)
        self.screen.brightness_brake(self.brightness_brake)

    def set_display(self, _=None):
        self.screen.display.set_brightness(self.brightness_display)
        self.screen.brightness_display(self.brightness_display)
        self.screen.show()

    def set_all(self, _=None):
        self.set_rear()
        self.set_direction()
        self.set_brake()
        self.set_display()
        self.set_general()
        self.set_volume()

    # Same

    def callback_same(self, _=None):
        self.set_all()

    # Separated

    def callback_separated_add(self, _=None):
        self.extra += 1
        self.set_all()

    def callback_separated_minus(self, _=None):
        self.extra -= 1
        self.set_all()

    def callback_separated_reset(self, _=None):
        self.extra = 0
        self.set_all()


# =========================== #
#             Menu            #
# =========================== #


class BikeState(State):
    def __init__(self, screen: Screen, trigger: Trigger | None = None,
                 iterable: tuple | list | None = None, start: int | float = 0, end: int | float = 10, step: int | float = 1,
                 initial: int | float | None = None, index: int | None = None,
                 to_highlight: list[Widget] = None, highlighted: Colour = Colours.RED, selected: Colour = Colours.GREEN,
                 callback=None):

        self.to_highlight = to_highlight if isinstance(to_highlight, list) else []
        self.normal = [None]*len(to_highlight)
        self.highlighted = highlighted
        self.selected = selected

        super().__init__(
            screen=screen, setting=False, title="", trigger=trigger,
            iterable=iterable, start=start, end=end, step=step, initial=initial, index=index,
            callback=callback
        )

    # Show / Hide

    def show(self):
        self.highlight(1)

    def hide(self):
        self.highlight(2)

    def hover(self):
        self.highlight(0)

    def highlight(self, value: int):
        for i, control in enumerate(self.to_highlight):
            if control.colour != self.selected and control.colour != self.highlighted:
                self.normal[i] = control.colour
            if value == 0:
                control.colour = self.highlighted
            elif value == 1:
                control.colour = self.selected
            else:
                control.colour = self.normal[i]
            control.show()

    # Enter / Exit

    def exit(self):
        self.hide()
        if self.parent is not None:
            self.parent.enter()

    # Callbacks

    def select(self):
        super().select()

    def cancel(self):
        super().cancel()
        if self.index != self.last:
            if self.callback is not None:
                self.callback(self.value)

    def prev(self):
        super().prev()
        if self.callback is not None:
            self.callback(self.value)

    def next(self):
        super().next()
        if self.callback is not None:
            self.callback(self.value)


class BikeMenu(Menu):

    def enter(self):
        super().enter()
        self.value.hover()

    def exit(self):
        self.value.hide()
        super().exit()

    def prev(self):
        super().prev()
        self.value.hide()
        self.scale.down()
        self.value.hover()

    def next(self):
        super().next()
        self.value.hide()
        self.scale.up()
        self.value.hover()


# =========================== #
#            Inner            #
# =========================== #


class BikeMenuMain(BikeMenu):
    def __init__(self, app: 'BikeApp', highlighted: Colour = Colours.RED, selected: Colour = Colours.GREEN,):
        self.app = app
        screen = app.screen
        settings =  app.settings
        controller = app.controller

        # Speed type
        self.speed_type = BikeState(
            screen=screen, to_highlight=[screen.app_main.icon_speed], highlighted=highlighted, selected=selected,
            start=0, end=1, step=1, initial=settings.setting_speed, callback=controller.callback_speed_type
        )

        # Distance type
        self.distance_type = BikeState(
            screen=screen, to_highlight=[screen.app_main.icon_distance], highlighted=highlighted, selected=selected,
            start=0, end=1, step=1, initial=settings.setting_odometer, callback=controller.callback_distance_type
        )

        # Speed / distance unit
        self.speed_unit = BikeState(
            screen=screen, to_highlight=[screen.app_main.unit_speed, screen.app_main.unit_distance], highlighted=highlighted,
            start=0, end=2, step=1, initial=settings.unit_speed, callback=controller.callback_speed_unit
        )

        # Clock unit
        self.clock_unit = BikeState(
            screen=screen, to_highlight=[screen.app_main.unit_speed, screen.app_main.unit_distance], highlighted=highlighted,
            start=0, end=2, step=1, initial=settings.unit_time, callback=controller.callback_clock_unit
        )

        super().__init__(
            screen=screen, setting=False, iterable=(
                self.speed_type, self.distance_type, self.speed_unit, self.clock_unit
        ))


# =========================== #
#           Settings          #
# =========================== #


class BikeSettingsRear(Menu):
    def __init__(self, screen: Screen,
                 modes: TriggerScale, types: TriggerScale, manual: TriggerScale,
                 frequency: TriggerScale, activation: TriggerButton
                 ):
        super().__init__(
            screen=screen, title="Rear", iterable=(
                    State(screen=screen, title="Modes", iterable=MODES_TEXT, trigger=modes),
                    State(screen=screen, title="Types", iterable=TYPES_TEXT, trigger=types),
                    State(screen=screen, title="Manual", iterable=MANUAL_TEXT, trigger=manual),
                    State(
                        screen=screen, title="Frequency", trigger=frequency,
                        start=PERIOD_SCALE[0], end=PERIOD_SCALE[1], step=PERIOD_SCALE[2],
                    ),
                    Function(screen=screen, callback=activation.call_as_empty, title="Activation"),
                )
        )


class BikeSettingsDirection(Menu):
    def __init__(self, screen: Screen,
                 beep: TriggerButton, left: TriggerButton, right: TriggerButton, warning: TriggerButton):
        super().__init__(
            screen=screen, title="Direction", iterable=(
                    CheckBox(screen=screen, title="Beep", callback=beep.set_value, initial=beep.value),
                    Function(screen=screen, title="Left", callback=left.call_as_empty),
                    Function(screen=screen, title="Right", callback=right.call_as_empty),
                    Function(screen=screen, title="Warning", callback=warning.call_as_empty),
                )

        )


class BikeSettingsBrake(Menu):
    def __init__(self, screen: Screen, enable: TriggerScale,):
        super().__init__(
            screen=screen, title="Brake", iterable=(
                    State(screen=screen, title="Enable", iterable=ENABLE_TEXT, callback=enable.call_as_empty),
                )
        )


class Picker(State):
    def __init__(self, screen: Screen, settings: Settings, icon: str | None = None,
                 title: str = "Menu", iterable: tuple | list | None = None,
                 callback=None):
        self.settings = settings
        super().__init__(screen, True, title=title, icon=icon, iterable=iterable, callback=callback)

    def enter(self):
        self.scale.iterable = self.settings.templates
        self.scale.value = self.settings.template
        super().enter()


class BikeSettingsGeneral(Menu):
    def __init__(self, screen: Screen, wifi: WifiManager, files: FileSettings, callback_sending, callback_reset, *settings,):
        super().__init__(
            screen=screen, title="General", iterable=(
                Function(screen, callback=wifi.ap, title="AP", icon="wifi_ap"),
                Function(screen, callback=wifi.station, title="Station", icon="wifi_station"),
                Function(screen, callback=callback_sending, title="Sending", icon="sending"),
                Function(screen, title="Reset", callback=callback_reset,),
                Menu(
                    screen, title="Settings", iterable=(
                        Function(screen, callback=files.download_all(*settings), title="Download"),
                        Function(screen, callback=files.save_all(*settings), title="Save"),
                        Function(screen, callback=files.upload_all(*settings), title="Upload"),
                        Function(screen, callback=files.remove_all(*settings), title="Delete"),
                        Picker(screen, settings=files, title="Pick", callback=files.load_all(*settings))
                    )
                ),
                Menu(
                    screen, title="Creds", iterable=(
                        Function(screen, callback=wifi.download, title="Download"),
                        Function(screen, callback=wifi.save, title="Save"),
                        Function(screen, callback=wifi.upload, title="Upload"),
                        Function(screen, callback=wifi.remove, title="Delete"),
                        Picker(screen, settings=files, title="Pick", callback=wifi.load)
                    )
                )
            )
        )


class BikeMenuSettings(Menu):
    def __init__(self, screen: Screen,
                 brightness: Brightness, rear: BikeSettingsRear, direction: BikeSettingsDirection,
                 brake: BikeSettingsBrake, general: BikeSettingsGeneral,
                 ):

        super().__init__(screen=screen, title="Settings", iterable=(
            brightness, rear, direction, brake, general
        ))
        self.screen.value(str(self.value), self.value.icon if hasattr(self.value, "icon") else None)
        self.screen.title(str(self.title), self.icon)

    @classmethod
    def from_controllers(cls, screen: Screen, controller: Front,
                         wifi: WifiManager, files: FileSettings, *setting,
                         settings: GeneralSettings | None = None
                         ):
        settings = settings if isinstance(settings, GeneralSettings) else GeneralSettings()

        brightness = Brightness(
            screen=screen, rear=controller.sender_rear, direction=controller.sender_dir, brake=controller.sender_brake,
            output_left=controller.output_left, output_right=controller.output_right, output_warning=controller.output_warning,
            settings=settings, amplification=controller.amplification, automatic=controller.automatic,
        )

        rear = BikeSettingsRear(
            screen=screen, modes=controller.modes, types=controller.types, manual=controller.manual,
            frequency=controller.frequency, activation=controller.activation
        )

        direction = BikeSettingsDirection(
            screen=screen, beep=controller.beep, left=controller.left, right=controller.right,
            warning=controller.warning,
        )

        brake = BikeSettingsBrake(
            screen=screen, enable=controller.enable,
        )

        general = BikeSettingsGeneral(
            screen, wifi, files, controller.callback_sending,
            controller.callback_reset, *setting,
        )

        return cls(
            screen=screen, brightness=brightness, rear=rear, direction=direction, brake=brake, general=general,
        )


# =========================== #
#           BikeApp           #
# =========================== #


class BikeApp(Menu):
    def __init__(self, screen: Screen, controller, menu: BikeMenuSettings, settings: GeneralSettings | None = None):
        self.settings = settings if isinstance(settings, GeneralSettings) else GeneralSettings()

        self.controller = controller
        self.screen = screen

        highlighted = Colours.RED
        selected = Colours.GREEN

        """ Dynamic -> Change apps (When not editing inside apps) """

        """ Hovering -> Settings inside app (When editing inside apps) """

        self.menu_main = BikeMenuMain(self, highlighted=highlighted, selected=selected)
        self.menu_rear = BikeMenuMain(self, highlighted=highlighted, selected=selected)
        self.menu_direction = BikeMenuMain(self, highlighted=highlighted, selected=selected)
        self.menu_brake = BikeMenuMain(self, highlighted=highlighted, selected=selected)
        self.menu_general = BikeMenuMain(self, highlighted=highlighted, selected=selected)

        self.scale_inner = [self.menu_main, self.menu_rear, self.menu_direction, self.menu_brake, self.menu_general]

        """ Settings -> Settings """

        self.menu_settings = menu
        self.menu_settings.parent = self

        super().__init__(screen=screen, setting=False, index=1, title="App", iterable=(
            self.menu_settings, self.menu_main, self.menu_rear, self.menu_direction, self.menu_brake, self.menu_general
        ))
        self.screen.dynamic = self.index

    """ Menu """

    def prev(self):
        super().prev()
        self.screen.dynamic = self.index

    def next(self):
        super().next()
        self.screen.dynamic = self.index

    def enter(self):
        self.index = 1
        self.screen.dynamic = self.index
        super().enter()