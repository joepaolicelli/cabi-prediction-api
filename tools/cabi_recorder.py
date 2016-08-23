"""
Records the status of all capital bikeshare stations.

A postgres database is required. The environmental variable 'CABI_DB' should
be set to a connection string of the format
'username:password@host:port/db_name'.

Timestamps are converted from UTC to US/Eastern, which they are stored as.
"""

import os
import pandas as pd
import pytz
import requests
from sqlalchemy import create_engine, sql
from sqlalchemy import Column, MetaData, Table
from sqlalchemy.types import DateTime, Integer
import traceback
import xmltodict

try:
    # Establish database connection.
    engine = create_engine("postgresql+psycopg2://" + os.environ["CABI_DB"])
    conn = engine.connect()

    if not engine.has_table("bike_count"):
        meta = MetaData()
        counts_table = Table(
            "bike_count", meta,
            Column("station_id", Integer),
            Column("ts", DateTime),
            Column("bikes", Integer),
            Column("spaces", Integer))
        meta.create_all(engine)

    data = xmltodict.parse(requests.get(
        "https://feeds.capitalbikeshare.com/stations/stations.xml").text)

    for st in data["stations"]["station"]:
        ts = pd.to_datetime(
            st["lastCommWithServer"], unit="ms", infer_datetime_format=True)
        # Convert from UTC to Eastern time.
        ts = ts.replace(tzinfo=pytz.utc).astimezone(
            pytz.timezone("US/Eastern"))

        query = sql.text(
            "INSERT INTO bike_count (station_id, ts, bikes, spaces) "
            "VALUES (:station_id, :ts, :bikes, :spaces)")

        conn.execute(
            query, station_id=st["terminalName"], ts=ts,
            bikes=st["nbBikes"], spaces=st["nbEmptyDocks"])

except Exception as err:
    print(traceback.format_exc())
    raise
