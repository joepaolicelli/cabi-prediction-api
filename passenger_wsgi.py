import os
import sys

is_dev = (os.environ["CABI_ENV"] == "DEV")
INTERP = "/opt/sites/CapitalBikeshareML-API/current/ENV/bin/python"
# This allows the API to run properly in a virtualenv.
# INTERP is present twice so that the new Python interpreter knows the actual
# executable path
if (not is_dev) and sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

from api_utils.auth import authorized       # noqa: E402 (Imports not at top)
from api_utils.logger_setup import logger_setup         # noqa: E402
from cabi.closest_stations import closest_stations      # noqa: E042
from cabi.create_model import create_model              # noqa: E402
from cabi.data_access.googlemaps import get_loc_info    # noqa: E402
from cabi.data_access.weather import get_forecast       # noqa: E042
from cabi.predict import predict                        # noqa: E402
import falcon                                           # noqa: E402
from falcon_cors import CORS                            # noqa: E402
import json                                             # noqa: E402
import logging                                          # noqa: E402
import pandas as pd                                     # noqa: E402
from sqlalchemy import create_engine                    # noqa: E402

logger_setup()
logger = logging.getLogger("cabi_api")


class StationStatus(object):
    def on_post(self, req, resp):
        """
        Expects a json body of the following structure:

        {
          "datetime": string (date and time),
          "location": string[,
          "station_count": integer]
        }

        The datetime string is passed to panda's to_datetime method, so any
        reasonable format (including unix timestamps) should be fine.

        The location string is passed to the Google Maps API to get
        coordinates, so specific addresses or general neighboorhoods (anything
        that works with Google Maps, actually) will both work.

        An optional station_count parameter can be passed to specify the
        number of closest stations that should be returned. The default is
        five.
        """

        logger.info("POST request.")
        try:
            engine = create_engine(
                "postgresql+psycopg2://" + os.environ["CABI_DB"])

            if not os.path.isdir("models"):
                logger.error("models directory not found.")
                raise falcon.HTTPServiceUnavailable

            query = json.loads(req.stream.read().decode('utf-8'))

            ts = pd.to_datetime(query["datetime"], infer_datetime_format=True)

            loc = get_loc_info(query["location"])
            forecast = get_forecast(ts, engine)

            results = {
                "address": loc["formatted_address"],
                "date": ts.strftime("%A %B %d, %Y"),
                "forecast": {
                    "condition": forecast["condition"]
                },
                "stations": [],
                "status": "success",
                "time": ts.strftime("%I:%M %p")
            }

            coord = (
                float(loc["geometry"]["location"]["lat"]),
                float(loc["geometry"]["location"]["lng"]))

            count = query["station_count"] if (
                "station_count" in query) else 5

            stations = closest_stations(coord, engine, count=int(count))

            for station in stations:
                try:
                    pred = predict(
                        "models/station_" + str(station["id"]) + "/model",
                        engine,
                        int(station["id"]),
                        ts, forecast)

                    results["stations"].append({
                        "name": station["name"],
                        "distance": station["distance"],
                        "prediction": pred
                    })

                except FileNotFoundError as err:
                    logger.error(err)

            resp.body = json.dumps(results)

        except Exception as err:
            logger.error(err)
            resp.body = json.dumps({"status": "error"})

station_status = StationStatus()

cors = CORS(
    allow_all_origins=True, allow_all_methods=True, allow_all_headers=True)

app = application = falcon.API(middleware=[cors.middleware])
app.add_route('/', station_status)
