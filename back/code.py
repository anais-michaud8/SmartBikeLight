
import gc
gc.collect()
print(gc.mem_free())

import board
import asyncio

gc.collect()
print(gc.mem_free())

from interface.components.ble import TFT_MAC_ADDRESS
from interface.components.ble import BLUEFRUIT_NAME
from interface.features.wireless import RearBluetooth, DirectionBluetooth, BrakeBluetooth, BikeLight, ToFrontBluetooth, ToBackBluetooth
from interface.features.settings import RearSettings, DirectionSettings, BrakeSettings, GeneralBackSettings
from interface.basic.utils import memory
from interface.features.back import Back

gc.collect()
print(gc.mem_free())

from back.components.outputs import Led, NeoPixel
from back.components.inputs import Button
from back.components.temperature import TemperatureSensor
from back.components.battery import BatteryMonitor
from back.components.ble import Bluetooth, Service, Characteristic, Information

gc.collect()

# Low Speed: A1 (D6) / A2 (D9) / A3 (D10) / A6 (D0)
# High Speed: A4 (SCL - D3) / A5 (SDA - D2) / TX (D1) / AUDIO (D12)

# Right side: A3 / A2 / A1 / AUDIO
_PIN_RIGHT_LIGHT  = board.D10  # A3 L
_PIN_BRAKE_LIGHT  = board.D9   # A2 L
_PIN_LEFT_LIGHT  = board.D6   # A1 L
# = board.D12    # AUDIO H

# Left side: A4 / A5 / A6 / TX
_PIN_SDA = board.SDA
_PIN_SCL = board.SCL
_PIN_REAR = board.D0     # A6 L
_PIN_ECO = board.D1    # TX H

_PIN_STATUS_LIGHT  = board.LED
_PIN_REAR_LIGHT  = board.NEOPIXEL


async def main():

    # Inputs
    eco = Button(_PIN_ECO, inverse=True)
    rear = Button(_PIN_REAR, inverse=True)
    sensor_temperature = TemperatureSensor()
    sensor_battery = BatteryMonitor()

    gc.collect()

    # Outputs
    light_rear = NeoPixel(_PIN_REAR_LIGHT, 10)
    light_left = Led(_PIN_LEFT_LIGHT)
    light_right = Led(_PIN_RIGHT_LIGHT)
    light_brake = Led(_PIN_BRAKE_LIGHT)
    light_status = Led(_PIN_STATUS_LIGHT)
    light_warning = [light_left, light_right]

    gc.collect()

    # Settings
    settings_rear = RearSettings()
    settings_direction = DirectionSettings()
    settings_brake = BrakeSettings()
    settings_general = GeneralBackSettings()

    gc.collect()

    # Bluetooth
    is_logging = True
    ble = Bluetooth(name=BLUEFRUIT_NAME, is_logging=is_logging, logging_name=BLUEFRUIT_NAME)
    ble.set_as_central(address=TFT_MAC_ADDRESS)
    service = BikeLight(ble, service=Service, characteristic=Characteristic, information=Information, is_logging=is_logging)
    receiver_rear = RearBluetooth(service)
    receiver_direction = DirectionBluetooth(service)
    receiver_brake = BrakeBluetooth(service)
    sender = ToFrontBluetooth(service)
    receiver = ToBackBluetooth(service)

    gc.collect()
    print(gc.mem_free())

    # Features
    is_logging = True
    feature = Back.from_settings(
        output_status=light_status, output_rear=light_rear, output_brake=light_brake,
        output_left=light_left, output_right=light_right, output_warning=light_warning,
        rear=rear, eco=eco,
        battery=sensor_battery,
        temperature=sensor_temperature,
        # battery=None, temperature=None,
        bluetooth=ble, service=service.service, receiver=receiver, sender=sender,
        receiver_rear=receiver_rear, receiver_brake=receiver_brake, receiver_dir=receiver_direction,
        settings_rear=settings_rear, settings_brake=settings_brake, settings_general=settings_general, settings_dir=settings_direction,
        is_logging=is_logging,
    )

    gc.collect()


    await asyncio.gather(
        feature.refreshing(),
        memory(3)
    )


asyncio.run(main())


