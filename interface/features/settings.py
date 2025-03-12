
import gc
gc.collect()


# Logic -> Components
from interface.components.files import Settings, Folder, JsonFile
from interface.basic.encoding import PercentageInt, Duration, Uint16, Uint8, Float
from interface.components.lights import RED, YELLOW, LightSettings
from interface.components.indicator import IndicatorSettings

# Start, End, Step, Initial, Factor

# Display
UNIT_TEMP = ["K", "°C", "°K"]
UNIT_SPEED = ["m/s", "km/h", "mph"]
UNIT_DISTANCE = ["m", "km", "mi"]
UNIT_TIME = ["24:00", "24h00", "12:00 AM"]
UNIT_DATE = ["YY-MM-DD", "DD/MM/YY", "MM/DD/YY"]
SETTING_SPEED = ["Current", "Maximum"]
SETTING_ODOMETER = ["Trip", "ODO"]
SETTINGS_BRIGHTNESS = ["Same", "Range", "Separated"]
SETTINGS_SOURCE = ["Auto", "Pot", "Display"]

# Rear
MODES_SCALE = (0, 3, 1, 0)
MODES_TEXT = ["Manual", "Auto", "Auto ON", "Auto OFF"]
TYPES_SCALE = (0, 2, 1, 0)
TYPES_TEXT = ["Both", "Light", "Time"]
MANUAL_SCALE = (0, 2, 1, 0)
MANUAL_TEXT = ["Manual", "Semi", "Auto"]

# Brake
ENABLE_TEXT = ["Disabled", "Speedometer", "Enabled"]

# General
AMPLIFICATION_SCALE = (10, 100, 10, 10)
PERIOD_SCALE = (0, 2, 0.5, 0)


gc.collect()


class FileSettings(Settings):
    def __init__(self, folder: Folder | str = "settings", template: str = "default"):
        self.folder = Folder(folder) if isinstance(folder, str) else folder
        super().__init__(file=JsonFile.at(name="names", folder=self.folder), template=template)

        self.rear_file = JsonFile.at(name="rear", folder=self.folder)
        self.direction_file = JsonFile.at(name="direction", folder=self.folder)
        self.brake_file = JsonFile.at(name="brake", folder=self.folder)
        self.general_file = JsonFile.at(name="general", folder=self.folder)
        self.creds_file = JsonFile.at(name="creds", folder=self.folder)

    @property
    def rear_settings(self):
        return RearSettings.from_file(file=self.rear_file, template=self.template)

    @property
    def direction_settings(self):
        return DirectionSettings.from_file(file=self.direction_file, template=self.template)

    @property
    def brake_settings(self):
        return BrakeSettings.from_file(file=self.brake_file, template=self.template)

    @property
    def general_settings(self):
        return GeneralSettings.from_file(file=self.general_file, template=self.template)

    @property
    def to_dict(self):
        return {"template": self.template}

    """ User """

    def download_all(self, *settings: Settings):
        """ Download data from phone and save to file and load. """
        def wrapper(_=None):
            for setting in settings:
                setting.download()
            if len(settings) > 0:
                self.template = settings[0].template
        return wrapper

    def load_all(self, *settings: Settings):
        """ Pick a template from local and update current data. """
        def wrapper(value: str | None = None):
            for setting in settings:
                setting.load(value)
            if len(settings) > 0:
                self.template = settings[0].template
        return wrapper

    def upload_all(self, *settings: Settings):
        """ Send template to phone. """
        def wrapper(value: str | None = None):
            for setting in settings:
                setting.upload(value)
            if len(settings) > 0:
                self.template = settings[0].template
        return wrapper

    def save_all(self, *settings: Settings):
        def wrapper(_=None):
            for setting in settings:
                setting.save()
            if len(settings) > 0:
                self.template = settings[0].template
                self.save()
        return wrapper

    def initialise_all(self, *settings: Settings):
        def wrapper(_=None):
            self.initialise()
            for setting in settings:
                setting.template = self.template
                setting.initialise()
        return wrapper

    def remove_all(self, *settings: Settings):
        """ Remove template and initialize again. """
        def wrapper(_=None):
            for setting in settings:
                if setting.file is not None and not setting.file.path.endswith("default.json"):
                    setting.file.remove()
            if len(settings) > 0:
                self.template = settings[0].template
        return wrapper


