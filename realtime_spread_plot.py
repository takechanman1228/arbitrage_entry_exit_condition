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

def plot_two_spreads(ex_1, ex_2, period_hour):
    spread_a_list = []
    spread_b_list = []
    dt_now = datetime.datetime.now()
    day = dt_now.day

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
    df_spread=df_spread[(df_spread.date>dt_now - datetime.timedelta(hours=period_hour)) & (df_spread.date<dt_now)]

    plt.figure()
    ax = df_spread[ex_1+"_bid-"+ex_2+"_ask"].plot.hist(bins=100, range=(-6000, 6000), alpha=0.6,legend=True)
    ax = df_spread[ex_2+"_bid-"+ex_1+"_ask"].plot.hist(bins=100, range=(-6000, 6000), alpha=0.6,legend=True)
    plt.savefig(output_folder_name+'_'+str(period_hour)+'h.png')

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
    column_name = ["Date","coincheck_bid-quoine_ask","quoine_bid-coincheck_ask"]
    df_market_spread=pd.DataFrame(ticker_list, columns=column_name)
    df_market_spread=df_market_spread[(df_market_spread.date>dt_now - datetime.timedelta(hour=period_hour)) & (df_market_spread.date<dt_now)]

    df_market_spread.Date=pd.to_datetime(df_market_spread.Date)
    df_market_spread.index = df_market_spread.Date
    # df_market_spread.head()

    plt.figure()#初期化
    ax = df_market_spread["coincheck_bid-quoine_ask"].plot(legend=True,ylim=[-5000,5000])
    ax = df_market_spread["quoine_bid-coincheck_ask"].plot(legend=True,ylim=[-5000,5000])
    plt.savefig(output_folder_name+'timeseries_'+str(period_hour)+'h.png')


# TODO:日付こえた場合の処理

while True:
    # global dt_now
    dt_now = datetime.datetime.now()
    last_update_min = 0
    # フォルダ作成
    input_folder_name = "./simulation_data/"
    # global output_folder_name
    output_folder_name = "/Users/admin/Dropbox/bitcoin_exchange_log/spread_image/"+dt_now.month+dt_now.day + "/"

    if not os.path.exists(output_folder_name):
        os.makedirs(output_folder_name)

    # データ読み取り
    # その日
    with open(input_folder_name+"2017-"+str(dt_now.month)+"-"+str(day)+"ticker_log.json") as data_file:
        data_json_today = json.load(data_file)
        ticker_log_today = collections.OrderedDict(sorted(data_json_today.items()))

    # 前の日
    with open(input_folder_name+"2017-"+str(dt_now.month)+"-"+str(day-1)+"ticker_log.json") as data_file:
        data_json_yesterday = json.load(data_file)
        ticker_log_yesterday = collections.OrderedDict(sorted(data_json_yesterday.items()))

    ticker_log = dict(ticker_log_today, **ticker_log_yesterday)


    if dt_now.minute % 3 == 0 and dt_now.minute != last_update_min:
        plot_two_spreads("coincheck","quoine", 1)
        plot_two_spreads("coincheck","quoine", 3)
        plot_two_spreads("coincheck","quoine", 6)
        plot_two_spreads("coincheck","quoine", 12)
        plot_two_spreads("coincheck","quoine", 24)
        spread_time_series_plot(12)
        last_update_min = dt_now.minute
