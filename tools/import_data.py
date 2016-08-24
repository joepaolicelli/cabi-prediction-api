# Script to import historical station outage data into a postgres database,
# in the format available for export from the excellent CaBi Tracker:
# http://cabitracker.com/outage_history.php
#
# Dates from this source are already in local time.
#
# Run this file directly, with all files to import listed as command line
# arguments. To clear the database table, make the first argument "clear".
#
# Database information must be entered below or in the env var CABI_DB.
#
# Also, if "import_data.py" is in the name of the file you're trying to
# import, it's not going to work. This is to prevent this code from trying
# to insert itself into the database.

import os
import pandas as pd
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

if sys.argv[1] == "clear" and engine.has_table("outage"):
    engine.execute("DROP TABLE outage;")
    print("Data cleared.")

for filename in sys.argv:
    if "import_data.py" not in filename and filename != "clear":
        csv = pd.read_csv(
            filename, skiprows=1, header=0, engine="c",
            infer_datetime_format=True,
            usecols=["Terminal Number", "Status", "Start", "End"],
            parse_dates=["Start", "End"])
        csv.rename(
            index=None, columns={
                "Terminal Number": "station_id",
                "Status": "outage_type",
                "Start": "outage_start",
                "End": "outage_end"
            }, inplace=True)

        csv.to_sql(
            "outage", engine, if_exists="append",
            dtype={
                "station_id": sqlalchemy.types.Integer,
                "outage_type": sqlalchemy.types.String,
                "outage_start": sqlalchemy.types.DateTime,
                "outage_end": sqlalchemy.types.DateTime
            })
        print(filename, "imported.")
