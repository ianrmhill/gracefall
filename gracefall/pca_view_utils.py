from sklearn.decomposition import PCA
import numpy as np
import pandas as pd

def seperate_ts(ms):
    """
    input:
        ms (DataFrame): time series to seperate
    output:
        t_series (dict): a dict of with seperated time series. where t_series[k][i] referes to the ith time series
    """
    t_series = {'param': [],
                "device #": [],
                "chip #": [],
                "lot #": [],
                "sample #":[],
                "aggtype":[]}
    
    # treat t_id key to individual time series; filter by them get 1 time series
    for t_id in ms["sample #"].unique():
        df_ori = ms[t_id == ms["sample #"]]
        for aggtype in df_ori.aggtype.unique():
            df = df_ori[df_ori.aggtype == aggtype]
            assert df.time.unique().shape[0] == len(df)

            t_series['param'].append(df['param'].iloc[0])
            t_series["device #"].append(df["device #"].iloc[0])
            t_series["chip #"].append(df["chip #"].iloc[0])
            t_series["lot #"].append(df["lot #"].iloc[0])
            t_series["sample #"].append(df["sample #"].iloc[0])
            t_series["aggtype"].append(df["aggtype"].iloc[0])

            if t_series.get("measured") is None:
                t_series['measured'] = df['measured'].to_numpy()[None]
            else:
                t_series["measured"] = np.concatenate([t_series["measured"], df["measured"].to_numpy()[None]])            
    
    return t_series


def create_table(ms):
    df = None

    for prm in ms['param'].unique():
        t_series = seperate_ts(ms.loc[ms['param'] == prm])
        t_np = {}
        t_np = t_series["measured"] # get the time series; shape = (n_time_series, n_points_per_series)
        t_np = np.concatenate([t_np, np.diff(t_np)], axis=-1) # add difference as features

        # create 2d position for each time series
        pca = PCA(2)
        pca.fit(t_np)
        t_xy = pca.transform(t_np)

        # create structured table for altair
        del t_series["measured"]
        t_series["x"] = []
        t_series["y"] = []

        # for pos, kc in zip(t_xy):#, t_cs):
        for pos in t_xy:
            x, y = pos
            t_series["x"].append(x)
            t_series["y"].append(y)
        if df is None:
            df = pd.DataFrame(t_series)
        else:
            df = pd.concat((df, pd.DataFrame(t_series)), axis=0)

    return df
