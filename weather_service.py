"""Weather service for interacting with the OpenWeatherMap API."""
import requests
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class WeatherServiceError(Exception):
    """Base exception for weather service errors."""
    pass

class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API."""
    
    BASE_URL = "http://api.openweathermap.org/data/2.5"
    
    def __init__(self, api_key: str, units: str = 'metric'):
        """Initialize the weather service.
        
        Args:
            api_key: OpenWeatherMap API key
            units: Units of measurement ('metric' or 'imperial')
        """
        self.api_key = api_key
        self.units = units
        self.session = requests.Session()
    
    def is_service_ready(self) -> bool:
        """Check if the weather service is ready (API key is set)."""
        return bool(self.api_key)
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a request to the OpenWeatherMap API.
        
        Args:
            endpoint: API endpoint
            params: Request parameters
            
        Returns:
            JSON response as a dictionary
            
        Raises:
            WeatherServiceError: If the request fails
        """
        if params is None:
            params = {}
            
        params['appid'] = self.api_key
        params['units'] = self.units
        
        try:
            response = self.session.get(f"{self.BASE_URL}/{endpoint}", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise WeatherServiceError(f"Failed to fetch weather data: {str(e)}") from e
    
    def get_current_weather(self, city: str, country_code: str = '') -> Dict:
        """Get current weather for a city.
        
        Args:
            city: City name
            country_code: Optional country code (e.g., 'US')
            
        Returns:
            Current weather data
        """
        query = f"{city},{country_code}" if country_code else city
        return self._make_request("weather", {'q': query})
    
    def get_weather_by_coords(self, lat: float, lon: float) -> Dict:
        """Get current weather by coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Current weather data
        """
        return self._make_request("weather", {'lat': lat, 'lon': lon})
    
    def get_forecast(self, city: str, country_code: str = '', days: int = 5) -> Dict:
        """Get weather forecast for a city.
        
        Args:
            city: City name
            country_code: Optional country code (e.g., 'US')
            days: Number of days of forecast (1-5)
            
        Returns:
            Forecast data
        """
        query = f"{city},{country_code}" if country_code else city
        return self._make_request("forecast", {'q': query, 'cnt': days * 8})  # 8 measurements per day
    
    def get_forecast_by_coords(self, lat: float, lon: float, days: int = 5) -> Dict:
        """Get weather forecast by coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            days: Number of days of forecast (1-5)
            
        Returns:
            Forecast data
        """
        return self._make_request("forecast", {'lat': lat, 'lon': lon, 'cnt': days * 8})
    
    def get_weather_icon_url(self, icon_code: str) -> str:
        """Get URL for weather icon.
        
        Args:
            icon_code: Weather icon code (e.g., '01d')
            
        Returns:
            URL to weather icon
        """
        return f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
    
    def parse_weather_data(self, data: Dict) -> Dict:
        """Parse weather data from API response.
        
        Args:
            data: Raw API response
            
        Returns:
            Parsed weather data
        """
        try:
            weather = data.get('weather', [{}])[0]
            main = data.get('main', {})
            wind = data.get('wind', {})
            sys = data.get('sys', {})
            
            return {
                'city': data.get('name', 'Unknown'),
                'country': sys.get('country', ''),
                'temp': main.get('temp', 0),
                'feels_like': main.get('feels_like', 0),
                'temp_min': main.get('temp_min', 0),
                'temp_max': main.get('temp_max', 0),
                'pressure': main.get('pressure', 0),
                'humidity': main.get('humidity', 0),
                'wind_speed': wind.get('speed', 0),
                'wind_deg': wind.get('deg', 0),
                'description': weather.get('description', '').title(),
                'icon': weather.get('icon', ''),
                'sunrise': datetime.fromtimestamp(sys.get('sunrise', 0)),
                'sunset': datetime.fromtimestamp(sys.get('sunset', 0)),
                'dt': datetime.fromtimestamp(data.get('dt', 0)),
                'timezone': data.get('timezone', 0),
                'visibility': data.get('visibility', 0) / 1000 if data.get('visibility') else None,  # Convert to km
                'clouds': data.get('clouds', {}).get('all', 0),
                'rain': data.get('rain', {}).get('1h', 0) if 'rain' in data else 0,
                'snow': data.get('snow', {}).get('1h', 0) if 'snow' in data else 0
            }
        except Exception as e:
            logger.error(f"Error parsing weather data: {e}")
            raise WeatherServiceError(f"Failed to parse weather data: {str(e)}") from e
    
    def parse_forecast_data(self, data: Dict) -> List[Dict]:
        """Parse forecast data from API response.
        
        Args:
            data: Raw API response
            
        Returns:
            List of parsed forecast data points
        """
        try:
            forecast_list = []
            for item in data.get('list', []):
                weather = item.get('weather', [{}])[0]
                main = item.get('main', {})
                wind = item.get('wind', {})
                
                forecast_list.append({
                    'dt': datetime.fromtimestamp(item.get('dt', 0)),
                    'temp': main.get('temp', 0),
                    'feels_like': main.get('feels_like', 0),
                    'temp_min': main.get('temp_min', 0),
                    'temp_max': main.get('temp_max', 0),
                    'pressure': main.get('pressure', 0),
                    'humidity': main.get('humidity', 0),
                    'wind_speed': wind.get('speed', 0),
                    'wind_deg': wind.get('deg', 0),
                    'description': weather.get('description', '').title(),
                    'icon': weather.get('icon', ''),
                    'clouds': item.get('clouds', {}).get('all', 0),
                    'rain': item.get('rain', {}).get('3h', 0) if 'rain' in item else 0,
                    'snow': item.get('snow', {}).get('3h', 0) if 'snow' in item else 0,
                    'pop': item.get('pop', 0)  # Probability of precipitation
                })
            return forecast_list
        except Exception as e:
            logger.error(f"Error parsing forecast data: {e}")
            raise WeatherServiceError(f"Failed to parse forecast data: {str(e)}") from e
