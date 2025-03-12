

from interface.wireless.api import API
from interface.wireless.location import LocationAPI

URL = "https://api.open-meteo.com/v1"

class WeatherProperty:

    def __init__(self, category: str, name: str, unit: bool = False, index: bool = False):
        self.category = category
        self.name = name
        self.unit = unit
        self.index = index

    def __get__(self, instance: 'WeatherAPI', owner: type['WeatherAPI']):
        value = instance.data.get(self.category, {}).get(self.name, None)
        if self.index and isinstance(value, list):
            value = value[0]
        if self.unit:
            unit = instance.data.get(f"{self.category}_units", {}).get(self.name, "")
            return f"{value} {unit}"
        return value


class WeatherAPI(API):

    temperature = WeatherProperty("current", name="temperature_2m")
    feels = WeatherProperty("current", name="apparent_temperature")
    humidity = WeatherProperty("current", name="relative_humidity_2m")
    precipitation = WeatherProperty("current", name="precipitation")
    pressure = WeatherProperty("current", name="surface_pressure")
    cloudiness = WeatherProperty("current", name="cloudiness")
    wind_speed = WeatherProperty("current", name="wind_speed_10m")
    wind_direction = WeatherProperty("current", name="wind_direction_10m")
    temperature_max = WeatherProperty("daily", name="temperature_2m_max", index=True)
    temperature_min = WeatherProperty("daily", name="temperature_2m_min", index=True)
    sunset = WeatherProperty("daily", name="sunset", index=True)
    sunrise = WeatherProperty("daily", name="sunrise", index=True)

    temperature_unit = WeatherProperty("current_units", name="temperature_2m")
    feels_unit = WeatherProperty("current_units", name="apparent_temperature")
    humidity_unit = WeatherProperty("current_units", name="relative_humidity_2m")
    precipitation_unit = WeatherProperty("current_units", name="precipitation")
    pressure_unit = WeatherProperty("current_units", name="surface_pressure")
    cloudiness_unit = WeatherProperty("current_units", name="cloudiness")
    wind_speed_unit = WeatherProperty("current_units", name="wind_speed_10m")
    wind_direction_unit = WeatherProperty("current_units", name="wind_direction_10m")
    temperature_max_unit = WeatherProperty("daily", name="temperature_2m_max", index=True)
    temperature_min_unit = WeatherProperty("daily", name="temperature_2m_min", index=True)
    sunset_unit = WeatherProperty("daily_units", name="sunset", index=True)
    sunrise_unit = WeatherProperty("daily_units", name="sunrise", index=True)

    temperature_str = WeatherProperty("current", name="temperature_2m", unit=True)
    feels_str = WeatherProperty("current", name="apparent_temperature", unit=True)
    humidity_str = WeatherProperty("current", name="relative_humidity_2m", unit=True)
    precipitation_str = WeatherProperty("current", name="precipitation", unit=True)
    pressure_str = WeatherProperty("current", name="surface_pressure", unit=True)
    cloudiness_str = WeatherProperty("current", name="cloudiness", unit=True)
    wind_speed_str = WeatherProperty("current", name="wind_speed_10m", unit=True)
    wind_direction_str = WeatherProperty("current", name="wind_direction_10m", unit=True)
    temperature_max_str = WeatherProperty("daily", name="temperature_2m_max", unit=True, index=True)
    temperature_min_str = WeatherProperty("daily", name="temperature_2m_min", unit=True, index=True)
    sunset_str = WeatherProperty("daily", name="sunset", unit=True, index=True)
    sunrise_str = WeatherProperty("daily", name="sunrise", unit=True, index=True)

    def __init__(self, location: LocationAPI | None = None, unit: int = 1,
                 name: str | None = None, is_logging: bool | None = None, style: str | None = None):
        super().__init__(URL, wifi=location.wifi if location is not None else None, name=name, is_logging=is_logging, style=style)

        self.location = location
        self.data = {}

    def get_from_ip(self):
        try:
            self.location.make_from_ip()
            params = {
                "latitude": self.location.latitude,
                "longitude": self.location.longitude,
                "timezone": self.location.timezone,
                "current": ["temperature_2m", "apparent_temperature", "relative_humidity_2m", "precipitation", "cloud_cover",
                            "surface_pressure", "wind_speed_10m", "wind_direction_10m"],
                "daily": ["sunrise", "sunset", "temperature_2m_max", "temperature_2m_min"],
                "forecast_days": 1
            }
            return self.get(f"forecast", query=params)
        except Exception as e:
            self.logging(f"Error when trying to access the WeatherAPI, .get_from_ip(): {e}", "ERROR")
            return None

    def make_from_ip(self):
        try:
            data = self.get_from_ip()
            if data is not None:
                self.data = data.json()
        except Exception as e:
            self.logging(f"Error when trying to access the WeatherAPI, .make_from_ip(): {e}", "ERROR")
        return self.temperature_str, self.wind_speed_str, self.sunset, self.sunrise

    def read(self):
        """ Returns the sunset, sunrise, temperature, humidity, precipitation and cloud cover. Other data is retrievable..."""
        self.make_from_ip()
        return self.sunset, self.sunrise, self.temperature, self.humidity, self.precipitation, self.cloudiness

