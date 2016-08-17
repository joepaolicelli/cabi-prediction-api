# Script to import historical weather data from ISD lite files into a
# postgres database. ISD lite data can be found here:
# http://www1.ncdc.noaa.gov/pub/data/noaa/isd-lite/
#
# Run this file directly, with all files to import listed as command line
# arguments. To clear the database table, make the first argument "clear".
#
# Database information must be entered below or in the env var CABI_DB.
#
# Also, if "import_weather_data.py" is in the name of the file you're trying
# to import, it's not going to work. This is to prevent this code from trying
# to insert itself into the database.

import os
import pandas as pd
import pytz
import sqlalchemy
from sqlalchemy import create_engine
import sys

# Database information, if not contained in the env var CABI_DB.
host = ""
port = ""
db_name = ""
user = ""
password = ""

db_str = os.environ["CABI_DB"]
if db_str is None:
    db_str = user + ":" + password + "@" + host + ":" + port + "/" + db_name

# Initialize database connection.
engine = create_engine("postgresql+psycopg2://" + db_str)

if sys.argv[1] == "clear" and engine.has_table("weather_isd"):
    engine.execute("DROP TABLE weather_isd;")
    print("\nData cleared.")

for filename in sys.argv:
    if "import_weather_data.py" not in filename and filename != "clear":
        weather = pd.read_csv(
            filename, header=None, engine="c", infer_datetime_format=True,
            delim_whitespace=True, na_values="-9999",
            usecols=[0, 1, 2, 3, 4, 10],
            parse_dates={"ts": [0, 1, 2, 3]})
        weather.rename(
            index=None, columns={4: "temp", 10: "precip"},
            inplace=True)

        # Convert time from UTC to US/Eastern.
        def correct_tz(x):
            x = x.replace(tzinfo=pytz.utc).astimezone(
                pytz.timezone("US/Eastern")).replace(tzinfo=None)
            return x
        weather["ts"] = weather["ts"].apply(correct_tz)

        # Change values of -1 in precip (meaning "trace percipitation") to
        # 0.1.
        weather["precip"] = weather["precip"].apply(
            lambda x: 0.1 if x == -1 else x)

        # Remove x10 multiplier from temperature and precipitation values.
        weather["temp"] = weather["temp"].apply(lambda x: x / 10)
        weather["precip"] = weather["precip"].apply(lambda x: x / 10)

        weather.to_sql(
            "weather_isd", engine, if_exists="append",
            dtype={
                "ts": sqlalchemy.types.DateTime,
                "temp": sqlalchemy.types.Float,
                "precip": sqlalchemy.types.Float
            })
        print(filename, "imported.")
