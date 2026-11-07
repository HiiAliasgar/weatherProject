import os
from unittest.mock import patch

from django.test import SimpleTestCase

from .views import get_api_key, resolve_weather_candidates, wind_degrees_to_compass


class WeatherConfigurationTests(SimpleTestCase):
    def test_api_key_is_read_from_environment(self):
        with patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test-key"}):
            self.assertEqual(get_api_key(), "test-key")

    def test_missing_api_key_fails_clearly(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesMessage(RuntimeError, "OPENWEATHER_API_KEY"):
                get_api_key()


class WeatherHelperTests(SimpleTestCase):
    def test_wind_degrees_wrap_to_compass_direction(self):
        self.assertEqual(wind_degrees_to_compass(0), "N")
        self.assertEqual(wind_degrees_to_compass(90), "E")
        self.assertEqual(wind_degrees_to_compass(180), "S")
        self.assertEqual(wind_degrees_to_compass(270), "W")

    def test_weather_main_maps_to_image_candidates(self):
        self.assertEqual(resolve_weather_candidates("Rain", "light rain"), ["rain", "shower"])
