# complete
# The primary (as of the current moment) feature selection method.

from cabi.prepare_data.utils import bal, get_and_adjust_data
import datetime
import numpy as np
import pandas as pd
from pandas.tseries.offsets import Hour


def complete(
        db_engine, selector, start, end, sample_size=int(1.0e5), balance=None):
    """
    sample_size will be ignored if balance is not None.
    """
    data = get_and_adjust_data(
        db_engine, selector, start, end, sample_size)

    # Balance or set to sample_size
    if balance is None:
        data = data.sample(n=sample_size)
    else:
        data = bal(data, balance)

    # Ensure shuffling.
    data = data.iloc[np.random.permutation(len(data))]

    X = []
    yempty = []
    yfull = []

    weather = pd.read_sql_query(
        "SELECT * FROM weather", db_engine, index_col="ts")

    weather.index = weather.index.tz_localize(None)

    # Get rid of duplicates
    weather = weather.groupby(level=0).first()

    weather = weather.asfreq(Hour(), method="pad")

    for row in data.iteritems():

        hour = row[0].replace(
            minute=0, second=0, microsecond=0, tzinfo=None)

        temp_hour = hour
        temp = float(weather.loc[temp_hour].temp)

        while pd.isnull(temp):
            temp_hour = temp_hour - datetime.timedelta(hours=1)
            temp = float(weather.loc[temp_hour].temp)

        features = [
            (1 if row[0].dayofweek == 0 else 0),
            (1 if row[0].dayofweek == 1 else 0),
            (1 if row[0].dayofweek == 2 else 0),
            (1 if row[0].dayofweek == 3 else 0),
            (1 if row[0].dayofweek == 4 else 0),
            (1 if row[0].dayofweek == 5 else 0),
            (1 if row[0].dayofweek == 6 else 0),
            float(((row[0].hour * 60) + row[0].minute)) / 1440.0,
            float(row[0].month) / 12.0,
            temp / 500.0,
            float(weather.loc[hour].precip) / 15.0
        ]

        X.append(features)
        yempty.append(1 if row[1] == "empty" else 0)
        yfull.append(1 if row[1] == "full" else 0)

    return {'X': X, 'yempty': yempty, 'yfull': yfull}
