# temporal_only
# The only features are the current time, day, and month.

from cabi.prepare_data.utils import bal, get_and_adjust_data
import numpy as np


def temporal_only(
        db_engine, station_id, start, end, sample_size=int(1.0e5),
        balance=None):
    """
    sample_size will be ignored if balance is not None.
    """

    data = get_and_adjust_data(
        db_engine, station_id, start, end, sample_size)

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

    for row in data.iteritems():
        features = [
            (1 if row[0].dayofweek == 0 else 0),
            (1 if row[0].dayofweek == 1 else 0),
            (1 if row[0].dayofweek == 2 else 0),
            (1 if row[0].dayofweek == 3 else 0),
            (1 if row[0].dayofweek == 4 else 0),
            (1 if row[0].dayofweek == 5 else 0),
            (1 if row[0].dayofweek == 6 else 0),
            float(((row[0].hour * 60) + row[0].minute)) / 1440.0,
            float(row[0].month) / 12.0
        ]

        X.append(features)
        yempty.append(1 if row[1] == "empty" else 0)
        yfull.append(1 if row[1] == "full" else 0)

    return {'X': X, 'yempty': yempty, 'yfull': yfull}
