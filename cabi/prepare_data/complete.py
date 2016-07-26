# complete
# The primary (as of the current moment) feature selection method.

import numpy as np
import pandas as pd
from pandas.tseries.offsets import Hour


def complete(db_engine, selector, sample_size, balance=None):
    """
    sample_size is ignored if balance is set to None.
    """
    df_orig = pd.read_sql_query(
        "SELECT * FROM station_status "
        + "WHERE %s;" % selector, db_engine)

    if(balance == "Empty"):
        df_empty = df_orig[df_orig["bikes"] == 0]
        df_not_empty = df_orig[df_orig["bikes"] != 0]

        df = pd.concat([
            df_not_empty.sample(len(df_empty)),
            df_empty])
    elif(balance == "Full"):
        df_full = df_orig[df_orig["spaces"] == 0]
        df_not_full = df_orig[df_orig["spaces"] != 0]

        df = pd.concat([
            df_not_full.sample(len(df_full)),
            df_full])
    else:
        df = df_orig.sample(n=sample_size)

    # Ensure shuffling.
    df = df.iloc[np.random.permutation(len(df))]

    X = []
    yempty = []
    yfull = []

    weather = pd.read_sql_query(
        "SELECT * FROM weather", db_engine, index_col="ts")

    weather.index = weather.index.tz_localize(None)

    # Get rid of duplicates
    weather = weather.groupby(level=0).first()

    weather = weather.asfreq(Hour(), method="pad")

    for row in df.itertuples():

        hour = row.ts.replace(
            minute=0, second=0, microsecond=0, tzinfo=None)

        features = [
            (1 if row.ts.dayofweek == 0 else 0),
            (1 if row.ts.dayofweek == 1 else 0),
            (1 if row.ts.dayofweek == 2 else 0),
            (1 if row.ts.dayofweek == 3 else 0),
            (1 if row.ts.dayofweek == 4 else 0),
            (1 if row.ts.dayofweek == 5 else 0),
            (1 if row.ts.dayofweek == 6 else 0),
            float(((row.ts.hour * 60) + row.ts.minute)) / 1440.0,
            float(row.ts.month) / 12.0,
            float(weather.loc[hour].temp) / 200.0,
            float(weather.loc[hour].precip) / 15.0
        ]

        X.append(features)
        yempty.append(1 if row.bikes == 0 else 0)
        yfull.append(1 if row.spaces == 0 else 0)

    return {'X': X, 'yempty': yempty, 'yfull': yfull}
