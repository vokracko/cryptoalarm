#!/usr/bin/env python3

import threading
import logging
from timeit import default_timer as timer
from datetime import datetime, timedelta
from .coin import BTC, BCH, DASH, ZEC, LTC, ETH
from .database import Database
from .notifier import Notifier

logger = logging.getLogger(__name__)

class Monitor():
    stop = threading.Event()
    coins = []
    threads = []
    database = None
    notifier = None

    def __init__(self, config):
        self.config = config
        self.database = Database(config['db'])
        self.notifier = Notifier(config, self.database)

        for coin in config['coins']:
            coin_inst = coin(config, self.stop)
            coin_inst.db_id = self.database.get_coin(coin_inst.__class__.__name__)['id']
            self.coins.append(coin_inst)

    def shutdown(self, signum, frame):
        logger.info('Shuting down')
        self.stop.set()
        for thread in self.threads:
            thread.join()
    
    def test_connection(self):
        self.notifier.test_connection()

        for coin in self.coins:
            if not coin.test_connection():
                raise ConnectionError('{}: node unreachable'.format(coin.__class__.__name__))

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
            number, block_hash = coin.get_last_block_number()
            self.database.set_block_number(coin, number, block_hash)
            logger.info('%s: setting %s as last processed block', coin, number)

    def process_block(self, database, coin, number):
        time_start = timer()
        coin.get_block(number)
        block_id = database.set_block_number(coin, number, coin.get_block_hash())
        logger.info('%s: processing block: %s', coin, number)
        cnt = 0

        for tx_hash in coin.get_block_transactions():
            addresses = coin.get_transaction_io(tx_hash)
            self.notifier.add_transaction(coin, number, block_id, tx_hash, addresses)
            cnt += 1

        time_total = timer() - time_start
        logger.debug('%s: processed %d transactions in %.4fs', coin, cnt, time_total)

        return number + 1

    def last_processed_block(self, database, coin):
        number = database.get_last_block_number(coin)

        while True:
            hash_saved = database.get_block_hash(coin, number)
            hash_node = coin.get_block_hash(number)

            if hash_saved == hash_node or hash_saved is None:
                break
            
            database.delete_block(coin, number)
            number -= 1

        return number

    def worker(self, coin):
        database = Database(self.config['db'])

        while not self.stop.is_set():
            current_number = self.last_processed_block(database, coin) + 1
            last_number, _ = coin.get_last_block_number()

            while current_number <= last_number:
                if self.stop.is_set():
                    break

                try:
                    current_number = self.process_block(database, coin, current_number)
                except InterruptedError:
                    break

            until_next_block = (coin.get_block_creation_time() + coin.get_block_time() - datetime.now()).total_seconds()

            if until_next_block < 0: # should be already generated
                until_next_block = (coin.get_block_time() * 0.05).total_seconds() # wait only brief time (5% of block time) before trying again

            self.stop.wait(timeout=until_next_block)

        logger.info('%s: terminating', coin)
