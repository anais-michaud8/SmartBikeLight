# Data from https://www.vishay.com/docs/84286/veml7700.pdf and https://www.vishay.com/docs/84323/designingveml7700.pdf

from machine import I2C
from micropython import const

from front.adafruit.i2c import I2CDevice, RWBits, RWBit, ROUnaryStruct

# Address
ADDR = const(0x10)

# Read/Write Registers
_ALS_CONF_0 = const(0x00)  # ALS gain, integration time, interrupt, and shutdown
_ALS_WH = const(0x01)      # ALS high threshold window setting
_ALS_WL = const(0x02)      # ALS low threshold window setting
_POW_SAV = const(0x03)     # Set (15 : 3) 0000 0000 0000 0b

# Read Registers
_ALS = const(0x04)         # Ambient light sensor high resolution output data
_WHITE = const(0x05)       # White channel output data
_INTERRUPT = const(0x06)   # ALS INT trigger event
_DEV_ID = const(0x07)      # Device ID

# Ambient light sensor gain settings
_ALS_GAIN_1 = const(0x0)
_ALS_GAIN_2 = const(0x1)
_ALS_GAIN_1_8 = const(0x2)
_ALS_GAIN_1_4 = const(0x3)
_ALS_GAIN = [_ALS_GAIN_2, _ALS_GAIN_1, _ALS_GAIN_1_4, _ALS_GAIN_1_8]

# Ambient light integration time settings
_ALS_25MS = const(0xC)
_ALS_50MS = const(0x8)
_ALS_100MS = const(0x0)
_ALS_200MS = const(0x1)
_ALS_400MS = const(0x2)
_ALS_800MS = const(0x3)
_ALS_IT = [_ALS_25MS, _ALS_50MS, _ALS_100MS, _ALS_200MS, _ALS_400MS, _ALS_800MS]


class LuxSensor:
    # Read/Write Registers

    # ALS_CONF_0 - ALS gain, integration time, shutdown.
    conf_shutdown = RWBit(_ALS_CONF_0, 0, register_width=2)
    conf_interrupt = RWBit(_ALS_CONF_0, 1, register_width=2)
    conf_pers = RWBits(2, _ALS_CONF_0, 4, register_width=2)
    conf_it = RWBits(4, _ALS_CONF_0, 6, register_width=2)
    conf_gain = RWBits(2, _ALS_CONF_0, 11, register_width=2)

    #
    # als_wh = ROUnaryStruct(_ALS_WH)
    # als_wl = ROUnaryStruct(_ALS_WL)
    # als_pw = ROUnaryStruct(_POW_SAV)

    # Read Registers
    light = ROUnaryStruct(_ALS, "<H")
    white = ROUnaryStruct(_WHITE, "<H")
    # interrupt = ROUnaryStruct(_INTERRUPT, "<H")
    # device = ROUnaryStruct(_DEV_ID, "<H")

    def __init__(self, i2c: I2C, address: hex = ADDR, gain: int = 0, it: int = 2, correct: bool = False):
        """

        Args:
            i2c (I2C):
            address (hex):
            gain (int):
                Gain -> [2, 1, 1/4, 1/8]
            it (int):
                Integration -> [25, 50, 100, 200, 400, 800]
        """
        self.i2c_device = I2CDevice(i2c, address)

        self._gain = gain
        self._it = it
        self._resolution = 0.0042 * 2/[2, 1, 1/4, 1/8][self.gain] * 800/[25, 50, 100, 200, 400, 800][self.it]

        self._correct = correct

        self.start()

    # Properties

    @property
    def gain(self) -> int:
        return self._gain

    @gain.setter
    def gain(self, gain: int) -> None:
        self._gain = gain
        self.conf_gain = _ALS_GAIN[gain]
        self._set_resolution()

    @property
    def it(self) -> int:
        return self._it

    @it.setter
    def it(self, it: int) -> None:
        self._it = it
        self.conf_it = _ALS_IT[it]
        self._set_resolution()

    def _set_resolution(self):
        self._resolution = 0.0042 * 2/[2, 1, 1/4, 1/8][self.gain] * 800/[25, 50, 100, 200, 400, 800][self.it]

    @property
    def resolution(self) -> float:
        return self._resolution

    # Start and stop measuring

    def start(self):
        self.conf_shutdown = False
        self.conf_gain = _ALS_GAIN[self.gain]
        self.conf_it = _ALS_IT[self.it]

    def stop(self):
        self.conf_shutdown = True

    # Read

    @staticmethod
    def corrector(lux: float) -> float:
        return 6.0135e-13 * lux ** 4 - 9.3924e-9 * lux ** 3 + 8.1488e-5 * lux ** 2 + 1.0023 * lux

    @property
    def lux(self) -> float:
        return self.corrector(self.light * self.resolution) if self._correct else self.resolution * self.light

    @property
    def value(self) -> float:
        return self.lux
    