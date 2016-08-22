

def get_forecast(ts, engine):
    conn = engine.connect()

    forecasts = conn.execute("SELECT * FROM forecast")

    forecast = None
    ts = ts.replace(minute=0, second=0, microsecond=0)

    for hour in forecasts:
        if hour["ts"] == ts:
            forecast = hour
            break

    if forecast is None:
        raise ValueError("Forecast not found for that hour.")

    return forecast
