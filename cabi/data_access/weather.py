import os
import requests


def get_forecast(ts):
    req = requests.get(
        "http://api.wunderground.com/api/%s/hourly10day/q/DC/Washington.json"
        % os.environ["WUNDERGROUND_KEY"]).json()

    forecast = None
    ts = ts.replace(minute=0, second=0, microsecond=0)

    for hour in req["hourly_forecast"]:
        if int(hour["FCTTIME"]["epoch"]) == int(ts.timestamp()):
            forecast = hour
            break

    if forecast is None:
        raise ValueError("Forecast not found for that hour.")

    return {
        "temp": forecast["temp"]["metric"],
        "precip": forecast["qpf"]["english"]
    }
