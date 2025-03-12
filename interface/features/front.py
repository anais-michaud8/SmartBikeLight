
import asyncio

# Logic -> Basic
from interface.basic.scale import Scale

# Logic -> Display
from interface.display.apps import Screen
from interface.display.widgets import waiter
from interface.display.menu import Selection

# Logic -> Components
from interface.components.indicator import Indicator
from interface.components.speedometer import Speedometer
from interface.components.clock import Clock
from interface.wireless.phone import PhoneAPI
from interface.components.ble import Bluetooth, Service

# Logic -> Operational
from interface.operational.triggers import Refresher
from interface.operational.special import TriggerButton, TriggerScale, TriggerComparison, TriggerAnalog, Input
from interface.operational.timer import TriggerClock, TriggerTimer
from interface.operational.feature import Feature

# Logic -> Features
from interface.features.settings import (RearSettings, DirectionSettings, BrakeSettings, GeneralSettings,
                                         PERIOD_SCALE, MODES_SCALE, MANUAL_SCALE, TYPES_SCALE, ENABLE_TEXT)

from interface.features.wireless import RearBluetooth, DirectionBluetooth, BrakeBluetooth, ToFrontBluetooth, ToBackBluetooth



class Front(Feature):
    def __init__(self, *,
                 # Outputs
                 output_left: Indicator | None = None, output_right: Indicator | None = None, output_warning: Indicator | None = None,
                 screen: Screen | None = None,
                 # Inputs (Rear)
                 activation: TriggerButton | None = None, frequency: TriggerScale | None = None,
                 modes: TriggerScale | None = None, types: TriggerScale | None = None, manual: TriggerScale | None = None,
                 dark: TriggerComparison | None = None, night: TriggerClock | None = None,
                 light = None, clock: Clock | None = None,
                 # Inputs (Dir)
                 left: TriggerButton | None = None, right: TriggerButton | None = None,
                 warning: TriggerButton | None = None, beep: TriggerButton | None = None,
                 # Inputs (Brake)
                 enable: TriggerScale | None = None, speedometer: Speedometer | None = None,
                 hall: TriggerButton | None = None, acceleration: TriggerComparison | None = None,
                 # Inputs (Display)
                 dis_left: TriggerButton | None = None, dis_right: TriggerButton | None = None,
                 dis_select: TriggerButton | None = None, dis_cancel: TriggerButton | None = None,
                 # Inputs (Other)
                 keys: TriggerButton | None = None, apps: TriggerButton | None = None, timing: TriggerTimer | None = None,
                 eco: TriggerButton | None = None, battery=None,
                 amplification: TriggerAnalog | None = None, automatic: TriggerAnalog | None = None,
                 # Bluetooth
                 bluetooth: Bluetooth | None = None, service: Service | None = None,
                 receiver: ToFrontBluetooth | None = None, sender: ToBackBluetooth | None = None,
                 sender_rear: RearBluetooth | None = None,
                 sender_dir: DirectionBluetooth | None = None, sender_brake: BrakeBluetooth | None = None,
                 # Wifi
                 phone: PhoneAPI | None = None,
                 # Settings
                 settings_rear: RearSettings | None = None, settings_brake: BrakeSettings | None = None,
                 settings_dir: DirectionSettings | None = None, settings_general: GeneralSettings | None = None,
                 # Logging + Initiate
                 name: str = None, is_logging: bool = None, style: str = None, initiate_first_action: bool = False,
                 ):

        # Settings
        settings_general = GeneralSettings() if settings_general is None else settings_general

        # Outputs
        self.output_left = output_left
        self.output_right = output_right
        self.output_warning = output_warning
        self.screen = screen

        # Bluetooth
        self.bluetooth = bluetooth
        self.service = service
        self.sender = sender
        self.receiver = receiver
        self.sender_rear = sender_rear
        self.sender_dir = sender_dir
        self.sender_brake = sender_brake

        # Wifi
        self.phone = phone

        # Inputs (Rear)
        self.activation = activation
        self.frequency = frequency
        self.modes = modes
        self.types = types
        self.manual = manual
        self.dark = dark
        self.night = night
        self.light = light
        self.clock = clock

        # Inputs (Dir)
        self.left = left
        self.right = right
        self.warning = warning
        self.beep = beep

        # Inputs (Brake)
        self.enable = enable
        self.speedometer = speedometer
        self.hall = hall
        self.acceleration = acceleration

        # Inputs (Display)
        self.dis_left = dis_left
        self.dis_right = dis_right
        self.dis_select = dis_select
        self.dis_cancel = dis_cancel

        # Inputs (Other)
        self.keys = keys
        self.apps = apps
        self.timing = timing
        self.eco = eco
        self.battery = battery
        self.amplification = amplification
        self.automatic = automatic

        # Data for direction
        self._left: bool = False
        self._right: bool = False
        self._warning: bool = False
        self.delay = settings_general.delay
        self.event_direction_set = asyncio.Event()

        # Data for display
        self.sending = settings_general.sending
        self.setting_speed = settings_general.setting_speed
        self.setting_odometer = settings_general.setting_odometer
        self.unit_time = settings_general.unit_time
        self.unit_date = settings_general.unit_date
        self.unit_temp = settings_general.unit_temp

        # Keys
        self.shared: tuple[tuple[Refresher, Refresher], ...] = (
            (self.frequency, self.dis_select),
            (self.left, self.dis_left),
            (self.right, self.dis_right),
            (self.warning, self.dis_cancel),
        )
        self.initiate_keys()

        # Action
        self.action_rear()
        self.action_direction()
        self.action_brake()
        self.action_display()

        # Connect to ble
        if self.bluetooth is not None:
            self.bluetooth.connect()

        super().__init__(
            name=name, is_logging=is_logging, style=style, initiate_first_action=initiate_first_action,
            to_refresh=[
                self.output_left, self.output_right, self.output_warning,
                self.bluetooth, self.service,
                self.activation, self.frequency, self.modes, self.types, self.manual, self.dark, self.night,
                self.left, self.right, self.warning, self.beep,
                self.enable, self.speedometer, self.hall, self.acceleration,
                self.dis_left, self.dis_right, self.dis_select, self.dis_cancel,
                self.keys, self.apps, self.timing, self.eco,
                self.amplification, self.automatic
            ],
            to_initiate=[
                self.enable, self.speedometer, self.hall, self.acceleration, self.amplification, self.automatic,
                self.timing,
            ]
        )

    @classmethod
    def from_settings(cls,
                      # Outputs
                      output_left=None, output_right=None, output_warning=None, output_buzzer= None,
                      screen: Screen | None = None,
                      # Inputs (Rear)
                      activation=None, frequency=None,
                      modes=None, types=None, manual=None,
                      dark=None, night=None,
                      light=None, clock: Clock | None = None,
                      # Inputs (Dir)
                      left=None, right=None,
                      warning=None, beep=None,
                      # Inputs (Brake)
                      enable=None, speedometer: Speedometer | bool | None = None,
                      hall=None, acceleration=None,
                      # Inputs (Display)
                      dis_left=None, dis_right=None,
                      dis_select=None, dis_cancel=None,
                      # Inputs (Other)
                      keys=None, apps=None, timing=None,
                      eco=None, battery=None, amplification=None, automatic=None,
                      # Bluetooth
                      bluetooth: Bluetooth | None = None, service: Service | None = None,
                      receiver: ToFrontBluetooth | None = None, sender: ToBackBluetooth | None = None,
                      sender_rear: RearBluetooth | None = None,
                      sender_dir: DirectionBluetooth | None = None, sender_brake: BrakeBluetooth | None = None,
                      # Wifi
                      phone: PhoneAPI | None = None,
                      # Settings
                      settings_rear: RearSettings | None = None, settings_brake: BrakeSettings | None = None,
                      settings_dir: DirectionSettings | None = None, settings_general: GeneralSettings | None = None,
                      speedometer_class: type[Speedometer] = Speedometer,
                      # Logging + Initiate
                      name: str = "Front", is_logging: bool = None, style: str = None, initiate_first_action: bool = False,
                      ):

        settings_rear = RearSettings() if settings_rear is None else settings_rear
        settings_dir = DirectionSettings() if settings_dir is None else settings_dir
        settings_brake = BrakeSettings() if settings_brake is None else settings_brake
        settings_general = GeneralSettings() if settings_general is None else settings_general

        uses_shared = True
        irq = False

        # Outputs
        output_left = Indicator.from_settings(
            settings=settings_dir, light_containers=output_left, buzzer_containers=output_buzzer,
            tone=settings_dir.tone_left, light_activation=settings_dir.light_activation, buzzer_activation=settings_dir.buzzer_activation,
            expiration=settings_dir.expiration_direction, does_expire=settings_dir.does_expire_direction,
            name=f"{name}LeftLight", is_logging=is_logging, style=style,
        ) if not isinstance(output_left, Indicator) and output_left is not None else output_left

        output_right = Indicator.from_settings(
            settings=settings_dir, light_containers=output_right, buzzer_containers=output_buzzer,
            tone=settings_dir.tone_right, light_activation=settings_dir.light_activation, buzzer_activation=settings_dir.buzzer_activation,
            expiration=settings_dir.expiration_direction, does_expire=settings_dir.does_expire_direction,
            name=f"{name}RightLight", is_logging=is_logging, style=style,
        ) if not isinstance(output_right, Indicator) and output_right is not None else output_right

        output_warning = Indicator.from_settings(
            settings=settings_dir, light_containers=output_warning, buzzer_containers=output_buzzer,
            tone=settings_dir.tone_warning, light_activation=settings_dir.light_activation, buzzer_activation=settings_dir.buzzer_activation,
            expiration=settings_dir.expiration_warning, does_expire=settings_dir.does_expire_warning,
            name=f"{name}WarnLight", is_logging=is_logging, style=style,
        ) if not isinstance(output_warning, Indicator) and output_warning is not None else output_warning

        # Inputs (Rear)
        activation = TriggerButton(
            source=activation if not isinstance(activation, bool) else Input(), irq=irq, initial=settings_rear.activation,
            wait_refresh=settings_general.wait_refresh_buttons, wait_change=settings_general.wait_change_buttons,
            name=f"{name}Activation", is_logging=is_logging, style=style, uses_active=uses_shared,
        ) if not isinstance(activation, Refresher) and activation is not None else activation

        frequency = TriggerScale(
            source=frequency if not isinstance(frequency, bool) else Input(), irq=irq,
            initial=settings_rear.period, scale=Scale(*PERIOD_SCALE),
            wait_refresh=settings_general.wait_refresh_buttons, wait_change=settings_general.wait_change_buttons,
            name=f"{name}Brightness", is_logging=is_logging, style=style, uses_active=uses_shared,
        ) if not isinstance(frequency, Refresher) and frequency is not None else frequency

        modes = TriggerScale(
            source=modes if not isinstance(modes, bool) else Input(),
            irq=irq, initial=settings_general.modes, scale=Scale(*MODES_SCALE),
            wait_refresh=settings_general.wait_refresh_buttons, wait_change=settings_general.wait_change_buttons,
            name=f"{name}Modes", is_logging=is_logging, style=style, uses_active=False,
        ) if not isinstance(modes, Refresher) and modes is not None else modes

        types = TriggerScale(
            source=types if not isinstance(enable, bool) else Input(),
            irq=irq, initial=settings_general.types, scale=Scale(*TYPES_SCALE),
            wait_refresh=settings_general.wait_refresh_buttons, wait_change=settings_general.wait_change_buttons,
            name=f"{name}Types", is_logging=is_logging, style=style, uses_active=False,
        ) if not isinstance(types, Refresher) and types is not None else types

        manual = TriggerScale(
            source=manual if not isinstance(manual, bool) else Input(), irq=irq, initial=settings_general.manual, scale=Scale(*MANUAL_SCALE),
            wait_refresh=settings_general.wait_refresh_buttons, wait_change=settings_general.wait_change_buttons,
            name=f"{name}Manual", is_logging=is_logging, style=style, uses_active=False,
        ) if not isinstance(manual, Refresher) and manual is not None else manual

        dark = TriggerComparison(
            source=dark if not isinstance(dark, bool) else Input(), switch=True, avg_input=settings_general.points_dark,
            lower=settings_general.limit_dark, operator="<", expansion_lower=settings_general.expansion_dark,
            wait_refresh=settings_general.wait_refresh_dark, wait_change=settings_general.wait_change_dark,
            name=f"{name}Dark", is_logging=is_logging, style=style, uses_active=True, initially_active=False
        ) if not isinstance(dark, Refresher) and dark is not None else dark

        night = TriggerClock(
            source=night if not isinstance(night, bool) else Input(),
            lower=settings_general.limit_morning, upper=settings_general.limit_evening, operator=">=<",
            name=f"{name}Night", is_logging=is_logging, style=style, uses_active=True, initially_active=False
        ) if not isinstance(night, Refresher) and night is not None else night

        # Inputs (Dir)
        left = TriggerButton(
            source=left if not isinstance(left, bool) else Input(), initial=False, irq=irq,
            wait_refresh=settings_general.wait_refresh_buttons, wait_change=settings_general.wait_change_buttons,
            name=f"{name}Left", is_logging=is_logging, style=style, uses_active=uses_shared,
        ) if not isinstance(left, Refresher) and left is not None else left

        right = TriggerButton(
            source=right if not isinstance(right, bool) else Input(), initial=False, irq=irq,
            wait_refresh=settings_general.wait_refresh_buttons, wait_change=settings_general.wait_change_buttons,
            name=f"{name}Right", is_logging=is_logging, style=style, uses_active=uses_shared,
        ) if not isinstance(right, Refresher) and right is not None else right

        warning = TriggerButton(
            source=warning if not isinstance(warning, bool) else Input(), initial=False, irq=irq,
            wait_refresh=settings_general.wait_refresh_buttons, wait_change=settings_general.wait_change_buttons,
            name=f"{name}Warning", is_logging=is_logging, style=style, uses_active=uses_shared,
        ) if not isinstance(warning, Refresher) and warning is not None else warning

        beep = TriggerButton(
            source=beep if not isinstance(beep, bool) else Input(),
            initial=settings_dir.buzzer_activation, irq=irq,
            wait_refresh=settings_general.wait_refresh_buttons, wait_change=settings_general.wait_change_buttons,
            name=f"{name}Beep", is_logging=is_logging, style=style, uses_active=False,
        ) if not isinstance(beep, Refresher) and beep is not None else beep

        # Inputs (Brake)
        enable = TriggerScale(
            source=enable if not isinstance(enable, bool) else Input(),
            irq=irq, initial=settings_general.enable, start=0, end=len(ENABLE_TEXT) - 1, step=1,
            wait_refresh=settings_general.wait_refresh_buttons, wait_change=settings_general.wait_change_buttons,
            name=f"{name}Enable", is_logging=is_logging, style=style, uses_active=False,
        ) if not isinstance(enable, Refresher) and enable is not None else enable

        speedometer = speedometer_class(
            radius=settings_general.radius, min_speed=settings_general.min_speed,
            unit=settings_general.unit_speed, rounding=settings_general.rounding,
            max_speed=settings_general.max_speed, odometer=settings_general.odometer,
            points=settings_general.points_speed, attr="acceleration",
            name=f"Speedometer", is_logging=is_logging, style=style, uses_active=uses_shared,
            initially_active=settings_general.enable > 0,
        ) if not isinstance(speedometer, Speedometer) and speedometer is not None else speedometer

        hall = TriggerButton(
            source=hall if not isinstance(hall, bool) else Input(), irq=True,
            name=f"{name}Hall", is_logging=is_logging, style=style,
            initially_active=settings_general.enable > 1, uses_active=True,
        ) if not isinstance(hall, Refresher) and hall is not None else hall

        acceleration = TriggerComparison(
            source=speedometer, wait_refresh=settings_general.wait_refresh_acceleration,
            lower=settings_general.limit_acceleration, operator="<", switch=True,
            name=f"{name}Acceleration", is_logging=is_logging, style=style, uses_active=True,
            initially_active=settings_general.enable > 1,
        ) if not isinstance(acceleration, Refresher) and acceleration is not None and speedometer is not None else acceleration

        # Inputs (Display)
        dis_left = TriggerButton(
            source=dis_left if not isinstance(dis_left, bool) else Input(), initial=False,
            wait_refresh=settings_general.wait_refresh_buttons, wait_change=settings_general.wait_change_buttons,
            name=f"{name}DisLeft", is_logging=is_logging, style=style, uses_active=uses_shared,
        ) if not isinstance(dis_left, Refresher) and dis_left is not None else dis_left

        dis_right = TriggerButton(
            source=dis_right if not isinstance(dis_right, bool) else Input(), initial=False,
            wait_refresh=settings_general.wait_refresh_buttons, wait_change=settings_general.wait_change_buttons,
            name=f"{name}DisRight", is_logging=is_logging, style=style, uses_active=uses_shared,
        ) if not isinstance(dis_right, Refresher) and dis_right is not None else dis_right

        dis_cancel = TriggerButton(
            source=dis_cancel if not isinstance(dis_cancel, bool) else Input(), initial=False,
            wait_refresh=settings_general.wait_refresh_buttons, wait_change=settings_general.wait_change_buttons,
            name=f"{name}DisCancel", is_logging=is_logging, style=style, uses_active=uses_shared,
        ) if not isinstance(dis_cancel, Refresher) and dis_cancel is not None else dis_cancel

        dis_select = TriggerButton(
            source=dis_select if not isinstance(dis_select, bool) else Input(), initial=False,
            wait_refresh=settings_general.wait_refresh_buttons, wait_change=settings_general.wait_change_buttons,
            name=f"{name}DisSelect", is_logging=is_logging, style=style, uses_active=uses_shared,
        ) if not isinstance(dis_select, Refresher) and dis_select is not None else dis_select

        # Inputs (Other)

        timing = TriggerTimer(
            wait_refresh=settings_general.wait_refresh_timing,
            name=f"{name}Timings", is_logging=is_logging, style=style,
        ) if not isinstance(timing, Refresher) and timing is not None else timing

        keys = TriggerButton(
            source=keys if not isinstance(keys, bool) else Input(), irq=irq, initial=False,
            wait_refresh=settings_general.wait_refresh_buttons, wait_change=settings_general.wait_change_buttons,
            name=f"{name}Keys", is_logging=is_logging, style=style, uses_active=False,
        ) if not isinstance(keys, Refresher) and keys is not None else keys

        apps = TriggerButton(
            source=apps if not isinstance(apps, bool) else Input(), irq=irq, initial=settings_general.display_activation,
            wait_refresh=settings_general.wait_refresh_buttons, wait_change=settings_general.wait_change_buttons,
            name=f"{name}Apps", is_logging=is_logging, style=style, uses_active=False,
        ) if not isinstance(apps, Refresher) and apps is not None else apps

        eco = TriggerButton(
            source=eco if not isinstance(eco, bool) else Input(), irq=irq, initial=False,
            wait_refresh=settings_general.wait_refresh_buttons, wait_change=settings_general.wait_change_buttons,
            name=f"{name}Eco", is_logging=is_logging, style=style, uses_active=False,
        ) if not isinstance(eco, Refresher) and eco is not None else eco

        amplification = TriggerAnalog(
            source=amplification if not isinstance(amplification, bool) else Input(),
            wait_refresh=settings_general.wait_refresh_pot, wait_change=settings_general.wait_change_pot,
            difference=settings_general.difference_amplification,
            name=f"{name}Amp", is_logging=is_logging, style=style, uses_active=True, initially_active=False
        ) if not isinstance(amplification, Refresher) and amplification is not None else amplification

        automatic = TriggerAnalog(
            source=automatic if not isinstance(automatic, bool) else Input(),
            wait_refresh=settings_general.wait_refresh_automatic, wait_change=settings_general.wait_change_pot,
            to_low=settings_general.brightness_min, to_high=settings_general.brightness_max, step=settings_general.brightness_step,
            from_low=settings_general.light_from_low, from_high=settings_general.light_from_high, inverse=False,
            avg_input=settings_general.points_automatic,
            name=f"{name}Auto", is_logging=is_logging, style=style, uses_active=True, initially_active=False
        ) if not isinstance(automatic, Refresher) and automatic is not None else automatic

        return cls(
            output_left=output_left, output_right=output_right, output_warning=output_warning,
            screen=screen,
            activation=activation, frequency=frequency, modes=modes, types=types, manual=manual,
            dark=dark, night=night, light=light, clock=clock,
            left=left, right=right, warning=warning, beep=beep,
            enable=enable, speedometer=speedometer, hall=hall, acceleration=acceleration,
            keys=keys, apps=apps, timing=timing, dis_left=dis_left, dis_right=dis_right, dis_select=dis_select, dis_cancel=dis_cancel,
            eco=eco, battery=battery, amplification=amplification, automatic=automatic,
            bluetooth=bluetooth, service=service, receiver=receiver, sender=sender,
            sender_rear=sender_rear, sender_dir=sender_dir, sender_brake=sender_brake,
            phone=phone,
            settings_rear=settings_rear, settings_brake=settings_brake, settings_dir=settings_dir,
            settings_general=settings_general,
            name=name, is_logging=is_logging, style=style, initiate_first_action=initiate_first_action,
        )

    def action_rear(self):
        if self.sender_rear is not None:

            # Activation
            if self.activation is not None:
                self.activation.add(funcs=self.callback_activation)
                self.sender_rear.activation.resume()
                if self.screen is not None:
                    self.screen.rear(self.activation.value)
                if self.dark is not None:
                    self.dark.add(funcs=self.callback_dark)
                    if self.screen is not None:
                        self.dark.add(funcs=self.screen.dark)
                        self.screen.dark(int(self.dark.value) if self.dark.is_active else 2)
                if self.night is not None:
                    self.night.add(funcs=self.callback_night)
                    if self.screen is not None:
                        self.night.add(funcs=self.screen.night)
                        self.screen.night(int(self.night.value) if self.night.is_active else 2)

            # Frequency
            if self.frequency is not None:
                self.frequency.add(funcs=self.sender_rear.frequency.set_value)
                self.sender_rear.frequency.resume()
                if self.screen is not None:
                    self.frequency.add(funcs=self.screen.frequency)
                    self.screen.frequency(self.frequency.value)

            # Modes, types & manual
            if self.modes is not None:
                self.modes.add(funcs=self.callback_modes_types)
                if self.screen is not None:
                    self.modes.add(funcs=self.screen.modes)
            if self.types is not None:
                self.types.add(funcs=self.callback_modes_types)
                if self.screen is not None:
                    self.types.add(funcs=self.screen.types)
            if self.manual is not None and self.screen is not None:
                self.manual.add(funcs=self.screen.manual)
                if self.screen is not None:
                    self.screen.manual(self.manual.value)

            # Initiate display
            if self.screen is not None:
                self.screen.modes(self.mode)
                self.screen.types(self.type)

    def action_direction(self):
        if self.sender_dir is not None or self.output_left is not None or self.output_right is not None or self.output_warning is not None:
            if self.left:
                self.left.add(funcs=self.callback_left)
            if self.right:
                self.right.add(funcs=self.callback_right)
            if self.warning:
                self.warning.add(funcs=self.callback_warning)
            if self.sender_dir is not None:
                self.sender_dir.activation.resume()
            if self.screen is not None:
                self.screen.beep(self.beep.value)
            if self.beep:
                if self.output_left is not None:
                    self.beep.add(funcs=self.output_left.set_buzzer_activation)
                if self.output_right is not None:
                    self.beep.add(funcs=self.output_right.set_buzzer_activation)
                if self.output_warning is not None:
                    self.beep.add(funcs=self.output_warning.set_buzzer_activation)
                if self.screen:
                    self.beep.add(funcs=self.screen.beep)

    def action_brake(self):
        if self.enable is not None:
            self.enable.add(funcs=self.callback_enable)
            if self.screen is not None:
                self.enable.add(funcs=self.screen.enable)
                self.screen.enable(0 if not self.enable.is_active else self.enable.value)
        if self.speedometer is not None and self.hall is not None:
            self.hall.add(funcs=self.speedometer.count)
            if self.screen is not None:
                self.screen.speed_unit(self.speedometer.unit)
                self.screen.distance_unit(self.speedometer.unit)
        if self.sender_brake is not None:
            if self.acceleration is not None:
                self.acceleration.add(funcs=self.sender_brake.activation.set_value)
                self.sender_brake.activation.resume()
                if self.screen is not None:
                    self.acceleration.add(funcs=self.screen.brake)

    def action_display(self):
        if self.screen is not None:
            if self.dis_left is not None:
                self.dis_left.add(funcs=Selection.callback_prev)
            if self.dis_right is not None:
                self.dis_right.add(funcs=Selection.callback_next)
            if self.dis_select is not None:
                self.dis_cancel.add(funcs=Selection.callback_cancel)
            if self.dis_cancel is not None:
                self.dis_select.add(funcs=Selection.callback_select)
            self.screen.temperature_unit(self.unit_temp)
        if self.keys is not None:
            self.keys.add(funcs=self.callback_keys)
            if self.screen is not None:
                self.keys.add(funcs=self.screen.keys)
            self.initiate_keys()
        if self.eco is not None:
            self.eco.add(funcs=self.callback_eco)
        if self.apps is not None and self.screen is not None:
            self.apps.add(funcs=self.screen.display.set_activation)
        if self.timing is not None:
            self.timing.add(funcs=self.callback_screen)
        if self.receiver is not None:
            self.receiver.battery.resume()
            self.receiver.temperature.resume()
            if self.screen is not None:
                self.receiver.battery.add(funcs=self.screen.battery_back)
                self.receiver.temperature.add(funcs=self.screen.temperature)

    async def refresh(self):
        tasks = [asyncio.create_task(self.setting_direction())]
        if self.screen is not None and self.bluetooth is not None:
            tasks.append(asyncio.create_task(waiter(self.screen.bluetooth, self.bluetooth, "connected", "status")))
        if self.output_left is not None and hasattr(self.output_left, "expired"):
            tasks.append(asyncio.create_task(waiter(self.callback_left_light, self.output_left, None, "expired")))
        if self.output_right is not None and hasattr(self.output_right, "expired"):
            tasks.append(asyncio.create_task(waiter(self.callback_right_light, self.output_right, None, "expired")))
        if self.output_warning is not None and hasattr(self.output_warning, "expired"):
            tasks.append(asyncio.create_task(waiter(self.callback_warning_light, self.output_warning, None, "expired")))
        await asyncio.gather(*tasks)

    """ Rear """

    @property
    def mode(self) -> int:
        return self.modes.value if self.modes is not None else 0

    @property
    def type(self) -> int:
        return self.types.value if self.types is not None else 0

    # Outputs

    def callback_activation(self, value: bool):
        """ Callback for trigger -> Manual """
        self.set_rear(value)
        self.set_mode_from_manual()

    def callback_dark(self, value: bool):
        """ Callback for trigger -> Dark """
        if self.night is None or not (self.night.active and self.night.value):
            if value != self.activation.value:
                self.set_rear(value)

    def callback_night(self, value: bool):
        """ Callback for trigger -> Night """
        if self.dark is None or not (self.dark.active and self.dark.value):
            if value != self.activation.value:
                self.set_rear(value)

    def callback_modes_types(self, _=None):
        """ Callback for trigger -> Modes/Types """
        self.set_mode_and_type()

    # Modes & Types & Rear

    def set_rear(self, value: bool):
        if self.activation.value != value:
            self.activation.set_value(value, callback=False)
        self.set_mode_and_type()
        self.sender_rear.activation.set_value(value)
        if self.screen is not None:
            self.screen.rear(value)

    def set_mode(self, value: int):
        if self.modes is not None:
            self.modes.value = value
            self.logging(f"Changed mode internally: {value}")
            if self.screen is not None:
                self.screen.modes(value)

    def set_mode_and_type(self):
        """ Decide whether certain workflows should be deactivated or not. """
        off = self.mode == 0 or (self.mode == 2 and self.activation.value) or (self.mode == 3 and not self.activation.value)
        night = off or self.type == 1
        dark = off or self.type == 2
        self.set_activation_night(not night)
        self.set_activation_dark(not dark)

    def set_activation_night(self, value: bool = True):
        if value != self.night.active:
            if value:
                self.logging("Resuming night")
                self.night.resume()
                if self.screen is not None:
                    self.screen.night(int(self.night.value))
            else:
                self.logging("Pausing night")
                self.night.pause()
                if self.screen is not None:
                    self.screen.night(2)

    def set_activation_dark(self, value: bool = True):
        if value != self.dark.active:
            if value:
                self.logging("Resuming dark")
                self.dark.resume()
                if self.screen is not None:
                    self.screen.night(int(self.dark.value))
            else:
                self.logging("Pausing dark")
                self.dark.pause()
                if self.screen is not None:
                    self.screen.dark(2)

    # Set mode from manual

    def set_mode_from_manual(self):
        if self.manual is None:
            self._set_mode_from_manual0()
        if self.manual.value == 2:
            self._set_mode_from_manual2()
        elif self.manual.value == 1:
            self._set_mode_from_manual1()
        else:
            self._set_mode_from_manual0()

    def _set_mode_from_manual0(self):
        self._set_mode_to_manual()

    def _set_mode_from_manual1(self):
        # Auto
        if self.mode == 1:
            self._set_mode_to_manual()
        # Auto ON and OFF
        self._set_mode_semi_to_manual()

    def _set_mode_from_manual2(self):
        # Auto
        if self.mode == 1:
            self._set_mode_auto_to_semi()
        # Auto ON and OFF
        self._set_mode_semi_to_manual()

    def _set_mode_to_manual(self):
        if self.mode != 0:
            self.set_mode(0)  # Manual

    def _set_mode_semi_to_manual(self):
        # Auto OFF
        if self.mode == 2:
            if not self.activation.value:
                self.set_mode(0)  # Manual
        # Auto ON
        elif self.mode == 3:
            if self.activation.value:
                self.set_mode(0)  # Manual

    def _set_mode_auto_to_semi(self):
        # Auto
        if self.mode == 1:
            if self.activation.value:
                self.set_mode(3)  # Auto OFF
            else:
                self.set_mode(2)  # Auto ON

    """ Direction """

    # Not used

    def callback_received(self, value: bool):
        self.logging(f"Received at back with value: {value}")

    def callback_left_light(self, _=None):
        self.set_direction_output(lambda: setattr(self, "_left", False))

    def callback_right_light(self, _=None):
        self.set_direction_output(lambda: setattr(self, "_right", False))

    def callback_warning_light(self, _=None):
        self.set_direction_output(lambda: setattr(self, "_warning", False))

    # Callbacks

    def callback_left(self, _=None):
        self._left = not self._left
        self._right = False
        self._warning = False
        self.event_direction_set.set()

    def callback_right(self, _=None):
        self._right = not self._right
        self._left = False
        self._warning = False
        self.event_direction_set.set()

    def callback_warning(self, _=None):
        self._warning = not self._warning
        self._left = False
        self._right = False
        self.event_direction_set.set()

    # Activation

    async def setting_direction(self):
        while True:
            await self.event_direction_set.wait()
            await self.set_direction()
            self.event_direction_set.clear()

    async def set_direction(self, _=None):
        val = 1 if self._left else 2 if self._right else 3 if self._warning else 0
        print(val)
        if self.sender_dir is not None:
            self.sender_dir.activation.set_value(val)
            self.logging(f"Waiting to receive before setting local activation...")
            await asyncio.sleep(self.delay)
        if self.output_left is not None:
            self.output_left.set_activation(self._left)
        if self.output_right is not None:
            self.output_right.set_activation(self._right)
        if self.output_warning is not None:
            self.output_warning.set_activation(self._warning)
        if self.screen is not None:
            self.screen.direction(val)

    def set_direction_output(self, func):
        previous = 1 if self._left else 2 if self._right else 3 if self._warning else 0
        func()
        val = 1 if self._left else 2 if self._right else 3 if self._warning else 0
        if previous != val:
            self.sender_dir.activation.set_value(val)
            if self.screen is not None:
                self.screen.direction(val)

    """ Rear """

    def callback_enable(self, value: int):
        """ Whether braking / hall detection is used or not: ["Disabled", "Speedometer", "Enabled"] """
        if value > 0:
            self.speedometer.resume()
            if value > 1:
                self.hall.resume()
                self.acceleration.resume()
        else:
            self.speedometer.pause()
            self.hall.pause()
            self.acceleration.pause()

    """ Display """

    @property
    def temperature(self) -> float | None:
        return self.receiver.temperature.value if self.receiver is not None else None

    @property
    def battery_back(self) -> int | None:
        return self.receiver.battery.value if self.receiver is not None else None

    # Callbacks

    def callback_screen(self, _=None):
        if self.screen is not None or self.phone is not None:
            # if self.screen is not None:
            #     self.screen.auto_show = False
            if self.light is not None:
                self.callback_light()
            if self.clock is not None:
                self.callback_date()
                self.callback_clock()
            if self.battery is not None:
                self.callback_battery_front()
            if self.receiver is not None:
                self.callback_battery_back()
                self.callback_temperature()
            if self.speedometer is not None:
                self.callback_speed()
                self.callback_distance()
                self.callback_duration()
            # if self.screen is not None:
            #     self.screen.auto_show = True
            #     self.screen.show()

    def initiate_keys(self):
        for pin_a, pin_b in self.shared:
            pin_a.set_activation(True)
            pin_b.set_activation(False)

    def callback_keys(self, _=None):
        for pin_a, pin_b in self.shared:
            pin_a.toggle_activation()
            pin_b.set_activation(not pin_a.is_active)

    def callback_eco(self, _=None):
        self.logging("Eco Mode is not implemented yet !")

    def callback_sending(self, _=None):
        self.sending = not self.sending
        if self.screen is not None:
            self.screen.sending(self.sending)
        self.callback_screen()

    def callback_reset(self, _=None):
        self.logging("Reset Button is not implemented yet !")

    # Speed

    def callback_speed_type(self, value: bool | int):
        self.setting_speed = bool(value)
        self.callback_speed()

    def callback_distance_type(self, value: bool | int):
        self.setting_odometer = bool(value)
        self.callback_distance()
        self.callback_duration()

    def callback_speed(self, _=None):
        if self.screen is not None:
            self.screen.speed(self.speedometer.max_speed if self.setting_speed else self.speedometer.speed, unit=0)

    def callback_distance(self, _=None):
        if self.screen is not None:
            self.screen.distance(
                self.speedometer.odometer if self.setting_odometer else self.speedometer.distance, unit=0
            )

    def callback_duration(self, _=None):
        if self.screen is not None:
            self.screen.duration(self.speedometer.total_duration if self.setting_odometer else self.speedometer.duration)

    def callback_speed_unit(self, value: int):
        self.speedometer.unit = value
        if self.screen is not None:
            self.screen.speed_unit(value)
            self.screen.distance_unit(value)
        self.callback_speed()
        self.callback_distance()

    # Datetime

    def callback_clock(self, _=None):
        if self.screen is not None:
            self.screen.clock(self.clock.value, unit=self.unit_time)

    def callback_clock_unit(self, value: int):
        self.unit_time = value
        self.callback_clock()

    def callback_date(self, _=None):
        if self.screen is not None:
            self.screen.date(
                self.clock.years, self.clock.months, self.clock.days, self.unit_date
            )

    def callback_date_unit(self, value: int):
        self.unit_date = value
        self.callback_date()

    # Sensors

    def callback_temperature(self, _=None):
        if self.screen is not None:
            self.screen.temperature(self.temperature, unit=self.unit_temp)
        if self.sending and self.phone is not None:
            self.phone.write(temperature=self.temperature)

    def callback_temperature_unit(self, value: int):
        self.unit_temp = value
        self.callback_temperature()

    def callback_light(self, _=None):
        if self.screen is not None:
            self.screen.light(self.light.value)
        if self.sending and self.phone is not None:
            self.phone.write(light=self.light.value)

    def callback_battery_front(self, _=None):
        if self.screen is not None:
            self.screen.battery_front(self.battery.value)
        if self.sending and self.phone is not None:
            self.phone.write(battery_front=self.battery.value)

    def callback_battery_back(self, _=None):
        if self.screen is not None:
            self.screen.battery_back(self.battery_back)
        if self.sending and self.phone is not None:
            self.phone.write(battery_back=self.battery_back)

    """ Other """

