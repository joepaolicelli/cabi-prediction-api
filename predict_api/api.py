from cabi.predict import predict
import falcon
import json
import os
import pandas as pd
from predict_api.auth import authorized
from sqlalchemy import create_engine


class StationStatus(object):
    @falcon.before(authorized)
    def on_post(self, req, resp):
        query = json.loads(req.stream.read().decode('utf-8'))

        engine = create_engine(
            "postgresql+psycopg2://" + os.environ["CABI_DB"])

        ts = pd.to_datetime(query["time"], infer_datetime_format=True)

        pred = predict(
            "temp/model", engine, int(query["station_id"]), ts)

        resp.body = json.dumps({
            "prediction": {
                "empty": pred["empty"],
                "full": pred["full"]}})

station_status = StationStatus()

app = falcon.API()
app.add_route('/', station_status)
