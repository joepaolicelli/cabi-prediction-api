import os
import sys

INTERP = "/opt/sites/CapitalBikeshareML-API/current/ENV/bin/python"
# INTERP is present twice so that the new Python interpreter knows the actual
# executable path
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

from api_utils.auth import authorized       # noqa: E402 (Imports not at top)
from api_utils.logger_setup import logger_setup     # noqa: E402
from cabi.create_model import create_model          # noqa: E402
from cabi.predict import predict                    # noqa: E402
import falcon                                       # noqa: E402
import json                                         # noqa: E402
import logging                                      # noqa: E402
import pandas as pd                                 # noqa: E402
from sqlalchemy import create_engine                # noqa: E402

logger_setup()
logger = logging.getLogger("cabi_api")


class StationStatus(object):
    @falcon.before(authorized)
    def on_post(self, req, resp):
        logger.info("POST request received.")
        try:
            engine = create_engine(
                "postgresql+psycopg2://" + os.environ["CABI_DB"])

            if not os.path.isdir("model"):
                os.makedirs("model")
                create_model(
                    "model/model", engine, 31230, "01/02/2015", "12/30/2015")

            query = json.loads(req.stream.read().decode('utf-8'))

            ts = pd.to_datetime(query["time"], infer_datetime_format=True)

            pred = predict(
                "model/model", engine, int(query["station_id"]), ts)

            resp.body = json.dumps({
                "prediction": {
                    "empty": pred["empty"],
                    "full": pred["full"]}})

        except Exception as err:
            logger.error(err)

station_status = StationStatus()

app = application = falcon.API()
app.add_route('/', station_status)
