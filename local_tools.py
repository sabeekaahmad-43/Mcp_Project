import requests
from datetime import datetime


def get_weather(location: str) -> dict:
    """Get current weather for a location using Open-Meteo (no API key required)."""

    geo_response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={
            "name": location,
            "count": 1,
            "language": "en",
            "format": "json"
        },
        timeout=10
    )
    geo_response.raise_for_status()
    geo_data = geo_response.json()

    if not geo_data.get("results"):
        return {"error": f"Location '{location}' not found."}

    place = geo_data["results"][0]
    latitude = place["latitude"]
    longitude = place["longitude"]

    weather_response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,weather_code",
            "temperature_unit": "celsius"
        },
        timeout=10
    )
    weather_response.raise_for_status()
    weather_data = weather_response.json()
    current = weather_data["current"]

    return {
        "location": location,
        "temperature": current["temperature_2m"],
        "temperature_unit": "celsius",
        "weather_code": current["weather_code"]
    }


def get_current_datetime() -> str:
    """Get the current date and time."""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")