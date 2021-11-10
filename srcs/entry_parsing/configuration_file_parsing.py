#!/usr/bin/python3

import os
import time
import json
import math
import sqlalchemy
import sys, getopt
import requests as rq
from dotenv import load_dotenv

MAX_QUANTITY = 100
MIN_QUANTITY = 5
DEFAULT_INTERVAL = "1d"
DEFAULT_LOOKBACK = "180 day ago UTC"
DEFAULT_INTERVAL_VALIDATE = "6h"
DEFAULT_LOOKBACK_VALIDATE = "7 day ago UTC"
bot = sys.argv[0]
url_binance_ticker_price = "https://api.binance.com/api/v3/ticker/price?symbol="

# Making sure that the symbol in the configuration file is valid for Binance

def parse_attributes(symbols):
    quantity = 0
    for i in range(len(symbols)):
        if 'quantity' in symbols[i]:
            if symbols[i]['quantity'] <= MIN_QUANTITY or symbols[i]['quantity'] > MAX_QUANTITY:
                print('Invalid quantity ' + str(symbols[i]['quantity']) + ' for symbol ' + symbols[i]['symbol'])
                print('Quantity should be between >= ' + str(MIN_QUANTITY) + ' and <= ' + str(MAX_QUANTITY) + '!')
                print('Quantity default value is ( Number_of_symbols / ' + str(MAX_QUANTITY) + ' )')
                sys.exit(1)
            else:
                quantity += math.floor(symbols[i]['quantity'])
        else:
            symbols[i]['quantity'] = math.floor(MAX_QUANTITY / len(symbols))
            quantity += symbols[i]['quantity']
        if not 'interval' in symbols[i]:
            symbols[i]['interval'] = DEFAULT_INTERVAL
        if not 'lookback' in symbols[i]:
            symbols[i]['lookback'] = DEFAULT_LOOKBACK
        if not 'interval_validate' in symbols[i]:
            symbols[i]['interval_validate'] = DEFAULT_INTERVAL_VALIDATE
        if not 'lookback_validate' in symbols[i]:
            symbols[i]['lookback_validate'] = DEFAULT_LOOKBACK_VALIDATE
    if quantity > MAX_QUANTITY:
        print('Invalid quantity the total quantity of your symbols is above 100% which is impossible check your configuration file')
        print('Quantity default value is ( Number_of_symbols / ' + str(MAX_QUANTITY) + ' )')
        sys.exit(1)
    return symbols

# Making sure that the symbol in the configuration file is valid for Binance

def parse_symbol(symbol):
    if symbol[-4:] != 'USDT':
        print('Error: ' + symbol + ' is not valid for BinanceBot check your configuration file')
        print('BinanceBot can only hold USDT currency as pair with another crypto like -> BTCUSDT, XRPUSDT, ETHUSDT, etc..')
        print('Note that you cannot trade USDT currency such as -> USDTBIDR, USDTRUB, USDTUAH, etc..')
        sys.exit(1)
    res = rq.get(url_binance_ticker_price + symbol).json()
    if 'msg' in res:
        print(symbol + ' is not valid for BinanceBot check your configuration file')
        print(res["msg"])
        print("Return Code : " + str(res["code"]))
        sys.exit(1)
    elif symbol == "":
        print(symbol + ' is not valid for BinanceBot check your configuration file')
        sys.exit(1)
    return symbol

# Parsing all symbols in the configuration file with JSON format

def parse_config_file(config_file):
    if config_file == '':
        print ("Error: configuration file missing")
        sys.exit(1)
    try:
        conf_fd = open(config_file,)
    except IOError:
        print ("Error: can't open " + config_file)
        sys.exit(1)
    try:
        config_object = json.load(conf_fd)
    except ValueError as e:
        print (config_file + " is not a valid config file")
        sys.exit(1)
    if 'symbols' in config_object:
        if len(config_object['symbols']) <= 0:
            print("Error: your configuration file is empty")
            sys.exit(1)
        if 'symbol' in config_object['symbols'][0]:
            symbols = []
    else:
        print("Error: configuration file doesn't have the right key")
        sys.exit(1)
    config_object['symbols'] = parse_attributes(config_object['symbols'])
    for symbol in config_object['symbols']:
        parse_symbol(symbol['symbol'])
        symbols.append(symbol)
    for i in range(len(symbols)):
        for j in range(len(symbols)):
            if symbols[i]['symbol'] == symbols[j]['symbol'] and i != j:
                print("Error: duplicated symbol " + symbols[i]['symbol'] + " in configuration file")
                sys.exit(1)
    return symbols

# Taking all arguments of the program to parse -h and -f options.
# Making sure that the use is sending valid input and valid symbol.

def parse_entry(argv):
    config_file = ""
    try:
        opts, args = getopt.getopt(argv, "hf:", ["help", "file="])
    except getopt.GetoptError:
        print ('python3 ' + bot + ' -f <file> or --file=<file>')
        print ('python3 ' + bot + ' -h or --help')
        sys.exit(1)
    if len(opts) <= 0:
        print ('python3 ' + bot + ' -f <file> or --file=<file>')
        print ('python3 ' + bot + ' -h or --help')
        sys.exit(1)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print ('python3 ' + bot + ' -f <file> or --file=<file>')
            sys.exit(0)
        elif opt in ('-f', '--file'):
            config_file = arg
    return parse_config_file(config_file)

if __name__ == "__main__":
    symbols = parse_entry(sys.argv[1:])
    print(symbols)
