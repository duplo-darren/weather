import requests
from flask import Flask, render_template

app = Flask(__name__)

# Location configuration
LATITUDE = 40.7968
LONGITUDE = -74.4815
CITY = "Morristown, NJ"
TIMEZONE = "America/New_York"
TEMP_UNIT = "fahrenheit"  # "celsius" or "fahrenheit"
WIND_UNIT = "mph"  # "kmh" or "mph"


def get_weather():
    """Fetch current weather from Open-Meteo API."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        "temperature_unit": TEMP_UNIT,
        "wind_speed_unit": WIND_UNIT,
        "timezone": TIMEZONE,
    }

    temp_symbol = "°C" if TEMP_UNIT == "celsius" else "°F"
    wind_symbol = "km/h" if WIND_UNIT == "kmh" else "mph"

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        current = data.get("current", {})
        weather_code = current.get("weather_code", 0)

        return {
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "wind_speed": current.get("wind_speed_10m"),
            "condition": get_weather_condition(weather_code),
            "icon": get_weather_icon(weather_code),
            "temp_unit": temp_symbol,
            "wind_unit": wind_symbol,
            "success": True,
        }
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}


def get_weather_condition(code):
    """Convert WMO weather code to human-readable condition."""
    conditions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }
    return conditions.get(code, "Unknown")


def get_weather_icon(code):
    """Get emoji icon for weather code."""
    if code == 0:
        return "☀️"
    elif code in [1, 2]:
        return "⛅"
    elif code == 3:
        return "☁️"
    elif code in [45, 48]:
        return "🌫️"
    elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        return "🌧️"
    elif code in [71, 73, 75]:
        return "❄️"
    elif code in [95, 96, 99]:
        return "⛈️"
    return "🌡️"


@app.route("/")
def home():
    weather = get_weather()
    return render_template("index.html", weather=weather, city=CITY)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
