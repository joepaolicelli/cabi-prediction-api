import datetime
import pandas as pd


def get_and_adjust_data(db_engine, selector, start, end, sample_size):
    df_orig = pd.read_sql_query(
        "SELECT * FROM outages "
        + "WHERE %s;" % selector, db_engine)

    # "5T" is 5 minutes.
    dti = pd.date_range(0, -1, freq="5T")
    data = pd.Series("", index=dti)

    # Merge each outage into dataframe.
    for outage in df_orig.itertuples():
        ostart = pd.to_datetime(outage[4], infer_datetime_format=True)
        + datetime.timedelta(seconds=150)
        ostart = ostart.replace(
            minute=(ostart.minute - (ostart.minute % 5)), second=0)
        oend = pd.to_datetime(outage[5], infer_datetime_format=True)
        + datetime.timedelta(seconds=150)
        oend = oend.replace(
            minute=(oend.minute - (oend.minute % 5)), second=0)

        index = pd.date_range(ostart, oend, freq="5T")

        data = pd.concat([data, pd.Series(outage[3], index=index)])

    data.sort_index(inplace=True)
    data = data.groupby(data.index).first()
    data = data.reindex(pd.date_range(start, end, freq="5T"))

    return data


def bal(df, balance):
    """
    df: The dataframe (or series) to balance.
    balance: The status to balance on. "Empty" or "Full"
    """
    if(balance == "empty"):
        df_empty = df[df == "empty"]
        df_not_empty = df[df != "empty"]

        return pd.concat([
            df_not_empty.sample(len(df_empty)),
            df_empty])
    elif(balance == "full"):
        df_full = df[df == "full"]
        df_not_full = df[df != "full"]

        return pd.concat([
            df_not_full.sample(len(df_full)),
            df_full])
