import os
import requests
from sqlalchemy import create_engine, sql
from sqlalchemy import Column, MetaData, Table
from sqlalchemy.types import Float, Integer, String
import traceback
import xmltodict

try:
    # Establish database connection.
    engine = create_engine("postgresql+psycopg2://" + os.environ["CABI_DB"])
    conn = engine.connect()

    if engine.has_table("station_info"):
        conn.execute("DROP TABLE station_info;")

    meta = MetaData()
    station_table = Table(
        "station_info", meta,
        Column("station_id", Integer),
        Column("name", String),
        Column("lat", Float),
        Column("long", Float))
    meta.create_all(engine)

    data = xmltodict.parse(requests.get(
        "https://feeds.capitalbikeshare.com/stations/stations.xml").text)

    query = sql.text(
        "INSERT INTO station_info (station_id, name, lat, long) "
        "VALUES (:station_id, :name, :lat, :long)")

    for st in data["stations"]["station"]:
        conn.execute(
            query, station_id=int(st["terminalName"]), name=st["name"],
            lat=float(st["lat"]), long=float(st["long"]))

except Exception as err:
    print(traceback.format_exc())
    raise
