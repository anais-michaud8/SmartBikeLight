

import gc
gc.collect()
print(gc.mem_free())  # 2055536

import asyncio

# Basic
from interface.basic.utils import memory

# Components
from interface.components.ble import TFT_NAME
# from interface.components.ble import ESP32_MAC_ADDRESS as BLUEFRUIT_MAC_ADDRESS
# from interface.components.ble import BLUEFRUIT_MAC_ADDRESS
from interface.components.clock import Clock

gc.collect()
print(gc.mem_free())  # 2021328

# Features
from interface.features.front import Front
from interface.features.wireless import RearBluetooth, DirectionBluetooth, BrakeBluetooth, BikeLight, ToFrontBluetooth, ToBackBluetooth
from interface.features.settings import FileSettings
from interface.features.bike import BikeMenuSettings, BikeApp

gc.collect()
print(gc.mem_free())  # 1799840

# Display
from interface.display.display import Display
from interface.display.apps import Screen

gc.collect()
print(gc.mem_free())  # 1799856

# Wireless
from interface.wireless.date import DateAPI
# from interface.wireless.location import LocationAPI
from interface.wireless.phone import PhoneAPI

# Front
from front.components.outputs import Led, Piezo
from front.components.inputs import Button, Potentiometer
from front.components.ble import Bluetooth, Characteristic, Service, Information
from front.components.display import TFT
from front.components.wifi import WifiManager, WifiStation, AccessPoint
from front.adafruit import board
from front.adafruit.stemma.veml_7700 import LuxSensor
from front.adafruit.stemma.max1704x import MAX17048
from front.adafruit.stemma.pcf8523.pcf8523 import PCF8523
from front.components.speedometer import Speedometer

gc.collect()
print(gc.mem_free())

gc.collect()

# Buttons n°
_BUTTON1 = 14 # A4
_BUTTON2 = 6  # D6
_BUTTON3 = 9 # D9
_BUTTON4 = 10  # D10
_BUTTON5 = 8  # A5
_BUTTON6 = 15  # A3
_BUTTON7 = 16  # A2
_BUTTON8 = 17  # A1

# Rear
_PIN_ACTIVATION = _BUTTON1
_PIN_FREQUENCY = _BUTTON5

# Direction
_PIN_LEFT = _BUTTON2
_PIN_RIGHT = _BUTTON4
_PIN_WARNING = _BUTTON3
_PIN_LEFT_LIGHT = 5  # D5
_PIN_RIGHT_LIGHT = 13  # D13
_PIN_BUZZER = 12  # D12

# BRAKE
_PIN_HALL = 18  # A0

# General
_PIN_BRIGHTNESS = 11 # D11
_PIN_ECO = _BUTTON7
_PIN_KEYS = _BUTTON6
_PIN_APPS = _BUTTON8

# Display
_PIN_NEXT = _PIN_RIGHT
_PIN_PREV = _PIN_LEFT
_PIN_SELECT = _PIN_ACTIVATION
_PIN_CANCEL = _PIN_WARNING

# _PIN_STATUS = 43


async def main():
    # Settings
    settings = FileSettings(r"files", template="template_0")
    settings_rear = settings.rear_settings
    settings_direction = settings.direction_settings
    settings_brake = settings.brake_settings
    settings_general = settings.general_settings
    settings.initialise_all(settings_rear, settings_direction, settings_brake, settings_general)()

    # Internet (real)
    phone = PhoneAPI(is_logging=True)
    ap = AccessPoint(is_logging=True)
    station = WifiStation(is_logging=True)
    wifi = WifiManager(ap, station, phone=phone, file=settings.creds_file)
    wifi.initialise()

    gc.collect()

    # APIs
    clock_api = DateAPI(wifi, is_logging=True)
    # location_api = LocationAPI(wifi, is_logging=True)
    # weather_api = WeatherAPI(location_api, is_logging=True)

    # ------ Inputs ------

    # Rear
    activation = Button(_PIN_ACTIVATION)
    frequency = Button(_PIN_FREQUENCY)

    # Direction
    left = Button(_PIN_LEFT)
    right = Button(_PIN_RIGHT)
    warning = Button(_PIN_WARNING)

    # General
    brightness = Potentiometer(_PIN_BRIGHTNESS, start=1, end=100)
    keys = Button(_PIN_KEYS)
    eco = Button(_PIN_ECO)
    apps = Button(_PIN_APPS)

    # Sensors
    i2c = board.I2C()  # uses board.SCL and board.SDA
    sensor_light = LuxSensor(i2c)
    sensor_battery = MAX17048(i2c)
    sensor_hall = Button(_PIN_HALL, inverse=True, pull=True)

    # Clock
    rtc = PCF8523(i2c)
    clock = Clock(rtc=rtc, api=clock_api, use_change=True, initialise_from_rtc=True)

    gc.collect()
    # ------ Outputs ------

    # Lights and Buzzers
    light_left = Led(_PIN_LEFT_LIGHT)
    light_right = Led(_PIN_RIGHT_LIGHT)
    buzzer = Piezo(_PIN_BUZZER)
    light_warning = [light_left, light_right]

    # Display
    tft_display = TFT(landscape=True)
    display = Display(tft_display, landscape=True)
    screen = Screen(display)
    screen.show()

    gc.collect()
    # ------ Bluetooth ------
    ble = Bluetooth(
        name=TFT_NAME,is_logging=True, logging_name=TFT_NAME
    ).set_as_peripheral()
    service = BikeLight(ble, service=Service, characteristic=Characteristic, information=Information, is_logging=True)
    sender_rear = RearBluetooth(service)
    sender_direction = DirectionBluetooth(service)
    sender_brake = BrakeBluetooth(service)
    receiver = ToFrontBluetooth(service)
    sender = ToBackBluetooth(service)

    # Features
    is_logging = True

    gc.collect()

    controller = Front.from_settings(
        output_left=light_left, output_right=light_right, output_warning=light_warning, output_buzzer=buzzer,
        screen=screen,
        activation=activation, frequency=frequency, modes=True, types=True, manual=True,
        dark=sensor_light, night=clock, light=sensor_light, clock=clock,
        left=left, right=right, warning=warning, beep=True,
        enable=True, speedometer=True, hall=sensor_hall, acceleration=True,
        keys=keys, apps=apps, timing=True, eco=eco, battery=sensor_battery, amplification=brightness, automatic=sensor_light,
        dis_left=left, dis_right=right, dis_select=frequency, dis_cancel=warning,
        bluetooth=ble, service=service.service, receiver=receiver, sender=sender,
        sender_rear=sender_rear, sender_dir=sender_direction, sender_brake=sender_brake,
        phone=phone,
        settings_rear=settings_rear, settings_brake=settings_brake, settings_dir=settings_direction,
        settings_general=settings_general,
        is_logging=is_logging, speedometer_class=Speedometer
    )

    settings_menu = BikeMenuSettings.from_controllers(
        screen, controller,
        wifi, settings, settings_rear, settings_direction, settings_brake, settings_general,
        settings=settings_general,
    )

    my_app = BikeApp(
        screen=screen, controller=controller, menu=settings_menu, settings=settings_general,
    )
    my_app.enter()

    gc.collect()

    await asyncio.gather(
        controller.refreshing(),
        memory(3)
    )


asyncio.run(main())

