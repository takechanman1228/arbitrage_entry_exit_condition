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

def plot_two_spreads(ex_1, ex_2, period_hour):
    spread_a_list = []
    spread_b_list = []
    dt_now = datetime.datetime.now()
    day = dt_now.day
    # その日
    with open("simulation_data/2017-10-"+str(day)+"ticker_log.json") as data_file:
        data_json_today = json.load(data_file)
        ticker_log_today = collections.OrderedDict(sorted(data_json.items()))

    # 前の日
    with open("simulation_data/2017-10-"+str(day-1)+"ticker_log.json") as data_file:
        data_json_yesterday = json.load(data_file)
        ticker_log_yesterday = collections.OrderedDict(sorted(data_json.items()))

    ticker_log = dict(ticker_log_today, **ticker_log_yesterday)

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
    df_spread=df_spread[(df_spread.date>dt_now - datetime.timedelta(hour=period_hour)) & (df_spread.date<dt_now)]

    plt.figure()
    ax = df_spread[ex_1+"_bid-"+ex_2+"_ask"].plot.hist(bins=100, range=(-6000, 6000), alpha=0.6,legend=True)
    ax = df_spread[ex_2+"_bid-"+ex_1+"_ask"].plot.hist(bins=100, range=(-6000, 6000), alpha=0.6,legend=True)
    plt.savefig(output_folder_name+'_'+str(period_hour)+'h.png')



# TODO:日付こえた場合の処理

while True:
    dt_now = datetime.datetime.now()
    last_update_min = 0
    # フォルダ作成
    global output_folder_name
    output_folder_name = "/Users/admin/Dropbox/bitcoin_exchange_log/spread_image/"+dt_now.month+dt_now.day

    if not os.path.exists(output_folder_name):
        os.makedirs(output_folder_name)

    if dt_now.minute % 3 == 0 and dt_now.minute != last_update_min:
        plot_two_spreads("coincheck","quoine", 1)
        plot_two_spreads("coincheck","quoine", 3)
        plot_two_spreads("coincheck","quoine", 6)
        plot_two_spreads("coincheck","quoine", 12)
        plot_two_spreads("coincheck","quoine", 24)
        last_update_min = dt_now.minute
