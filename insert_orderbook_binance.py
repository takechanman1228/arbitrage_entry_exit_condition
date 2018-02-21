import ccxt
import json
# import pandas as pd
import numpy as np
import matplotlib.pylab
from datetime import datetime
# import seaborn as sns
import pickle
print(ccxt.exchanges) # print a list of all available exchange classes
from time import sleep

from urllib.parse import urlparse
import mysql.connector

# binanceででる
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

url = urlparse('mysql://take@localhost:3306/bitcoin')

conn = mysql.connector.connect(
    host = url.hostname or 'take',
    port = url.port or 3306,
    user = url.username or 'root',
    password = url.password or '',
    database = url.path[1:],
)
cur = conn.cursor()

binance = ccxt.binance()
symbol_l = []
for symbol in binance.symbols:
    if symbol[-4:] == "/BTC":
        symbol_l.append(symbol)

trade_id_dict_prev_loop = {}


while True:
    exchange_name = "binance"
    # percent_list = [0.025,0.05,0.075,0.1,0.125,0.15,0.175,0.2]
    percent_list = [0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.1,0.125,0.15,0.175,0.2]
    for pair_name in symbol_l:
        try:
            ob=binance.fetch_order_book(pair_name)
        # except ccxt.errors.ExchangeError:
        except:
            print("order book fetch failed")
            sleep(60)
            continue

        print(pair_name)
        percent_coint_dict = dict.fromkeys(percent_list,0)
        timestamp = ob["timestamp"]
        best_ask = ob["asks"][0][0]

        for percent in percent_list:
        # for percent in [0.01,0.025,0.075,0.1,0.125,0.15,0.175,0.2]:
            sum_coin_amount = 0
            flag_dict = {}
            for ask in ob["asks"]:
        #         print(ob["asks"][0][0]*(1+percent),)
                # ask[0]-> price
                # ask[1]->amount
                sum_coin_amount+=ask[1]
                # ob["asks"][0][0]はbest ask
                # 価格が2.5%とかこえたとき
                if best_ask*(1+percent) < ask[0]:
                    # print(percent,sum_coin_amount)
                    percent_coint_dict[percent] = sum_coin_amount
        #             flag = 1
                    break
        # 一行挿入
        sql_string = "INSERT INTO orderbook \
        (exchange_name,pair_name,timestamp,best_ask,`1`,`2`,`3`,`4`,`5`,`6`,`7`,`8`,`9`,`10`,`12_5`,`15`,`17_5`,`20`) \
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        percent_amount_list = []
        # 2_5,5,7_5,10,12_5,15,17_5,20
        for percent in percent_list:
            amount = percent_coint_dict[percent]
            percent_amount_list.append(amount)
        try:
    #         print(sql_string)
            print([exchange_name,pair_name,timestamp,best_ask]+percent_amount_list)
            cur.execute(sql_string, [exchange_name,pair_name,timestamp,best_ask]+percent_amount_list)
            conn.commit()
        except:

            conn.rollback()
            raise

        sleep(1)
