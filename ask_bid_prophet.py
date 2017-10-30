import pandas as pd
import numpy as np
from fbprophet import Prophet
from numpy.random import *
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import seaborn as sns
import pandas as pd
import math
import pickle
import time
import datetime
import json
import itertools
import collections
import os

def create_spread_df():
    print("create_spread_df")
    dt_now = datetime.datetime.now()
    last_update_min = 0
    # フォルダ作成
    input_folder_name = "./simulation_data/"
    out_df_filename = "df_bid-ask_all.dump"
    if os.path.isfile(out_df_filename):
        with open(out_df_filename,"rb") as f:
            df_spread = pickle.load(f)
    else:
        # データ読み取り
        data_json_all = {}
        for day in [14,15,16,17,19,20,21,22,23,24,25,26,27,28,29]:
            with open(input_folder_name+"2017-10-"+str(day)+"ticker_log.json") as data_file:
                data_json = json.load(data_file)

            data_json_all = dict(data_json_all, **data_json)

        ticker_all = collections.OrderedDict(sorted(data_json_all.items()))

        spread_a_list = []
        spread_b_list = []

        for key, ticker in ticker_all.items():
            spread_a = ticker[ex_1]["bid"] - ticker[ex_2]["ask"]
            spread_b = ticker[ex_2]["bid"] - ticker[ex_1]["ask"]
            spread_a_list.append(spread_a)
            spread_b_list.append(spread_b)

        df_spread=pd.DataFrame(index=list(ticker_all.keys()))

        df_spread[ex_1+"_bid-"+ex_2+"_ask"] = pd.DataFrame(spread_a_list, index=list(ticker_all.keys()))
        df_spread[ex_2+"_bid-"+ex_1+"_ask"] = pd.DataFrame(spread_b_list, index=list(ticker_all.keys()))

        df_spread['date']=df_spread.index
        df_spread['date']=pd.to_datetime(df_spread['date'], format='%Y-%m-%d-%H:%M:%S')
        with open(out_df_filename,"wb") as f:
            pickle.dump(df_spread, f)
        print("finish create_spread_df")
    return df_spread

def get_prophetmodel(column_name):
    print("get_prophetmodel")
    df=pd.DataFrame(index=df_spread.index)
    df["y"]=df_spread[[column_name]]
    df["ds"]=df_spread.index
    # 10000以上は異常値
    df=df[(df['y']>-10000) & (df['y']<1000)]

    m = Prophet()
    m.fit(df)
    with open("prophetmodel.dump","wb") as f:
        pickle.dump(m, f)
    print("finish get_prophetmodel")
    return m

ex_1 = "coincheck"
ex_2 = "quoine"

df_spread = create_spread_df()
df_spread=df_spread[df_spread['date']>"2017-10-23"]

# coincheck_bid-quoine_ask
model_ccbid_quask=get_prophetmodel("coincheck_bid-quoine_ask")

# 今後12時間を予測する
predict_hour = 12
future_ccbid_quask = model_ccbid_quask.make_future_dataframe(periods=predict_hour*60, freq = 'min')
forecast_ccbid_quask = model_ccbid_quask.predict(future_ccbid_quask)
model_ccbid_quask.plot(forecast_ccbid_quask).savefig('predict_12h.png')

# 要素ごと
model_ccbid_quask.plot_components(forecast_ccbid_quask).savefig('component.png')
