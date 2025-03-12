

import gc
gc.collect()


# Built-in
from micropython import const

# Interface -> Basic
from interface.basic.encoding import (Encoder, BOOLEAN_ENCODER, UINT8_ENCODER, PERCENTAGE_INT_ENCODER, FLOAT_ENCODER)

# Interface -> Components
from interface.components.ble import Service, Characteristic, Bluetooth, Information


# =========================== #
#          Bluetooth          #
# =========================== #


# When server is FRONT and client is BACK
_NOT_USED = const(0)
_FRONT_TO_BACK = const(1)
_BACK_TO_FRONT = const(2)
_BOTH_DIRECTIONS = const(3)


# =========================== #
#         Top-classes         #
# =========================== #


class CharacteristicDefinition:

    def __init__(self, uuid: str |int, server: int = 2, encoder: Encoder | None = None, name: str = None, ):
        self.uuid = uuid
        self.server = server
        self.encoder = encoder
        self.name = name

    def make_characteristic(self, service: Service, _class: type[Characteristic] = Characteristic,
                            is_logging: bool | None = None, style: str | None = None) -> Characteristic:
        return _class(
            uuid=self.uuid,
            service=service, server=self.server, encoder=self.encoder,
            name=self.name, is_logging=is_logging, style=style
        )


gc.collect()


class InformationDefinition:

    def __init__(self, encoder: Encoder, name: str = None, ):
        self.encoder = encoder
        self.name = name

    def make_information(self, characteristic: Characteristic, _class: type[Information] = Information,
                            is_logging: bool | None = None, style: str | None = None) -> Information:
        return _class(
            characteristic=characteristic, encoder=self.encoder, name=self.name, is_logging=is_logging, style=style
        )


gc.collect()


# =========================== #
#           Specific          #
# =========================== #


class BikeLight:
    # Service
    SERVICE = "0adf3b2b-9772-4302-ae25-d15939407b89"

    """ Generic """
    GENERIC = CharacteristicDefinition(
        "5b5716df-51e1-4de8-8199-71860c0b69cf", _FRONT_TO_BACK, name="BleGeneric"
    )

    # Informations

    # Rear
    REAR_ACTIVATION = InformationDefinition(BOOLEAN_ENCODER, "BleRearActivation")
    REAR_FREQUENCY = InformationDefinition(FLOAT_ENCODER, "BleRearFrequency")
    REAR_BRIGHTNESS = InformationDefinition(PERCENTAGE_INT_ENCODER, "BleRearBrightness")

    # Direction
    DIR_ACTIVATION = InformationDefinition(UINT8_ENCODER, "BleDirActivation")
    DIR_BRIGHTNESS = InformationDefinition(PERCENTAGE_INT_ENCODER, "BleDirBrightness")

    # Brake
    BRAKE_ACTIVATION = InformationDefinition(BOOLEAN_ENCODER, "BleBrakeActivation")
    BRAKE_BRIGHTNESS = InformationDefinition(PERCENTAGE_INT_ENCODER, "BleBrakeBrightness")

    # General
    GENERAL_ECO = InformationDefinition(BOOLEAN_ENCODER, "GeneralEco")

    """ Back to front """
    BLUEFRUIT = CharacteristicDefinition(
        "46acacdb-30c5-49ab-bbbb-a09e0b4cb1b6", _BACK_TO_FRONT, name="BleBack"
    )

    BLUEFRUIT_TEMPERATURE = InformationDefinition(FLOAT_ENCODER, "BleBackTemperature")
    BLUEFRUIT_BATTERY = InformationDefinition(FLOAT_ENCODER, "BleBackBattery")


    def __init__(self, bluetooth: Bluetooth,
                 is_logging: bool | None = None, is_logging_char: bool | None = None, is_logging_info: bool | None = None,
                 style: str | None = None,
                 service: type[Service] = Service, characteristic: type[Characteristic] = Characteristic,
                 information: type[Information] = Information):

        self.service = service(self.SERVICE, bluetooth)

        # Generic
        self.generic = self.GENERIC.make_characteristic(
            self.service, characteristic, is_logging if is_logging_char is None else is_logging_char, style
        )

        args = (self.generic, information, is_logging if is_logging_info is None else is_logging_info, style)
        self.rear_activation = self.REAR_ACTIVATION.make_information(*args)
        self.rear_brightness = self.REAR_BRIGHTNESS.make_information(*args)
        self.rear_frequency = self.REAR_FREQUENCY.make_information(*args)
        self.dir_activation = self.DIR_ACTIVATION.make_information(*args)
        self.dir_brightness = self.DIR_BRIGHTNESS.make_information(*args)
        self.brake_activation = self.BRAKE_ACTIVATION.make_information(*args)
        self.brake_brightness = self.BRAKE_BRIGHTNESS.make_information(*args)
        self.general_eco = self.GENERAL_ECO.make_information(*args)

        # From back
        self.bluefruit = self.BLUEFRUIT.make_characteristic(
            self.service, characteristic, is_logging if is_logging_char is None else is_logging_char, style
        )
        args = (self.bluefruit, information, is_logging if is_logging_info is None else is_logging_info, style)
        self.bluefruit_temperature = self.BLUEFRUIT_TEMPERATURE.make_information(*args)
        self.bluefruit_battery = self.BLUEFRUIT_BATTERY.make_information(*args)


gc.collect()


# =========================== #
#           Feature           #
# =========================== #


class FeatureBluetooth:
    def __init__(self, wireless: BikeLight):
        self.wireless = wireless


gc.collect()


class PropertyBluetooth:
    def __init__(self, name: str):
        self.name = name
        self.setter = lambda instance: self.__get__(instance, None)

    def __get__(self, instance: FeatureBluetooth, _class: type[FeatureBluetooth] = None):
        return getattr(getattr(instance, "wireless"), self.name)

    def __set__(self, instance: FeatureBluetooth, value):
        setattr(getattr(instance, "wireless"), self.name, value)


gc.collect()


# =========================== #
#           Specific          #
# =========================== #


class ToBackBluetooth(FeatureBluetooth):
    eco = PropertyBluetooth("general_eco")


class ToFrontBluetooth(FeatureBluetooth):
    temperature = PropertyBluetooth("bluefruit_temperature")
    battery = PropertyBluetooth("bluefruit_battery")


class RearBluetooth(FeatureBluetooth):
    activation = PropertyBluetooth("rear_activation")
    brightness = PropertyBluetooth("rear_brightness")
    frequency = PropertyBluetooth("rear_frequency")


class DirectionBluetooth(FeatureBluetooth):
    activation = PropertyBluetooth("dir_activation")
    brightness = PropertyBluetooth("dir_brightness")


class BrakeBluetooth(FeatureBluetooth):
    activation = PropertyBluetooth("brake_activation")
    brightness = PropertyBluetooth("brake_brightness")


gc.collect()
