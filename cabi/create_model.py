from cabi.prepare_data.complete import complete
from cabi.techniques.ensemble import random_forest
import pandas as pd
from sklearn.externals import joblib


def create_model(
        file_prefix, db_engine, station_id, start, end, prep=complete,
        technique=random_forest):
    start = pd.to_datetime(start, infer_datetime_format=True)
    end = pd.to_datetime(end, infer_datetime_format=True)

    start = start.replace(
        minute=(start.minute - (start.minute % 5)), second=0, microsecond=0)
    end = end.replace(
        minute=(end.minute - (end.minute % 5)), second=0, microsecond=0)

    data = prep(db_engine, station_id, start, end)

    model_empty = technique(data["X"], data["yempty"])
    model_full = technique(data["X"], data["yfull"])

    joblib.dump(model_empty, file_prefix + "_empty", compress=True)
    joblib.dump(model_full, file_prefix + "_full", compress=True)
