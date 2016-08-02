"""
Records the current weather conditions and upcoming hourly forecasts.

A postgres database is required. The environmental variable 'CABI_DB' should
be set to a connection string of the format
'username:password@host:port/db_name'.
"""

import os
import pandas as pd
import requests
from sqlalchemy import create_engine, sql
from sqlalchemy import Column, MetaData, Table
from sqlalchemy.types import DateTime, Float

# Establish database connection.
engine = create_engine("postgresql+psycopg2://" + os.environ["CABI_DB"])
conn = engine.connect()

if not engine.has_table("weather"):
    meta = MetaData()
    weather_table = Table(
        "weather", meta,
        Column("ts", DateTime),
        Column("temp", Float),
        Column("precip", Float))
    meta.create_all(engine)

req = requests.get(
    "http://api.wunderground.com/api/%s/conditions/q/DC/Washington.json"
    % os.environ["WUNDERGROUND_KEY"]).json()

ts = pd.to_datetime(
    req["current_observation"]["local_time_rfc822"],
    infer_datetime_format=True)

query = sql.text(
    "INSERT INTO weather (ts, temp, precip) "
    "VALUES (:ts, :temp, :precip)")

conn.execute(
    query, ts=ts,
    temp=float(req["current_observation"]["temp_c"]),
    precip=float(req["current_observation"]["precip_1hr_metric"]))
