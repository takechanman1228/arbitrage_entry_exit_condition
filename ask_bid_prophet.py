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

    # フォルダ作成
    input_folder_name = "/Users/admin/Dropbox/bitcoin_exchange_log/simulation_data/"
    out_df_filename = "df_bid-ask_all.dump"
    # 15分に一回dataframe更新する
    if os.path.isfile(out_df_filename) and dt_now.minute % 30 == 0:
        with open(out_df_filename,"rb") as f:
            df_spread = pickle.load(f)
    else:
        # データ読み取り
        data_json_all = {}
        # TODO 今の日付
        # for day in [14,15,16,17,19,20,21,22,23,24,25,26,27,28,29,30]:
        for day in range(23,dt_now.day + 1):
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

last_update_min = -1
while True:
    dt_now = datetime.datetime.now()
    if dt_now.minute % 10 == 0 and dt_now.minute != last_update_min:
        try:

            day = dt_now.day

            # フォルダ作成
            # input_folder_name = "/Users/admin/Dropbox/bitcoin_exchange_log/simulation_data/"
            output_folder_name = "/Users/admin/Dropbox/bitcoin_exchange_log/prophet/"+str(dt_now.month)+str(dt_now.day) + "/"

            if not os.path.exists(output_folder_name):
                os.makedirs(output_folder_name)


            # output_folder_name = "/Users/admin/Dropbox/bitcoin_exchange_log/prophet/"
            df_spread = create_spread_df()
            df_spread=df_spread[df_spread['date']>"2017-10-23"]

            ex_1 = "coincheck"
            ex_2 = "quoine"
            model_name = ex_1 + "_bid" + "-"+ex_2+"_ask"
            # coincheck_bid-quoine_ask
            model_ccbid_quask=get_prophetmodel(model_name)

            # 今後12時間を予測する
            predict_hour = 12
            future_ccbid_quask = model_ccbid_quask.make_future_dataframe(periods=predict_hour*60, freq = 'min')
            forecast_ccbid_quask = model_ccbid_quask.predict(future_ccbid_quask)
            model_ccbid_quask.plot(forecast_ccbid_quask).savefig(output_folder_name+ex_1+"-"+ex_2+"_predict_12h.png")
            # 要素ごと
            model_ccbid_quask.plot_components(forecast_ccbid_quask).savefig(output_folder_name+ex_1+"-"+ex_2+"component.png")


            ex_2 = "coincheck"
            ex_1 = "quoine"
            model_name = ex_1 + "_bid" + "-"+ex_2+"_ask"
            # coincheck_bid-quoine_ask
            model_ccbid_quask=get_prophetmodel(model_name)

            # 今後12時間を予測する
            predict_hour = 12
            future_ccbid_quask = model_ccbid_quask.make_future_dataframe(periods=predict_hour*60, freq = 'min')
            forecast_ccbid_quask = model_ccbid_quask.predict(future_ccbid_quask)
            model_ccbid_quask.plot(forecast_ccbid_quask).savefig(output_folder_name+ex_1+"-"+ex_2+"_predict_12h.png")
            # 要素ごと
            model_ccbid_quask.plot_components(forecast_ccbid_quask).savefig(output_folder_name+ex_1+"-"+ex_2+"component.png")



        except Exception as e:
            print('error')
            print(e)
            sentence = str(e)
            time.sleep(10)
            continue
    else:
        time.sleep(10)
