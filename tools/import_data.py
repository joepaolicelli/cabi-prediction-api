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
if sys.argv[1] == "clear" and engine.has_table("outages"):
    engine.execute("DROP TABLE outages;")
    print("Data cleared.")

for filename in sys.argv:
    if filename != "import_data.py" and filename != "clear":
        csv = pd.read_csv(
            filename, skiprows=1, header=0, engine="c",
            infer_datetime_format=True,
            usecols=["Terminal Number", "Status", "Start", "End"],
            parse_dates=["Start", "End"])
        csv.rename(
            index=None, columns={
                "Terminal Number": "station_id",
                "Status": "status",
                "Start": "start",
                "End": "end"
            }, inplace=True)

        csv.to_sql(
            "outages", engine, if_exists="append",
            dtype={
                "station_id": sqlalchemy.types.Integer,
                "status": sqlalchemy.types.String,
                "start": sqlalchemy.types.DateTime,
                "end": sqlalchemy.types.DateTime
            })
        print(filename, "imported.")
