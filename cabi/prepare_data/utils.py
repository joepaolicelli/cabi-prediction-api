import datetime
import numpy as np
import pandas as pd


def get_and_adjust_data(db_engine, station_id, start, end, sample_size):
    # Add data in the outage format.
    outages = pd.read_sql_query(
        "SELECT outage_type, outage_start, outage_end FROM outage "
        + "WHERE station_id = %(station_id)s AND "
        + "outage_start >= %(start)s AND outage_end <= %(end)s;",
        db_engine, params={
            "station_id": station_id, "start": start, "end": end})

    # "5T" is 5 minutes.
    dti = pd.date_range(0, -1, freq="5T")
    data = pd.Series("", index=dti)

    # Merge each outage into dataframe.
    for outage in outages.itertuples():
        ostart = pd.to_datetime(outage[2], infer_datetime_format=True)
        + datetime.timedelta(seconds=150)
        ostart = ostart.replace(
            minute=(ostart.minute - (ostart.minute % 5)), second=0)
        oend = pd.to_datetime(outage[3], infer_datetime_format=True)
        + datetime.timedelta(seconds=150)
        oend = oend.replace(
            minute=(oend.minute - (oend.minute % 5)), second=0)

        index = pd.date_range(ostart, oend, freq="5T")

        data = pd.concat([data, pd.Series(outage[1], index=index)])

    # Add data in the bike count format.
    bike_counts = pd.read_sql_query(
        "SELECT ts, bikes, spaces FROM bike_count "
        + "WHERE station_id = %(station_id)s AND "
        + "ts >= %(start)s AND ts <= %(end)s;",
        db_engine, params={
            "station_id": station_id, "start": start, "end": end})
    for bike_count in bike_counts.itertuples():
        ts = pd.to_datetime(bike_count[1], infer_datetime_format=True)
        + datetime.timedelta(seconds=150)
        ts = ts.replace(minute=(ts.minute - (ts.minute % 5)), second=0)

        status = np.nan
        if bike_count[2] == 0:
            status = "empty"
        elif bike_count[3] == 0:
            status = "full"

        index = pd.date_range(ts, ts, freq="5T")

        data = pd.concat([data, pd.Series(status, index=index)])

    data.sort_index(inplace=True)

    # Remove any duplicates.
    data = data.groupby(data.index).first()
    # Add NaN for those times when the station is not full or empty.
    data = data.reindex(pd.date_range(start, end, freq="5T"))

    return data


def bal(s, balance):
    """
    s: The series to balance.
    balance: The status to balance on. "empty" or "full"
    """
    if(balance == "empty"):
        df_empty = s[s == "empty"]
        df_not_empty = s[s != "empty"]

        return pd.concat([
            df_not_empty.sample(len(df_empty)),
            df_empty])
    elif(balance == "full"):
        df_full = s[s == "full"]
        df_not_full = s[s != "full"]

        return pd.concat([
            df_not_full.sample(len(df_full)),
            df_full])
