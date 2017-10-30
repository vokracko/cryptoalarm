#!/usr/bin/env python3

import time
import sys
import threading
import argparse
import signal
import logging
from timeit import default_timer as timer

from lib.Bitcoin import Bitcoin
# from lib.BitcoinCash import BitcoinCash
from lib.Litecoin import Litecoin
from lib.Dash import Dash
from lib.Zcash import Zcash
from lib.Ethereum import Ethereum
from lib.Database import Database
from lib.Notifier import Notifier

logging.basicConfig()
logger = logging.getLogger('cryptoalarm')
logger.setLevel(logging.INFO)

class Cryptoalarm():
    stop = threading.Event()
    coins = []
    threads = []
    notifier = None

    def __init__(self):
        signal.signal(signal.SIGINT, self.shutdown)

        btc = Bitcoin('http://bitcoin:local321@147.229.9.86:8332')
        ltc = Litecoin('http://bitcoin:local321@147.229.9.86:9332')
        dash = Dash('http://dash:local321@147.229.9.86:9998')
        zec = Zcash('http://bitcoin:local321@147.229.9.86:9997')
        eth = Ethereum('http://localhost:8545')

        self.coins = [btc, ltc, dash, zec, eth]
        self.database = Database('dbname=dp user=postgres')
        self.notifier = Notifier(self.database)

    def shutdown(self, signum, frame):
        logger.info('Shuting down')
        self.stop.set()
        for thread in self.threads:
            thread.join()

    def start(self):
        for coin in self.coins:
            logger.info('{}: starting monitor'.format(coin))
            thread = threading.Thread(target=self.worker, args=(coin,))
            self.threads.append(thread)
            thread.start()

    def set_last_blocks(self):
        for coin in self.coins:
            last_hash = coin.get_best_block_hash()
            self.database.set_last_block_hash(coin, last_hash)
            logger.info('{}: setting last_block_hash to {}'.format(coin, last_hash))

    def process_block(self, coin, hash):
        tx_acc = 0
        not_acc = 0
        coin.get_block(hash)
        logger.info('{}: processing block: height {}, hash {}'.format(coin, coin.get_block_height(), hash))
        cnt = 0

        for tx_hash in coin.get_block_transactions():
            tx_start = timer()
            tx = coin.get_transaction_io(tx_hash)
            tx_acc += timer() - tx_start
            not_start = timer()
            self.notifier.process_transaction(coin, tx)
            not_acc += timer() - not_start
            cnt += 1
        logger.info('{}: txs processed: {}, tx time {}, not time {}'.format(coin, cnt, tx_acc, not_acc))

        return coin.get_parent_block_hash()

    def worker(self, coin):
        database = Database('dbname=dp user=postgres')

        while not self.stop.is_set():
            last_hash = database.get_last_block_hash(coin)
            current_hash = coin.get_best_block_hash()
            database.set_last_block_hash(coin, current_hash)

            while current_hash != last_hash:
                # TODO jak řešit kill
                # pokud se to přeruší tady nezpracují se všechny bloky
                # pokud se to nepřeruší tak může to může běžet ještě dlouho po killu
                if self.stop.is_set():
                    break
                current_hash = self.process_block(coin, current_hash)

            self.notifier.notify(coin)
            self.stop.wait(timeout=coin.block_time.total_seconds())

        logger.info('{}: terminating'.format(coin))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crypto monitor')
    parser.add_argument('--init', action='store_true', help='Set current blocks as last ones processed')
    args = parser.parse_args()

    m = Cryptoalarm()

    if args.init:
        m.set_last_blocks()
    else:
        m.start()
