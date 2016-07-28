import pandas as pd


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
