import datetime
import numpy as np
import pandas as pd


def get_and_adjust_data(db_engine, station_id, start, end, sample_size):
    data_list = []
    # "5T" is 5 minutes.
    dti = pd.date_range(0, -1, freq="5T")
    data = pd.Series(None, index=dti)
    # Add data in the bike count format.
    bike_counts = pd.read_sql_query(
        "SELECT ts, bikes, spaces FROM bike_count "
        + "WHERE station_id = %(station_id)s AND "
        + "ts >= %(start)s AND ts <= %(end)s;",
        db_engine, params={
            "station_id": station_id, "start": start, "end": end})
    # bike_count[0] is the index, [1..3] are the columns in the order
    # selected in the above query
    for bike_count in bike_counts.itertuples():
        # Do not insert counts with no bikes or spaces (inactive stations).
        if not (bike_count[2] == 0 and bike_count[3] == 0):
            ts = pd.to_datetime(bike_count[1], infer_datetime_format=True)
            # Round the timestamp to the nearest five minute mark.
            ts += datetime.timedelta(seconds=150)
            ts = ts.replace(minute=(ts.minute - (ts.minute % 5)), second=0)

            # A status of np.nan means the station is neither full nor empty.
            status = np.nan
            if bike_count[2] == 0:
                status = "empty"
            elif bike_count[3] == 0:
                status = "full"

            # Create index with only one entry, ts.
            index = pd.date_range(ts, ts, freq="5T")

            data_list.append(pd.Series(status, index=index))

    if len(data_list) > 0:
        data = pd.concat(data_list)

    data_list = []
    # Add data in the outage format.
    outages = pd.read_sql_query(
        "SELECT outage_type, outage_start, outage_end FROM outage "
        + "WHERE station_id = %(station_id)s AND "
        + "outage_start >= %(start)s AND outage_end <= %(end)s;",
        db_engine, params={
            "station_id": station_id, "start": start, "end": end})

    # Merge each outage into dataframe.
    for outage in outages.itertuples():
        ostart = pd.to_datetime(outage[2], infer_datetime_format=True)
        ostart += datetime.timedelta(seconds=150)
        ostart = ostart.replace(
            minute=(ostart.minute - (ostart.minute % 5)), second=0)
        oend = pd.to_datetime(outage[3], infer_datetime_format=True)
        oend += datetime.timedelta(seconds=150)
        oend = oend.replace(
            minute=(oend.minute - (oend.minute % 5)), second=0)

        index = pd.date_range(ostart, oend, freq="5T")

        data_list.append(pd.Series(outage[1], index=index))

    outage_data = pd.concat(data_list)

    outage_data = outage_data.groupby(outage_data.index).first()
    # Remove any timestamps from outage_data that are in the bike_count data.
    unique = outage_data.index.difference(data.index)

    outage_data = outage_data.reindex(unique)

    # Merge the two series together.
    data = pd.concat([data, outage_data])

    # Remove any remaining stray duplicates.
    data = data.groupby(data.index).first()
    # Add NaN for those times when the station is not full or empty.
    data = data.reindex(pd.date_range(start, end, freq="5T"))
    data.sort_index(inplace=True)

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
