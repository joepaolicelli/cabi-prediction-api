import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
import sys
import traceback

# These must be added for this to work.
host = ""
port = ""
db_name = ""
user = ""
password = ""

temps_filename = sys.argv[1]
precip_filename = sys.argv[2]

try:
    # Initialize database connection.
    engine = create_engine(
        "postgresql+psycopg2://"
        + user + ":" + password + "@"
        + host + ":" + port + "/" + db_name)

    temps = pd.read_csv(
        temps_filename, header=0, engine="c", infer_datetime_format=True,
        usecols=["YR--MODAHRMN", "TEMP"], parse_dates=["YR--MODAHRMN"])
    temps.rename(
        index=None, columns={"YR--MODAHRMN": "ts", "TEMP": "temp"},
        inplace=True)
    temps.drop(temps[temps.temp == "****"].index, inplace=True)

    precip = pd.read_csv(
        precip_filename, header=0, engine="c", infer_datetime_format=True,
        usecols=["valid", "precip_in"], parse_dates=["valid"])
    precip.rename(
        index=None, columns={"valid": "ts", "precip_in": "precip"},
        inplace=True)

    weather = pd.merge(
        temps, precip, on="ts"
    )

    # Delete anything previously in the table.
    if engine.has_table("weather"):
        engine.execute("DROP TABLE weather;")

    weather.to_sql(
        "weather", engine, index=True,
        dtype={
            "ts": sqlalchemy.types.DateTime,
            "temp": sqlalchemy.types.Integer,
            "precip": sqlalchemy.types.Float
        })

except Exception as e:
    print("Error when trying to connect to database:\n", e)
    print(traceback.print_exc())
