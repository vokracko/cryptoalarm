#!/usr/bin/env python3

import time
import sys
import threading
import argparse
import signal
from timeit import default_timer as timer
from datetime import timedelta
from Coin import BTC, BCH, DASH, ZEC, LTC, ETH
from Database import Database
from Notifier import Notifier
from config import logger
import config as cfg


class Cryptoalarm():
    stop = threading.Event()
    coins = []
    threads = []
    database = None
    notifier = None

    def __init__(self):
        signal.signal(signal.SIGINT, self.shutdown)

        for coin_name, rpc in cfg.COINS.items():
            coin_inst = globals()[coin_name](rpc)
            self.coins.append(coin_inst)

        self.database = Database(cfg.DATABASE)
        self.notifier = Notifier(self.database)

    def shutdown(self, signum, frame):
        logger.info('Shuting down')
        self.stop.set()
        for thread in self.threads:
            thread.join()
    
    def test_connection(self):
        self.notifier.test_connection()

        for coin in self.coins:
            coin.get_last_block_number()

    def start(self):
        for coin in self.coins:
            logger.info('%s: starting monitor', coin)
            thread = threading.Thread(target=self.worker, args=(coin,))
            self.threads.append(thread)
            thread.start()
        
        thread = threading.Thread(target=self.notifier.worker, args=(self.stop,))
        self.threads.append(thread)
        thread.start()

    def set_last_blocks(self):
        for coin in self.coins:
            number = coin.get_last_block_number()
            self.database.set_last_block_number(coin, number)
            logger.info('%s: setting last_block_number to %s', coin, number)

    def process_block(self, coin, number):
        time_start = timer()
        coin.get_block(number)
        logger.info('%s: processing block: %s', coin, number)
        cnt = 0

        for tx_hash in coin.get_block_transactions():
            tx = coin.get_transaction_io(tx_hash)
            self.notifier.add_transaction(coin, tx)
            cnt += 1

        time_total = timer() - time_start
        logger.debug('%s: processed %d transactions in %.4fs', coin, cnt, time_total)

        return number + 1, time_total

    def worker(self, coin):
        database = Database(cfg.DATABASE)

        while not self.stop.is_set():
            current_number = database.get_last_block_number(coin)
            last_number = coin.get_last_block_number()
            processing_time = 0

            while current_number < last_number:
                if self.stop.is_set():
                    break

                current_number, block_time = self.process_block(coin, current_number)
                processing_time += block_time
                database.set_last_block_number(coin, current_number)

            until_next_block = (coin.block_time - timedelta(seconds=processing_time)).total_seconds()
            self.stop.wait(timeout=until_next_block)

        logger.info('%s: terminating', coin)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cryptoalarm')
    parser.add_argument('--init', action='store_true', help='Set current blocks as last ones processed')
    args = parser.parse_args()

    ca = Cryptoalarm()
    ca.test_connection()

    if args.init:
        ca.set_last_blocks()
    else:
        ca.start()
