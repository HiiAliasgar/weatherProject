import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import numpy as np
import pandas as pd
from django.shortcuts import render
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
COUNTRY_LOOKUP_URL = "https://restcountries.com/v3.1/name"
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "weather.csv"
IMG_DIR = Path(__file__).resolve().parent / "static" / "img"

WEATHER_IMAGE_KEYWORDS = {
    "thunder": ["thunder"],
    "storm": ["thunder"],
    "blizzard": ["blizzard", "snow"],
    "snow": ["snow"],
    "sleet": ["sleet", "snow"],
    "ice": ["ice", "snow"],
    "drizzle": ["drizzle", "rain"],
    "shower": ["shower", "showers", "rain"],
    "rain": ["rain"],
    "fog": ["fog", "mist"],
    "mist": ["mist", "fog"],
    "haze": ["haze", "mist", "fog"],
    "overcast": ["overcast", "cloudy"],
    "cloud": ["cloudy", "overcast"],
    "clear": ["clear", "sunny"],
    "sun": ["sunny", "clear"],
}

WEATHER_MAIN_IMAGE_MAP = {
    "thunderstorm": ["thunder"],
    "drizzle": ["drizzle", "rain"],
    "rain": ["rain", "shower"],
    "snow": ["snow", "blizzard"],
    "mist": ["mist", "fog"],
    "smoke": ["mist", "fog"],
    "haze": ["haze", "mist", "fog"],
    "dust": ["fog", "mist"],
    "fog": ["fog", "mist"],
    "sand": ["fog", "mist"],
    "ash": ["fog", "mist"],
    "squall": ["cloudy", "overcast"],
    "tornado": ["thunder"],
    "clear": ["clear", "sunny"],
    "clouds": ["cloudy", "overcast"],
}


def resolve_location_query(city):
    query = (city or "").strip()
    if not query:
        return query

    # If user enters a country name (e.g., "Kenya"), prefer its capital city.
    try:
        country_url = (
            f"{COUNTRY_LOOKUP_URL}/{quote(query)}"
            "?fullText=true&fields=capital,cca2"
        )
        with urlopen(country_url, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        if isinstance(data, list) and data:
            first = data[0]
            capital_list = first.get("capital") or []
            country_code = (first.get("cca2") or "").strip()
            if capital_list:
                capital = str(capital_list[0]).strip()
                if capital and country_code:
                    return f"{capital},{country_code}"
                if capital:
                    return capital
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, ValueError):
        pass

    return query


