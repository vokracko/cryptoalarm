#!/usr/bin/env python3

import time
import sys
import threading
import argparse

from lib.Bitcoin import Bitcoin
# from lib.BitcoinCash import BitcoinCash
from lib.Litecoin import Litecoin
from lib.Dash import Dash
from lib.Zcash import Zcash
from lib.Ethereum import Ethereum
from lib.Database import Database

def set_last_blocks(coin):
    database = Database('localhost', 'root', '', 'dp')
    last_hash = coin.get_best_block_hash()
    database.set_last_block_hash(coin, last_hash)


def process_block(coin, hash, addrs):
    coin.get_block(hash)
    print("processing", coin, "height", coin.get_block_height(), "hash", hash)

    for tx_hash in coin.get_block_transactions():
            tx = coin.get_transaction_io(tx_hash)

            # TODO dořešit pro všechny adresy
            # if addrs in tx['from'] + tx['to']:
                # print('Address {} found in tx: {}'.format(addrs, tx_hash))

    return coin.get_parent_block_hash()


def worker(coin):
    database = Database('localhost', 'root', '', 'dp')
    addrs = database.get_addresses(coin)[0]['hash']

    while True:
        last_hash = database.get_last_block_hash(coin)
        current_hash = coin.get_best_block_hash()
        database.set_last_block_hash(coin, current_hash)
        print(coin, current_hash, last_hash)

        while current_hash != last_hash:
            current_hash = process_block(coin, current_hash, addrs)

        time.sleep(coin.block_time.total_seconds())


parser = argparse.ArgumentParser(description='Crypto monitor')
parser.add_argument('--init', action='store_true', help='Set current blocks as last ones processed')
args = parser.parse_args()

btc = Bitcoin('http://bitcoin:local321@147.229.9.86:8332')
ltc = Litecoin('http://bitcoin:local321@147.229.9.86:9332')
dash = Dash('http://dash:local321@147.229.9.86:9998')
zec = Zcash('http://bitcoin:local321@147.229.9.86:9997')
eth = Ethereum('http://localhost:8545')

coins = [btc, ltc, dash, zec, eth]
threads = []

for coin in coins:
    if args.init:
        set_last_blocks(coin)
    else:
        thread = threading.Thread(target=worker, args=(coin,))
        threads.append(thread)
        thread.start()


# TODO ukončení
# TODO set current block for now
# TODO načtení nových adres