gc.collect()


class GeneralSettings(Settings):
    def __init__(self,
                 file=None,

                 # Wait
                 wait_refresh_buttons: Duration = 0.05,
                 wait_change_buttons: Duration = 0.1,
                 wait_refresh_pot: Duration = 0.05,
                 wait_change_pot: Duration = 0.1,

                 wait_refresh_temp: Duration = 20,
                 wait_refresh_battery: Duration = 10,
                 wait_refresh_speedometer: Duration = 0.05,
                 wait_refresh_acceleration: Duration = 0.05,

                 wait_refresh_sending: Duration = 0.2,
                 wait_refresh_timing: Duration = 5,
                 wait_refresh_automatic: Duration = 0.1,

                 wait_refresh_dark: Duration = 0.01,
                 wait_change_dark: Duration = 5,

                 # Brightness
                 brightness_general: PercentageInt = 70,
                 brightness_display: PercentageInt = 100,
                 brightness_rear: PercentageInt = 30,
                 brightness_direction: PercentageInt = 50,
                 brightness_brake: PercentageInt = 80,
                 volume: PercentageInt = 50,

                 brightness_min: PercentageInt = 5,
                 brightness_max: PercentageInt = 90,
                 brightness_step: PercentageInt = 5,

                 brightness_display_lower: PercentageInt = 20,
                 brightness_display_upper: PercentageInt = 100,
                 brightness_rear_lower: PercentageInt = 30,
                 brightness_rear_upper: PercentageInt = 70,
                 brightness_direction_lower: PercentageInt = 30,
                 brightness_direction_upper: PercentageInt = 70,
                 brightness_brake_lower: PercentageInt = 60,
                 brightness_brake_upper: PercentageInt = 90,

                 # Settings
                 setting_speed: bool = False,
                 setting_odometer: bool = False,
                 setting_brightness: Uint8 = 1, # Initial brightness mode
                 setting_source: Uint8 = 1, # Initial source of general

                 unit_temp: Uint8 = 1,   #   K,         °C,          °F
                 unit_speed: Uint8 = 1,  # m/s (m),  km/h (km),  mph (mi)
                 unit_time: Uint8 = 0,   #   24h,       12h
                 unit_date: Uint8 = 0,   # YY-MM-DD, DD/MM/YY,  MM/DD/YY

                 # Display
                 display_activation: bool = True,
                 sending: bool = False,

                 # Sensors
                 difference_temperature: float = 0.3,
                 difference_battery: float = 0.2,
                 difference_amplification: Uint8 = 5,

                 points_automatic: int = 20,
                 light_from_low: int = 0,
                 light_from_high: int = 100,

                 # Speedometer
                 radius: float = 0.25,
                 min_speed: float = 1,
                 rounding: int = 2,
                 points_speed: int = 10,

                 # Records
                 odometer: Uint16 = 0,
                 total_duration: Uint16 = 0,
                 max_speed: float = 0,

                 # Accelerometer
                 enable: int = 2,
                 limit_acceleration: int | float = -0.15,
                 every: Duration = 1,

                 # Direction
                 delay: Duration = 0.25,

                 # Rear settings
                 modes: Uint8 = 0,
                 types: Uint8 = 0,
                 manual: Uint8 = 0,

                 # Dark and night
                 points_dark: Uint8 = 100,
                 expansion_dark: Uint16 = 50,

                 limit_evening: Float = 19,
                 limit_morning: Float = 6,
                 limit_dark: Float = 100,

                 **kwargs
                 ):
        super().__init__(file)

        # Wait
        self.wait_refresh_buttons: Duration = wait_refresh_buttons
        self.wait_change_buttons: Duration = wait_change_buttons
        self.wait_refresh_pot: Duration = wait_refresh_pot
        self.wait_change_pot: Duration = wait_change_pot
        self.wait_refresh_temp: Duration = wait_refresh_temp
        self.wait_refresh_battery: Duration = wait_refresh_battery
        self.wait_refresh_sending: Duration = wait_refresh_sending
        self.wait_refresh_timing: Duration = wait_refresh_timing
        self.wait_refresh_automatic: Duration = wait_refresh_automatic
        self.wait_refresh_acceleration: Duration = wait_refresh_acceleration
        self.wait_refresh_speedometer: Duration = wait_refresh_speedometer

        # Brightness
        self.brightness_general: PercentageInt = brightness_general
        self.brightness_display: PercentageInt = brightness_display
        self.brightness_rear: PercentageInt = brightness_rear
        self.brightness_direction: PercentageInt = brightness_direction
        self.brightness_brake: PercentageInt = brightness_brake
        self.volume = volume

        # Brightness range
        self.brightness_display_lower: PercentageInt = brightness_display_lower
        self.brightness_display_upper: PercentageInt = brightness_display_upper
        self.brightness_rear_lower: PercentageInt = brightness_rear_lower
        self.brightness_rear_upper: PercentageInt = brightness_rear_upper
        self.brightness_direction_lower: PercentageInt = brightness_direction_lower
        self.brightness_direction_upper: PercentageInt = brightness_direction_upper
        self.brightness_brake_lower: PercentageInt = brightness_brake_lower
        self.brightness_brake_upper: PercentageInt = brightness_brake_upper

        self.brightness_max: PercentageInt = brightness_max
        self.brightness_min: PercentageInt = brightness_min
        self.brightness_step: PercentageInt = brightness_step

        # Settings
        self.setting_speed: bool = setting_speed
        self.setting_odometer: bool = setting_odometer
        self.setting_brightness: Uint8 = setting_brightness
        self.setting_source: Uint8 = setting_source

        # Display
        self.unit_temp: PercentageInt = unit_temp
        self.unit_speed: PercentageInt = unit_speed
        self.unit_time: PercentageInt = unit_time
        self.unit_date: PercentageInt = unit_date

        # Display
        self.display_activation: PercentageInt = display_activation
        self.sending: bool = sending

        # Difference
        self.difference_battery = difference_battery
        self.difference_temperature = difference_temperature
        self.difference_amplification = difference_amplification

        self.points_automatic = points_automatic
        self.light_from_low = light_from_low
        self.light_from_high = light_from_high

        # Speedometer
        self.radius: float = radius
        self.min_speed: float = min_speed
        self.rounding: int = rounding

        # Records
        self.max_speed: float = max_speed
        self.odometer: Uint16 = odometer
        self.total_duration: Uint16 = total_duration

        # Accelerometer
        self.enable: int = enable
        self.every: int | float = every
        self.points_speed: int = points_speed
        self.limit_acceleration: int | float = limit_acceleration

        # Direction
        self.delay: Duration = delay

        # Wait refresh
        self.wait_refresh_dark: Duration = wait_refresh_dark
        self.wait_change_dark: Duration = wait_change_dark

        # Dark
        self.points_dark: Uint8 = points_dark
        self.expansion_dark: Uint16 = expansion_dark

        # Limits
        self.limit_evening: Float = limit_evening
        self.limit_morning: Float = limit_morning
        self.limit_dark: Float = limit_dark

        # Modes and types and manual after manual activation
        self.manual: Uint8 = manual
        self.modes: Uint8 = modes
        self.types: Uint8 = types


