

from micropython import const
from machine import Pin
from machine import I2C as _I2C

# I2C
SDA = const(3)
SCL = const(4)
I2C_POWER = const(7)  # Needs to be pulled high

def I2C(port_id: int = 0, timeout: int = 50000, frequency: int = 400000):
    p = Pin(I2C_POWER, Pin.PULL_UP)
    p.value(1)
    return _I2C(port_id, scl=Pin(SCL), sda=Pin(SDA), freq=frequency, timeout=timeout)

# SPI
SCK = const(36)
MOSI = const(35)
MISO = const(37)

# UART
RX = const(38)
TX = const(39)

# Analog
A0 = const(18)
A1 = const(17)
A2 = const(16)
A3 = const(15)
A4 = const(14)
A5 = const(8)

# Digital
D5 = const(5)
D6 = const(6)
D9 = const(9)
D10 = const(10)
D11 = const(11)
D12 = const(12)
D13 = const(13)

# Neo-pixels
NEOPIXEL = const(33)
NEOPIXEL_POWER = const(21)  # Needs to be pulled high

# LEDs
LED = const(13)

# Buttons
D0 = const(0)  # This button is pulled HIGH by default
D1 = const(1)
D2 = const(2)

# Display (ST7789)
TFT_POWER = I2C_POWER
TFT_CS = const(42)
TFT_DC = const(40)
TFT_RESET = const(41)
TFT_BACKLIGHT = const(45)
WIDTH = const(135)
HEIGHT = const(240)

# I2C addresses (https://github.com/adafruit/Adafruit_CircuitPython_MAX1704x/blob/main/adafruit_max1704x.py)
MAX17048_ADDR = const(0x36)

# Light Sensor: VEML7700 (https://github.com/adafruit/Adafruit_CircuitPython_VEML7700)
VEML7700_ADDR = const(0x10)

# 9-axis IMU: ICM20948 (https://github.com/adafruit/Adafruit_CircuitPython_ICM20X)
ICM20948_ADDR = const(0x69)

# RTC: PCF8523 (https://github.com/adafruit/Adafruit_CircuitPython_PCF8523)
PCF8523_ADDR = const(0x01)

# Battery Monitor: LC709203F (https://github.com/adafruit/Adafruit_CircuitPython_LC709203F)
LC709203F_ADDR = const(0x02)