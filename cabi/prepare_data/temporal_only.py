# temporal_only
# The only features are the current time, day, and month.

import numpy as np
import pandas as pd


def temporal_only(db_engine, selector, sample_size, balance=None):
    """
    sample_size is ignored if balance is set to True.
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

    for row in df.itertuples():
        features = [
            (1 if row.ts.dayofweek == 0 else 0),
            (1 if row.ts.dayofweek == 1 else 0),
            (1 if row.ts.dayofweek == 2 else 0),
            (1 if row.ts.dayofweek == 3 else 0),
            (1 if row.ts.dayofweek == 4 else 0),
            (1 if row.ts.dayofweek == 5 else 0),
            (1 if row.ts.dayofweek == 6 else 0),
            float(((row.ts.hour * 60) + row.ts.minute)) / 1440.0,
            float(row.ts.month) / 12.0
        ]

        X.append(features)
        yempty.append(1 if row.bikes == 0 else 0)
        yfull.append(1 if row.spaces == 0 else 0)

    return {'X': X, 'yempty': yempty, 'yfull': yfull}