class GeneralBackSettings(Settings):
    def __init__(self,
                 file=None,

                 # Wait
                 wait_refresh_buttons: Duration = 0.05,
                 wait_change_buttons: Duration = 0.1,

                 wait_refresh_temp: Duration = 20,
                 wait_refresh_battery: Duration = 10,

                 # Brightness
                 brightness_rear: PercentageInt = 30,
                 brightness_direction: PercentageInt = 50,
                 brightness_brake: PercentageInt = 80,

                 # Sensors
                 difference_temperature: float = 0.3,
                 difference_battery: float = 1,
                 **kwargs
                 ):
        super().__init__(file)

        # Wait
        self.wait_refresh_buttons: Duration = wait_refresh_buttons
        self.wait_change_buttons: Duration = wait_change_buttons
        self.wait_refresh_temp: Duration = wait_refresh_temp
        self.wait_refresh_battery: Duration = wait_refresh_battery

        # Brightness
        self.brightness_rear: PercentageInt = brightness_rear
        self.brightness_direction: PercentageInt = brightness_direction
        self.brightness_brake: PercentageInt = brightness_brake

        # Difference
        self.difference_battery = difference_battery
        self.difference_temperature = difference_temperature


gc.collect()


class RearSettings(LightSettings):
    def __init__(self,
                 file=None,

                 activation: bool = False,
                 brightness: PercentageInt = 30,  # Use general

                 period: Duration = 0,
                 duty: Duration = 0,
                 fade_in: Duration = 0,
                 fade_out: Duration = 0,

                 does_fade: bool = False,
                 does_blink: bool = True,

                 **kwargs
                 ):
        super().__init__(
            file=file,
            initialize=True,
            activation=activation, colour=RED, brightness=brightness,
            period=period, duty=duty, expiration=0, fade_in=fade_in, fade_out=fade_out,
            does_fade=does_fade, does_blink=does_blink, does_expire=False,
        )


