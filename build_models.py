from cabi.create_model import create_model
import datetime
from dateutil.relativedelta import relativedelta
import os
from sqlalchemy import create_engine, sql

START_DATE = datetime.date.today() - relativedelta(months=26)
END_DATE = datetime.date.today()

# Establish database connection.
engine = create_engine("postgresql+psycopg2://" + os.environ["CABI_DB"])
conn = engine.connect()

# Get list of all station ids.
query = sql.text(
    "SELECT DISTINCT station_id FROM outage "
    "UNION "
    "SELECT DISTINCT station_id FROM bike_count;")
id_list = conn.execute(query)

# Build and save a model for each station.
for row in id_list:
    station_id = row[0]
    model_path = "models/station_" + str(station_id)

    # Create folder for model if needed.
    if not os.path.isdir(model_path):
        os.makedirs(model_path)
    print("Station", str(station_id))
    create_model(
        model_path + "/model", engine, station_id, START_DATE, END_DATE)
