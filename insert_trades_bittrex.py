import ccxt
import json
import pandas as pd
import numpy as np
import matplotlib.pylab
from datetime import datetime
# import seaborn as sns
import pickle
print(ccxt.exchanges) # print a list of all available exchange classes
from time import sleep

from urllib.parse import urlparse
import mysql.connector

url = urlparse('mysql://take@localhost:3306/bitcoin')

conn = mysql.connector.connect(
    host = url.hostname or 'take',
    port = url.port or 3306,
    user = url.username or 'root',
    password = url.password or '',
    database = url.path[1:],
)
cur = conn.cursor()

symbol_l = [
             'ETH/BTC',
             'LTC/BTC',
             'XRP/BTC',
             'ETC/BTC',
             'XVG/BTC',
             'ADA/BTC',
             'NEO/BTC',
             'XMR/BTC',
             'OMG/BTC',
             'BTG/BTC',
             'ZCL/BTC',
             'XEM/BTC',
             'NBT/BTC',
             'SC/BTC',
             'LSK/BTC',
             # 'BCC/BTC',
]
bittrex = ccxt.bittrex()

trade_id_dict_prev_loop = {}
for pair_name in symbol_l:
    trade_id_dict_prev_loop[pair_name] = set()
while True:
    for pair_name in symbol_l:
        print(pair_name)
        try:
            trades=bittrex.fetchTrades(pair_name)
        # except ccxt.errors.ExchangeError:
        except:
            print("fetch trade failed")
            sleep(60)
            continue

        # print("len(trades)")
        # print(len(trades))
        trade_id_set_this_loop  = set()
        for trade in trades:

            price = trade["price"]
            amount = trade["amount"]
            timestamp = trade["timestamp"]
            trade_id = trade["id"]
            trade_id_set_this_loop.add(trade_id)
            if trade["side"] == "sell":
                side = 1
            elif trade["side"] == "buy":
                side = 0

            # 前回
            if trade_id in trade_id_dict_prev_loop[pair_name]:
                sql_string = "INSERT INTO trades \
                (exchange_name,pair_name,trade_id,timestamp,price,amount,buy_sell_type) \
                VALUES (%s,%s,%s,%s,%s,%s,%s)"

                try:
                    cur.execute(sql_string, ["bittrex",pair_name,trade_id,timestamp,price,amount,side])
                    # cur.execute('INSERT INTO bittrex_trades (bittrex_trade_id,timestamp,price,amount,buy_sell_type) VALUES (%s,%s,%s,%s)', [145862691,"2018-02-18T01:50:28.633",0.02052002,2.63045673,1])
                    conn.commit()
                except:

                    conn.rollback()
                    raise


        print("1秒前との差分個数")
        # print(trade_id_set_prev_loop.intersection(trade_id_set_this_loop))
        print(len(trade_id_dict_prev_loop[pair_name].difference(trade_id_set_this_loop)))
        # trade_id_set_prev_loop = trade_id_set_this_loop
        trade_id_dict_prev_loop[pair_name] = trade_id_set_this_loop
        sleep(5)