gc.collect()


class DirectionSettings(IndicatorSettings):
    def __init__(self,
                 file=None,

                 light_activation: bool = True,
                 buzzer_activation: bool = False,

                 brightness: PercentageInt = 50,
                 volume: PercentageInt = 50,

                 tone_left: Uint16 = 500,
                 tone_warning: Uint16 = 750,
                 tone_right: Uint16 = 800,

                 period: Duration = 1,
                 duty: Duration = 0,
                 fade_in: Duration = 0,
                 fade_out: Duration = 0,

                 expiration_direction: Duration = 10,
                 expiration_warning: Duration = 0,

                 does_fade: bool = False,
                 does_expire_warning: bool = False,
                 does_expire_direction: bool = True,
                 **kwargs
                 ):
        super().__init__(
            file=file,
            initialize=True,
            activation=False, colour=YELLOW, brightness=brightness, volume=volume,
            period=period, duty=duty, fade_in=fade_in, fade_out=fade_out,
            does_blink=True, does_fade=does_fade,
            light_activation=light_activation, buzzer_activation=buzzer_activation,
        )

        # Extra (indicator)
        self.tone_left: Uint16 = tone_left
        self.tone_right: Uint16 = tone_right
        self.tone_warning: Uint16 = tone_warning
        self.expiration_direction: Duration = expiration_direction
        self.expiration_warning: Duration = expiration_warning
        self.does_expire_warning: bool = does_expire_warning
        self.does_expire_direction: bool = does_expire_direction


gc.collect()


class BrakeSettings(LightSettings):
    def __init__(self,
                 file=None,

                 # Light
                 brightness: PercentageInt = 80,
                 fade_out: Duration = 2,

                 **kwargs
                 ):
        super().__init__(
            file=file,
            initialize=False, activation=False,
            colour=RED, brightness=brightness,
            period=0, duty=0,
            expiration=0, fade_in=0, fade_out=fade_out,
            does_fade=True, does_blink=False, does_expire=False,
        )


gc.collect()

