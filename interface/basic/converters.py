
import gc
gc.collect()

import math

# =========================== #
#        Time and Date        #
# =========================== #

# Float <-> (hours, minutes)

def float_to_hm(value: float):
    hours = int(value)
    minutes = int((value - hours) * 60)
    return hours, minutes

def hm_to_float(hours: int, minutes: int):
    return hours + minutes/60

gc.collect()

# Formatters

def duration_formatter(value: float):
    """ Convert seconds to text of length 6. """
    value = int(value)
    # In mins:secs
    if value <= 3600:
        return f"{value // 60:02}m{value % 60:02}s"
    value = value // 60 # In minutes
    # In hours:mins
    if value <= 3600:
        return f"{value // 60:02}h{value % 60:02}m"
    value = value // 60 # In hours
    # In days:hours
    return f"{value // 60:02}h{value % 60:02}m"


def time_formatter(value: float | int, hours: int | None = None, minutes: int | None = None, seconds: int | None = None,
                   unit: int = 0, space: bool = False):
    """ Convert time (in hours) to adequate unit: ["24:00", "24h00", "12:00AM" or "12:00 AM"] """
    hours = int(value) % 24 if hours is None else hours
    minutes = int((value - hours) * 60) if minutes is None else minutes
    part = 'm' if unit == 1 else ':'
    seconds = f"{part}{seconds:02}" if seconds is not None else ""
    space = " " if space else ""
    return f"{hours:02}h{minutes:02}{seconds}" if unit == 1 \
        else f"{hours%12:02}:{minutes:02}{space}{'PM' if hours//12 else 'AM'}".replace("00:", "12:") + seconds if unit == 2 \
        else f"{hours:02}:{minutes:02}{seconds}"


def date_formatter(year: int, month: int, day: int, unit: int = 0, crop: bool = False):
    """ Convert date (from year, month, day) to adequate unit: ["YY-MM-DD", "DD/MM/YY", "MM/DD/YY"]. """
    year = f"{year:04}"[2:] if crop else f"{year:04}"
    return f"{day:02}/{month:02}/{year}" if unit == 1 \
        else f"{month:02}/{day:02}/{year}" if unit == 2 \
        else f"{year}-{month:02}-{day:02}"

gc.collect()

# =========================== #
#         Speedometer         #
# =========================== #


def period_to_angular_speed(period: float) -> float:
    """
    \omega = 2\pi / T

    Args:
        period :
            The period of the wheel in seconds.
    Returns:
        The angular speed of the wheel in radians/seconds.

    """
    return 2 * math.pi/period if period > 0 else 0

def angular_speed_to_period(angular: float) -> float:
    """
    T = 2\pi / \omega

    Args:
        angular :
            The angular speed of the wheel in radians/seconds.

    Returns:
        The period of the revolution of the wheel in seconds.
    """
    return 2*math.pi/angular if angular > 0 else 0


def angular_speed_to_linear_speed(angular: float, radius: float) -> float:
    """
    v = \omega * r

    Args:
        angular :
            The angular speed of the wheel in radians/seconds.
        radius :
            The radius of the wheel in meters.

    Returns:
        The linear speed of the wheel in meters/seconds.
    """
    return angular * radius

def linear_speed_to_angular_speed(linear: float, radius: float) -> float:
    """
    \omega = v/r

    Args:
        linear :
            The linear speed of the wheel in meters/seconds.
        radius :
            The radius of the wheel in meters.

    Returns:
        The angular speed of the wheel in radians/seconds.
    """
    return linear / radius if radius > 0 else 0


def period_to_linear_speed(period: float, radius: float) -> float:
    return angular_speed_to_linear_speed(period_to_angular_speed(period), radius)

def linear_speed_to_period(linear: float, radius: float) -> float:
    return angular_speed_to_period(linear_speed_to_angular_speed(linear, radius))


def acceleration(u: float, v: float, t: float) -> float:
    return (v-u)/t if t != 0 else 0

def displacement(u: float, v: float, t: float) -> float:
    return 0.5*(u+v)*t


gc.collect()


# =========================== #
#       Speed Conversion      #
# =========================== #


def ms_to_kmh(value: float) -> float:
    return value * 3.6

def kmh_to_ms(value: float) -> float:
    return value / 3.6

def km_to_miles(value: float) -> float:
    return value / 1.609

def miles_to_km(value: float) -> float:
    return value * 1.609


def speed_converter(value: float, unit: int = 1) -> float:
    """ Convert m/s to [m/s, km/h, mph]. """
    return ms_to_kmh(value) if unit == 1 else ms_to_kmh(km_to_miles(value)) if unit == 2 else value

def distance_converter(value: float, unit: int = 1) -> float:
    """ Convert m/s to [m, km, mi]. """
    return value/1000 if unit == 1 else km_to_miles(value/1000) if unit == 2 else value

gc.collect()


# =========================== #
#         Temperature         #
# =========================== #


def celsius_to_kelvin(celsius: float) -> float:
    return celsius - 273.15

def kelvin_to_celsius(kelvin: float) -> float:
    return kelvin + 273.15

def celsius_to_fahrenheit(celsius: float) -> float:
    return celsius * 1.8 + 32

def fahrenheit_to_celsius(fahrenheit: float) -> float:
    return (fahrenheit - 32 ) / 1.8


def temperature_converter(celsius, unit: int = 1):
    """ Convert celsius to [Kelvin, Celsius, Fahrenheit] """
    return celsius if unit == 1 else celsius_to_fahrenheit(celsius) if unit == 2 else celsius_to_kelvin(celsius)


gc.collect()
