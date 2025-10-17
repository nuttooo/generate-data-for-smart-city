import random
import math
from datetime import datetime

class WeatherSimulator:
    """Simulate realistic weather station data"""
    
    def __init__(self):
        # Base values for Bangkok climate
        self.base_temperature = 28.0  # Celsius
        self.base_humidity = 70.0  # Percent
        self.base_pressure = 1013.25  # hPa
        
    def get_time_factor(self):
        """Get time-based factor (0-1) based on hour of day"""
        hour = datetime.now().hour
        # Temperature peaks around 2-3 PM (14-15h), lowest at 5-6 AM
        time_factor = math.sin((hour - 6) * math.pi / 12)
        return max(-1, min(1, time_factor))
    
    def generate_temperature(self):
        """Generate realistic temperature (25-35°C for Bangkok)"""
        time_factor = self.get_time_factor()
        # Temperature variation based on time of day
        temp_variation = time_factor * 4.0  # ±4°C variation
        # Add some random variation
        random_variation = random.uniform(-1.0, 1.0)
        temperature = self.base_temperature + temp_variation + random_variation
        return round(temperature, 2)
    
    def generate_humidity(self):
        """Generate realistic humidity (50-90%)"""
        time_factor = self.get_time_factor()
        # Humidity inversely related to temperature
        humidity_variation = -time_factor * 10.0  # ±10% variation
        random_variation = random.uniform(-5.0, 5.0)
        humidity = self.base_humidity + humidity_variation + random_variation
        return round(max(40.0, min(95.0, humidity)), 2)
    
    def generate_pressure(self):
        """Generate realistic atmospheric pressure (1008-1018 hPa)"""
        # Pressure variation is smaller
        random_variation = random.uniform(-3.0, 3.0)
        pressure = self.base_pressure + random_variation
        return round(pressure, 2)
    
    def generate_wind_speed(self):
        """Generate realistic wind speed (0-8 m/s for typical conditions)"""
        hour = datetime.now().hour
        # Wind typically picks up during the day
        if 10 <= hour <= 18:
            base_wind = 3.0
        else:
            base_wind = 1.5
        
        random_variation = random.uniform(-1.0, 2.0)
        wind_speed = base_wind + random_variation
        return round(max(0.0, wind_speed), 2)
    
    def generate_wind_direction(self):
        """Generate wind direction in degrees (0-359)"""
        return random.randint(0, 359)
    
    def generate_rainfall(self):
        """Generate rainfall (mostly 0, occasional rain)"""
        # 10% chance of rain
        if random.random() < 0.1:
            return round(random.uniform(0.1, 5.0), 2)
        return 0.0
    
    def generate_light_intensity(self):
        """Generate light intensity in lux (0-120000)"""
        hour = datetime.now().hour
        
        if 6 <= hour < 8:
            # Dawn
            base_lux = 10000
            variation = 5000
        elif 8 <= hour < 17:
            # Daytime
            base_lux = 80000
            variation = 20000
        elif 17 <= hour < 19:
            # Dusk
            base_lux = 15000
            variation = 8000
        else:
            # Night
            base_lux = 100
            variation = 200
        
        light = base_lux + random.uniform(-variation, variation)
        return int(max(0, light))
    
    def generate_weather_data(self):
        """Generate complete weather data"""
        return {
            'temperature_c': self.generate_temperature(),
            'humidity_percent': self.generate_humidity(),
            'pressure_hpa': self.generate_pressure(),
            'wind_speed_ms': self.generate_wind_speed(),
            'wind_direction_deg': self.generate_wind_direction(),
            'rainfall_mm': self.generate_rainfall(),
            'light_intensity_lux': self.generate_light_intensity()
        }
