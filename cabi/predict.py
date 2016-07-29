from cabi.data_access.weather import get_forecast
from sklearn.externals import joblib


def predict(file_prefix, db_engine, station_id, ts):
    model_empty = joblib.load(file_prefix + "_empty")
    model_full = joblib.load(file_prefix + "_full")

    forecast = get_forecast(ts)

    features = [
        (1 if ts.dayofweek == 0 else 0),
        (1 if ts.dayofweek == 1 else 0),
        (1 if ts.dayofweek == 2 else 0),
        (1 if ts.dayofweek == 3 else 0),
        (1 if ts.dayofweek == 4 else 0),
        (1 if ts.dayofweek == 5 else 0),
        (1 if ts.dayofweek == 6 else 0),
        float(((ts.hour * 60) + ts.minute)) / 1440.0,
        float(ts.month) / 12.0,
        float(int(forecast["temp"]) * 10) / 500.0,
        float(forecast["precip"]) / 15.0
    ]

    prob_empty = model_empty.predict_proba([features])[0][1]
    prob_full = model_full.predict_proba([features])[0][1]

    return {"empty": prob_empty, "full": prob_full}
