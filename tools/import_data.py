import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
import sys
import traceback

# These must be added for this to work.
host = ""
port = ""
dbname = ""
user = ""
password = ""

filename = sys.argv[1]

try:
    # Initialize database connection.
    engine = create_engine(
        "postgresql+psycopg2://"
        + user + ":" + password + "@"
        + host + ":" + port + "/" + dbname)

    counter = 0
    chunksize = 100000
    csv = pd.read_csv(
        filename, chunksize=chunksize, header=None, engine="c",
        names=["station_id", "bikes", "spaces", "ts"])

    # Delete anything previously in the table.
    if engine.has_table("station_status"):
        engine.execute("DROP TABLE station_status;")

    for chunk in csv:
        invalidstationmask = chunk.apply(
            lambda row: (row["spaces"] == 0 and row["bikes"] == 0),
            axis=1
        )
        cleanedchunk = chunk[~invalidstationmask]

        cleanedchunk.to_sql(
            "station_status", engine, if_exists="append",
            dtype={
                "station_id": sqlalchemy.types.Integer,
                "bikes": sqlalchemy.types.Integer,
                "space": sqlalchemy.types.Integer,
                "ts": sqlalchemy.types.DateTime
            })
        print("Imported " + str(counter) + " to "
              + str(counter+(chunksize-1)) + ".")
        counter += chunksize
        if counter >= chunksize * 400:
            break

except Exception as e:
    print("Error when trying to connect to database:\n", e)
    print(traceback.print_exc())