def get_current_weather(city):
    params = urlencode({"q": city, "appid": API_KEY, "units": "metric"})

    with urlopen(f"{BASE_URL}?{params}", timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))

    wind = data.get("wind", {})
    wind_speed_mps = float(wind.get("speed", 0) or 0)
    return {
        "city": data["name"],
        "weather_main": data["weather"][0].get("main", ""),
        "current_temp": round(data["main"]["temp"]),
        "feels_like": round(data["main"]["feels_like"]),
        "temp_min": round(data["main"]["temp_min"]),
        "temp_max": round(data["main"]["temp_max"]),
        "pressure": data["main"]["pressure"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
        "country": data["sys"]["country"],
        "wind_gust_dir": wind.get("deg", 0),
        "wind_gust_speed": round(wind_speed_mps * 3.6, 1),
        "clouds": data["clouds"]["all"],
        "visibility": data.get("visibility", 0),
        "timezone_offset": data.get("timezone", 0),
        "lat": data["coord"]["lat"],
        "lon": data["coord"]["lon"],
    }


def get_hourly_forecast(lat, lon, timezone_offset=0, count=5):
    params = urlencode(
        {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric", "cnt": count}
    )

    with urlopen(f"{FORECAST_URL}?{params}", timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))

    city_timezone_offset = data.get("city", {}).get("timezone", timezone_offset)
    forecast_data = []

    for item in data.get("list", [])[:count]:
        timestamp = item.get("dt")
        main = item.get("main", {})
        if timestamp is None or not main:
            continue

        local_time = datetime.fromtimestamp(timestamp + city_timezone_offset, tz=timezone.utc)
        forecast_data.append(
            {
                "time": local_time.strftime("%H:00"),
                "temp": round(float(main.get("temp", 0)), 1),
                "humidity": round(float(main.get("humidity", 0)), 1),
            }
        )

    return forecast_data


def resolve_weather_candidates(weather_main, description):
    weather_main = (weather_main or "").lower()
    if weather_main in WEATHER_MAIN_IMAGE_MAP:
        return WEATHER_MAIN_IMAGE_MAP[weather_main]

    description = (description or "").lower()
    for keyword, mapped_name in WEATHER_IMAGE_KEYWORDS.items():
        if keyword in description:
            return mapped_name
    return ["clear", "sunny"]


def get_weather_image(weather_main, description):
    candidates = resolve_weather_candidates(weather_main, description)
    for image_name in candidates:
        for extension in ("png", "jpg", "jpeg"):
            image_path = IMG_DIR / f"{image_name}.{extension}"
            if image_path.exists():
                return f"img/{image_path.name}"

    for extension in ("png", "jpg", "jpeg"):
        image_path = IMG_DIR / f"clear.{extension}"
        if image_path.exists():
            return f"img/{image_path.name}"
    return "img/main-blur.png"


def read_historical_data(filename):
    df = pd.read_csv(filename)
    df = df.dropna()
    df = df.drop_duplicates()
    return df


def prepare_data(data):
    data = data.copy()

    le_windgustdir = LabelEncoder()
    data["WindGustDir"] = le_windgustdir.fit_transform(data["WindGustDir"])

    le_raintomorrow = LabelEncoder()
    data["RainTomorrow"] = le_raintomorrow.fit_transform(data["RainTomorrow"])

    X = data[["MinTemp", "MaxTemp", "WindGustDir", "WindGustSpeed", "Humidity", "Pressure", "Temp"]]
    y = data["RainTomorrow"]

    return X, y, le_windgustdir, le_raintomorrow


def train_rain_model(X, y):
    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model


def prepare_regression_data(data, feature):
    X, y = [], []

    for i in range(len(data) - 1):
        X.append(data[feature].iloc[i])
        y.append(data[feature].iloc[i + 1])

    X = np.array(X).reshape(-1, 1)
    y = np.array(y)
    return X, y


def train_regression_model(X, y):
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model


def predict_future(model, current_value):
    predictions = [current_value]

    for _ in range(5):
        current_input = np.array([[predictions[-1]]])
        next_value = model.predict(current_input)
        predictions.append(next_value[0])

    return predictions[1:]


def wind_degrees_to_compass(wind_deg):
    compass_points = [
        ("N", 0, 11.25), ("NNE", 11.25, 33.75), ("NE", 33.75, 56.25),
        ("ENE", 56.25, 78.75), ("E", 78.75, 101.25), ("ESE", 101.25, 123.75),
        ("SE", 123.75, 146.25), ("SSE", 146.25, 168.75), ("S", 168.75, 191.25),
        ("SSW", 191.25, 213.75), ("SW", 213.75, 236.25), ("WSW", 236.25, 258.75),
        ("W", 258.75, 281.25), ("WNW", 281.25, 303.75), ("NW", 303.75, 326.25),
        ("NNW", 326.25, 360),
    ]
    return next((point for point, start, end in compass_points if start <= wind_deg < end), "N")


def build_forecast_context(city, current_weather):
    historical_data = read_historical_data(CSV_PATH)

    X, y, le_windgustdir, le_raintomorrow = prepare_data(historical_data)
    rain_model = train_rain_model(X, y)

    compass_direction = wind_degrees_to_compass(current_weather["wind_gust_dir"])
    compass_direction_encoded = 0
    if compass_direction in le_windgustdir.classes_:
        compass_direction_encoded = le_windgustdir.transform([compass_direction])[0]

    current_data = {
        "MinTemp": current_weather["temp_min"],
        "MaxTemp": current_weather["temp_max"],
        "WindGustDir": compass_direction_encoded,
        "WindGustSpeed": current_weather["wind_gust_speed"],
        "Humidity": current_weather["humidity"],
        "Pressure": current_weather["pressure"],
        "Temp": current_weather["current_temp"],
    }

    current_df = pd.DataFrame([current_data])
    rain_prediction = rain_model.predict(current_df)[0]
    rain_label = le_raintomorrow.inverse_transform([rain_prediction])[0]

    city_time_offset = current_weather.get("timezone_offset", 0)
    now = datetime.now(timezone.utc) + timedelta(seconds=city_time_offset)
    weather_image = get_weather_image(
        current_weather.get("weather_main"),
        current_weather.get("description"),
    )

    context = {
        "location": city,
        "current_temp": current_weather["current_temp"],
        "MinTemp": current_weather["temp_min"],
        "MaxTemp": current_weather["temp_max"],
        "feels_like": current_weather["feels_like"],
        "humidity": current_weather["humidity"],
        "clouds": current_weather["clouds"],
        "description": current_weather["description"],
        "weather_image": weather_image,
        "layout_image": weather_image,
        "city": current_weather["city"],
        "country": current_weather["country"],
        "time": now,
        "date": now.strftime("%B %d, %Y"),
        "wind": current_weather["wind_gust_speed"],
        "pressure": current_weather["pressure"],
        "visibility": current_weather["visibility"],
        "rain_prediction": rain_label,
    }

    hourly_forecast = []
    try:
        hourly_forecast = get_hourly_forecast(
            current_weather["lat"],
            current_weather["lon"],
            city_time_offset,
            count=5,
        )
    except Exception:
        hourly_forecast = []
    if len(hourly_forecast) == 5:
        for index, forecast_item in enumerate(hourly_forecast, start=1):
            context[f"time{index}"] = forecast_item["time"]
            context[f"temp{index}"] = f"{forecast_item['temp']:.1f}"
            context[f"hum{index}"] = f"{forecast_item['humidity']:.1f}"
    else:
        X_temp, y_temp = prepare_regression_data(historical_data, "Temp")
        temp_model = train_regression_model(X_temp, y_temp)
        future_temp = predict_future(temp_model, current_weather["current_temp"])

        X_hum, y_hum = prepare_regression_data(historical_data, "Humidity")
        hum_model = train_regression_model(X_hum, y_hum)
        future_humidity = predict_future(hum_model, current_weather["humidity"])
        future_times = [now + timedelta(hours=i) for i in range(1, 6)]

        for index, forecast_time in enumerate(future_times, start=1):
            context[f"time{index}"] = forecast_time.strftime("%H:00")
            context[f"temp{index}"] = f"{round(future_temp[index - 1], 1)}"
            context[f"hum{index}"] = f"{round(future_humidity[index - 1], 1)}"

    return context


def weather_view(request):
    default_context = {
        "layout_image": "img/main-blur.png",
        "weather_image": "img/main-blur.png",
    }

    if request.method == "POST":
        city = request.POST.get("city", "").strip()
        if not city:
            return render(
                request,
                "weather.html",
                {**default_context, "error": "Please enter a city."},
            )

        try:
            resolved_city = resolve_location_query(city)
            current_weather = get_current_weather(resolved_city)
            context = build_forecast_context(resolved_city, current_weather)
            context["location"] = city
            if resolved_city.casefold() != city.casefold():
                context["resolved_location"] = f"{current_weather['city']}, {current_weather['country']}"
        except Exception as exc:
            context = {
                **default_context,
                "location": city,
                "error": f"Could not fetch weather for {city}. {exc}",
            }

        return render(request, "weather.html", context)

    return render(request, "weather.html", default_context)
