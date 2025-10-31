"""
Weather information using Open-Meteo API (free, no key required)
"""

import requests
from typing import Optional, Dict

class WeatherAction:
    def __init__(self, settings):
        self.settings = settings
        self.api_url = settings.WEATHER_API_URL
        self.geocode_url = settings.WEATHER_GEOCODING_URL
        self.default_location = settings.DEFAULT_LOCATION
    
    def get_coordinates(self, location: str) -> Optional[Dict]:
        """Get lat/lon for a location"""
        try:
            params = {
                "name": location,
                "count": 1,
                "language": "en",
                "format": "json"
            }
            
            response = requests.get(self.geocode_url, params=params, timeout=10)
            data = response.json()
            
            results = data.get("results", [])
            if results:
                result = results[0]
                return {
                    "lat": result["latitude"],
                    "lon": result["longitude"],
                    "name": result["name"],
                    "country": result.get("country", "")
                }
            return None
        
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None
    
    def get_weather(self, location: Optional[str] = None) -> str:
        """Get weather information"""
        try:
            # Use configured default location if not provided
            if not location:
                location = self.default_location
            
            # Get coordinates for the location
            coords = self.get_coordinates(location)
            
            if not coords:
                return f"I couldn't find the location '{location}'. Please try a different city name."
            
            # Get weather data
            params = {
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                "timezone": "auto"
            }
            
            response = requests.get(self.api_url, params=params, timeout=10)
            data = response.json()
            
            current = data.get("current", {})
            
            temp = current.get("temperature_2m")
            humidity = current.get("relative_humidity_2m")
            wind_speed = current.get("wind_speed_10m")
            weather_code = current.get("weather_code")
            
            # Interpret weather code
            weather_desc = self._interpret_weather_code(weather_code)
            
            location_name = f"{coords['name']}, {coords['country']}"
            
            weather_report = f"Weather in {location_name}: "
            weather_report += f"Currently {weather_desc} with a temperature of {temp}°C. "
            weather_report += f"Humidity is {humidity}% and wind speed is {wind_speed} km/h."
            
            return weather_report
        
        except requests.exceptions.Timeout:
            return "Weather service timed out. Please try again."
        except requests.exceptions.ConnectionError:
            return "Cannot connect to weather service. Check your internet connection."
        except Exception as e:
            return f"Error getting weather: {str(e)}"
    
    def _interpret_weather_code(self, code: int) -> str:
        """Convert WMO weather code to description"""
        weather_codes = {
            0: "clear sky",
            1: "mainly clear",
            2: "partly cloudy",
            3: "overcast",
            45: "foggy",
            48: "depositing rime fog",
            51: "light drizzle",
            53: "moderate drizzle",
            55: "dense drizzle",
            61: "slight rain",
            63: "moderate rain",
            65: "heavy rain",
            71: "slight snow",
            73: "moderate snow",
            75: "heavy snow",
            77: "snow grains",
            80: "slight rain showers",
            81: "moderate rain showers",
            82: "violent rain showers",
            85: "slight snow showers",
            86: "heavy snow showers",
            95: "thunderstorm",
            96: "thunderstorm with slight hail",
            99: "thunderstorm with heavy hail"
        }
        
        return weather_codes.get(code, "unknown conditions")