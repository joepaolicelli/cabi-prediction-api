import datetime
import os
import pandas as pd
import pytz
import requests
from sqlalchemy import create_engine, sql
from sqlalchemy import Column, MetaData, Table
from sqlalchemy.types import DateTime, Float, String
import traceback

try:
    req = requests.get(
        "http://api.wunderground.com/api/%s/hourly10day/q/DC/Washington.json"
        % os.environ["WUNDERGROUND_KEY"]).json()

    # Establish database connection.
    engine = create_engine("postgresql+psycopg2://" + os.environ["CABI_DB"])
    conn = engine.connect()

    if engine.has_table("forecast"):
        conn.execute("DROP TABLE forecast;")

    meta = MetaData()
    forecast_table = Table(
        "forecast", meta,
        Column("ts", DateTime),
        Column("temp", Float),
        Column("precip", Float),
        Column("condition", String))
    meta.create_all(engine)

    query = sql.text(
        "INSERT INTO forecast (ts, temp, precip, condition) "
        "VALUES (:ts, :temp, :precip, :condition)")

    for hour in req["hourly_forecast"]:
        ts = pd.to_datetime(hour["FCTTIME"]["pretty"])
        # Convert from UTC to Eastern time.
        ts = ts.replace(tzinfo=pytz.utc).astimezone(
            pytz.timezone("US/Eastern")).replace(tzinfo=None)

        conn.execute(
            query,
            ts=ts,
            temp=float(hour["temp"]["metric"]),
            precip=float(hour["qpf"]["english"]),
            condition=hour["condition"])

except Exception as err:
    print(datetime.datetime.now().strftime('%c'))
    print(traceback.format_exc())
    raise
