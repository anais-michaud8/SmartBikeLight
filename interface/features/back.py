

import gc
gc.collect()
import asyncio

# Logic -> Basic

# Logic -> Components
from interface.components.lights import Light
from interface.components.indicator import Indicator
from interface.components.ble import Bluetooth, Service

# Logic -> Operational
from interface.operational.feature import Feature
from interface.operational.special import TriggerButton, TriggerAnalog
from interface.operational.triggers import Refresher

# Logic -> Features
from interface.features.wireless import RearBluetooth, DirectionBluetooth, BrakeBluetooth, ToBackBluetooth, ToFrontBluetooth
from interface.features.settings import RearSettings, DirectionSettings, BrakeSettings, GeneralBackSettings


gc.collect()


class Back(Feature):
    def __init__(self,
                 # Outputs
                 output_status: Light | None = None, output_rear: Light | None = None, output_brake: Light | None = None,
                 output_left: Indicator | None = None, output_right: Indicator | None = None, output_warning: Indicator | None = None,
                 # Inputs
                 rear: TriggerButton | None = None, eco: TriggerButton | None = None,
                 temperature: TriggerAnalog | None = None, battery: TriggerAnalog | None = None,
                 # Bluetooth
                 bluetooth: Bluetooth | None = None, service: Service | None = None,
                 sender: ToFrontBluetooth | None = None, receiver: ToBackBluetooth | None = None,
                 receiver_rear: RearBluetooth | None = None,
                 receiver_dir: DirectionBluetooth | None = None, receiver_brake: BrakeBluetooth | None = None,
                 # Logging + Initiate
                 name: str = None, is_logging: bool = None, style: str = None, initiate_first_action: bool = False,
                 ):

        # Outputs
        self.output_status = output_status
        self.output_rear = output_rear
        self.output_brake = output_brake
        self.output_left = output_left
        self.output_right = output_right
        self.output_warning = output_warning

        # Bluetooth
        self.bluetooth = bluetooth
        self.service = service
        self.sender = sender
        self.receiver = receiver
        self.receiver_rear = receiver_rear
        self.receiver_dir = receiver_dir
        self.receiver_brake = receiver_brake

        # Inputs
        self.input_rear = rear
        self.input_eco = eco
        self.input_temperature = temperature
        self.input_battery = battery

        # Actions
        if self.output_rear is not None:
            if self.receiver_rear is not None:
                self.receiver_rear.activation.add(funcs=self.output_rear.set_activation)
                self.receiver_rear.brightness.add(funcs=self.output_rear.set_brightness)
                self.receiver_rear.frequency.add(funcs=self.output_rear.set_period)
                self.receiver_rear.activation.resume()
                self.receiver_rear.brightness.resume()
                self.receiver_rear.frequency.resume()
            if self.input_rear is not None:
                self.input_rear.add(funcs=self.output_rear.set_activation)
        if self.output_brake is not None and self.receiver_brake is not None:
            self.receiver_brake.activation.add(funcs=self.output_brake.set_activation)
            self.receiver_brake.brightness.add(funcs=self.output_brake.set_brightness)
            self.receiver_brake.activation.resume()
            self.receiver_brake.brightness.resume()
        if self.receiver_dir is not None:
            self.receiver_dir.activation.add(funcs=self.callback_direction)
            self.receiver_dir.activation.resume()
            to_add = [act for act in [self.output_left, self.output_right, self.output_warning] if act is not None]
            if len(to_add) > 0:
                self.receiver_dir.brightness.add(funcs=[act.set_brightness for act in to_add])
                self.receiver_dir.brightness.resume()
        if self.input_temperature is not None and self.sender is not None:
            self.input_temperature.add(funcs=self.sender.temperature.set_value)
            self.sender.temperature.resume()
        if self.input_battery is not None and self.sender is not None:
            self.input_battery.add(funcs=self.sender.battery.set_value)
            self.sender.battery.resume()
        if self.input_eco is not None:
            self.input_eco.add(funcs=self.callback_eco)
        if self.receiver is not None:
            self.receiver.eco.add(funcs=self.callback_eco)
            self.receiver.eco.resume()

        # Connect to ble
        if self.bluetooth is not None:
            self.bluetooth.connect()

        super().__init__(
            name=name, is_logging=is_logging, style=style, initiate_first_action=initiate_first_action,
            to_refresh=[
                self.output_status, self.output_rear, self.output_brake,
                self.output_left, self.output_right, self.output_warning,
                self.bluetooth, self.service,
                self.input_rear, self.input_eco, self.input_temperature, self.input_battery,
            ], to_initiate=[]
        )

        gc.collect()

    def callback_direction(self, value: int):
        left, right, warning = (True, False, False) if value == 1 else (False, True, False) if value == 2 \
            else (False, False, True) if value == 3 else (False, False, False)
        if self.output_left is not None:
            self.output_left.set_activation(left)
        if self.output_right is not None:
            self.output_right.set_activation(right)
        if self.output_rear is not None:
            self.output_warning.set_activation(warning)

    def callback_eco(self, value: bool):
        self.logging(f"Eco mode: {value}")
        if value:
            if self.bluetooth is not None:
                self.bluetooth.disconnect()
        else:
            if self.bluetooth is not None:
                self.bluetooth.connect()
        if self.input_rear is not None:
            self.input_rear.set_activation(not value)
        if self.input_battery is not None:
            self.input_battery.set_activation(not value)
        if self.input_temperature is not None:
            self.input_temperature.set_activation(not value)
        gc.collect()

    def callback_settings(self, value: bool):
        self.logging(f"Settings received: {value}")

    async def refresh_bluetooth(self):
        while True:
            await self.bluetooth.status.wait()
            if self.input_rear is not None:
                self.input_rear.set_activation(not self.bluetooth.connected)
            if self.input_battery is not None:
                self.input_battery.set_activation(self.bluetooth.connected)
            if self.input_temperature is not None:
                self.input_temperature.set_activation(self.bluetooth.connected)
            if self.output_status is not None:
                self.output_status.set_period(0 if self.bluetooth.connected else 2)
            self.bluetooth.status.clear()

    async def refresh(self):
        await self.refresh_bluetooth()

    # Class method

    @classmethod
    def from_settings(cls, *,
                      # Outputs
                      output_status=None, output_rear=None, output_brake=None, output_left=None, output_right=None, output_warning=None,
                      # Inputs
                      rear=None, eco=None, temperature=None, battery=None,
                      # Bluetooth
                      bluetooth: Bluetooth | None = None, service: Service | None = None,
                      sender: ToFrontBluetooth | None = None, receiver: ToBackBluetooth | None = None,
                      receiver_rear: RearBluetooth | None = None,
                      receiver_dir: DirectionBluetooth | None = None, receiver_brake: BrakeBluetooth | None = None,
                      # Settings
                      settings_rear: RearSettings | None = None, settings_brake: BrakeSettings | None = None,
                      settings_dir: DirectionSettings | None = None, settings_general: GeneralBackSettings | None = None,
                      # Logging + Initiate
                      name: str = "Back", is_logging: bool = None, style: str = None, initiate_first_action: bool = False,
                      ):

        settings_rear = RearSettings() if settings_rear is None else settings_rear
        settings_dir = DirectionSettings() if settings_dir is None else settings_dir
        settings_brake = BrakeSettings() if settings_brake is None else settings_brake
        settings_general = GeneralBackSettings() if settings_general is None else settings_general

        # Outputs

        output_status = Light(
            containers=output_status, does_fade=False, does_blink=True, activation=True, period=2, brightness=20
        ) if not isinstance(output_status, Light) and output_status is not None else output_status

        output_rear = Light.from_settings(
            settings=settings_rear, containers=output_rear, brightness=settings_general.brightness_rear,
            name=f"{name}RearLight", is_logging=is_logging, style=style,
        ) if not isinstance(output_rear, Light) and output_rear is not None else output_rear
        gc.collect()

        output_brake = Light.from_settings(
            settings=settings_brake, containers=output_brake, brightness=settings_general.brightness_brake,
            name=f"{name}BrakeLight", is_logging=is_logging, style=style,
        ) if not isinstance(output_brake, Light) and output_brake is not None else output_brake
        gc.collect()

        output_left = Indicator.from_settings(
            settings=settings_dir, light_containers=output_left,
            tone=settings_dir.tone_left, light_activation=settings_dir.light_activation,
            expiration=settings_dir.expiration_direction, does_expire=settings_dir.does_expire_direction,
            brightness=settings_general.brightness_direction,
            name=f"{name}LeftLight", is_logging=is_logging, style=style,
        ) if not isinstance(output_left, Indicator) and output_left is not None  else output_left
        gc.collect()

        output_right = Indicator.from_settings(
            settings=settings_dir, light_containers=output_right,
            tone=settings_dir.tone_right, light_activation=settings_dir.light_activation,
            expiration=settings_dir.expiration_direction, does_expire=settings_dir.does_expire_direction,
            brightness=settings_general.brightness_direction,
            name=f"{name}RightLight", is_logging=is_logging, style=style,
        ) if not isinstance(output_right, Indicator) and output_right is not None  else output_right
        gc.collect()

        output_warning = Indicator.from_settings(
            settings=settings_dir, light_containers=output_warning,
            tone=settings_dir.tone_warning, light_activation=settings_dir.light_activation,
            expiration=settings_dir.expiration_warning, does_expire=settings_dir.does_expire_warning,
            brightness=settings_general.brightness_direction,
            name=f"{name}WarnLight", is_logging=is_logging, style=style,
        ) if not isinstance(output_warning, Indicator) and output_warning is not None else output_warning
        gc.collect()
        # Inputs

        rear = TriggerButton(
            source=rear, initial=False,
            wait_refresh=settings_general.wait_refresh_buttons, wait_change=settings_general.wait_change_buttons,
            name=f"{name}Rear", is_logging=is_logging, style=style, uses_active=True, initially_active=True,
        ) if not isinstance(rear, Refresher) and rear is not None else rear

        gc.collect()

        eco = TriggerButton(
            source=eco, initial=False,
            wait_refresh=settings_general.wait_refresh_buttons, wait_change=settings_general.wait_change_buttons,
            name=f"{name}Eco", is_logging=is_logging, style=style, uses_active=False,
        ) if not isinstance(eco, Refresher) and eco is not None else eco
        gc.collect()

        temperature = TriggerAnalog(
            source=temperature, wait_refresh=settings_general.wait_refresh_temp, difference=settings_general.difference_temperature,
            name=f"{name}Temperature", is_logging=is_logging, style=style, uses_active=True, initially_active=False,
        ) if not isinstance(temperature, Refresher) and temperature is not None else temperature
        gc.collect()

        battery = TriggerAnalog(
            source=battery, wait_refresh=settings_general.wait_refresh_battery, difference=settings_general.difference_battery,
            name=f"{name}Battery", is_logging=is_logging, style=style, uses_active=True, initially_active=False,
        ) if not isinstance(battery, Refresher) and battery is not None else battery

        gc.collect()

        return cls(
            output_status=output_status, output_rear=output_rear, output_brake=output_brake,
            output_left=output_left, output_right=output_right, output_warning=output_warning,
            rear=rear, eco=eco, temperature=temperature, battery=battery,
            bluetooth=bluetooth, service=service, sender=sender, receiver=receiver,
            receiver_rear=receiver_rear, receiver_dir=receiver_dir, receiver_brake=receiver_brake,
            name=name, is_logging=is_logging, style=style, initiate_first_action=initiate_first_action,
        )


gc.collect()
