# Script to import historical station status data into a postgres database.
#
# Run this file directly, with all files to import listed as command line
# arguments. To clear the database table, make the first argument "clear".

import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
import sys

# Database information.
host = ""
port = ""
dbname = ""
user = ""
password = ""

# Initialize database connection.
engine = create_engine(
    "postgresql+psycopg2://"
    + user + ":" + password + "@"
    + host + ":" + port + "/" + dbname)

# Delete anything previously in the table.
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
