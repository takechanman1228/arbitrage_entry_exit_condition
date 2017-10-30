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

def make_df_spread(ex_1, ex_2):
    spread_a_list = []
    spread_b_list = []

    for key, ticker in ticker_log.items():
        spread_a = ticker[ex_1]["bid"] - ticker[ex_2]["ask"]
        spread_b = ticker[ex_2]["bid"] - ticker[ex_1]["ask"]
        spread_a_list.append(spread_a)
        spread_b_list.append(spread_b)

    df_spread=pd.DataFrame(index=list(ticker_log.keys()))

    df_spread[ex_1+"_bid-"+ex_2+"_ask"] = pd.DataFrame(spread_a_list, index=list(ticker_log.keys()))
    df_spread[ex_2+"_bid-"+ex_1+"_ask"] = pd.DataFrame(spread_b_list, index=list(ticker_log.keys()))

    df_spread['date']=df_spread.index
    df_spread['date']=pd.to_datetime(df_spread['date'], format='%Y-%m-%d-%H:%M:%S')
    return df_spread


def plot_two_spreads(ex_1, ex_2, period_hour):
    df=df_spread[(df_spread.date>dt_now - datetime.timedelta(hours=period_hour)) & (df_spread.date<dt_now)]

    plt.figure()
    ax = df[ex_1+"_bid-"+ex_2+"_ask"].plot.hist(bins=100, range=(-6000, 6000), alpha=0.6,legend=True)
    ax = df[ex_2+"_bid-"+ex_1+"_ask"].plot.hist(bins=100, range=(-6000, 6000), alpha=0.6,legend=True)
    plt.savefig(output_folder_name+str(period_hour)+'h.png')
    plt.close()

# 時系列
def spread_time_series_plot(period_hour):

    ticker_list = []
    for key, ticker in ticker_log.items():
        one_list = []
        one_line = [
        key,
        ticker["coincheck"]["bid"] - ticker["quoine"]["ask"],
        ticker["quoine"]["bid"] - ticker["coincheck"]["ask"],
        ]
        ticker_list.append(one_line)
    column_name = ["date","coincheck_bid-quoine_ask","quoine_bid-coincheck_ask"]
    df_market_spread=pd.DataFrame(ticker_list, columns=column_name)
    df_market_spread['date']=pd.to_datetime(df_market_spread['date'], format='%Y-%m-%d-%H:%M:%S')
    df_market_spread=df_market_spread[(df_market_spread.date>dt_now - datetime.timedelta(hours=period_hour)) & (df_market_spread.date<dt_now)]

    df_market_spread.Date=pd.to_datetime(df_market_spread.date)
    df_market_spread.index = df_market_spread.Date
    # df_market_spread.head()

    plt.figure()#初期化
    ax = df_market_spread["coincheck_bid-quoine_ask"].plot(legend=True)
    ax = df_market_spread["quoine_bid-coincheck_ask"].plot(legend=True)
    # ax = df_market_spread["coincheck_bid-quoine_ask"].plot(legend=True,ylim=[-6000,6000])
    # ax = df_market_spread["quoine_bid-coincheck_ask"].plot(legend=True,ylim=[-6000,6000])
    plt.savefig(output_folder_name+'timeseries_'+str(period_hour)+'h.png')
    plt.close()

last_update_min = -1

while True:
    dt_now = datetime.datetime.now()
    if dt_now.minute % 5 == 0 and dt_now.minute != last_update_min:
        try:
            dt_now = datetime.datetime.now()
            #
            # tstr = '2017-10-26 12:00:00'
            # dt_now = datetime.datetime.strptime(tstr, '%Y-%m-%d %H:%M:%S')
            day = dt_now.day

            # フォルダ作成
            input_folder_name = "/Users/admin/Dropbox/bitcoin_exchange_log/simulation_data/"
            output_folder_name = "/Users/admin/Dropbox/bitcoin_exchange_log/spread_image/"+str(dt_now.month)+str(dt_now.day) + "/"

            if not os.path.exists(output_folder_name):
                os.makedirs(output_folder_name)

            # データ読み取り
            # その日
            with open(input_folder_name+"2017-"+str(dt_now.month)+"-"+str(day)+"ticker_log.json") as data_file:
                data_json_today = json.load(data_file)
                # ticker_log_today = collections.OrderedDict(sorted(data_json_today.items()))

            # 前の日
            with open(input_folder_name+"2017-"+str(dt_now.month)+"-"+str(day-1)+"ticker_log.json") as data_file:
                data_json_yesterday = json.load(data_file)
                ticker_log_yesterday = collections.OrderedDict(sorted(data_json_yesterday.items()))

            data_json = dict(data_json_today, **data_json_yesterday)
            ticker_log = collections.OrderedDict(sorted(data_json.items()))

            df_spread = make_df_spread("coincheck","quoine")
            print("create df success")
        except Exception as e:
            print('error')
            print(e)
            sentence = str(e)
            time.sleep(10)
            continue

        print("start plotting")
        print(dt_now)
        print(dt_now.minute, last_update_min)
        plot_two_spreads("coincheck","quoine", 1)
        plot_two_spreads("coincheck","quoine", 3)
        plot_two_spreads("coincheck","quoine", 6)
        plot_two_spreads("coincheck","quoine", 12)
        plot_two_spreads("coincheck","quoine", 24)
        spread_time_series_plot(12)
        last_update_min = dt_now.minute

    else:
        time.sleep(10)
