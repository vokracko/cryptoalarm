#!/usr/bin/env python3

import time
import sys
import threading
import argparse
import signal
import logging
from timeit import default_timer as timer

from lib.Coin import Bitcoin, BitcoinCash, Dash, Zcash, Litecoin, Ethereum
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
            number = coin.get_last_block_number()
            self.database.set_last_block_number(coin, number)
            logger.info('{}: setting last_block_number to {}'.format(coin, number))

    def process_block(self, coin, number):
        tx_acc = 0
        coin.get_block(number)
        logger.info('{}: processing block: {}'.format(coin, number))
        cnt = 0

        for tx_hash in coin.get_block_transactions():
            tx_start = timer()
            tx = coin.get_transaction_io(tx_hash)
            tx_acc += timer() - tx_start
            self.notifier.process_transaction(coin, tx)
            cnt += 1
        logger.info('{}: txs processed: {}, tx time {}'.format(coin, cnt, tx_acc))

        return number + 1

    def worker(self, coin):
        database = Database('dbname=dp user=postgres')

        while not self.stop.is_set():
            current_number = database.get_last_block_number(coin)
            last_number = coin.get_last_block_number()

            while current_number < last_number:
                if self.stop.is_set():
                    break

                database.set_last_block_number(coin, current_number)
                current_number = self.process_block(coin, current_number)

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
