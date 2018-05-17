import requests
import json
import time
import logging
from functools import reduce
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Coin():
    url = None
    block_time = None
    block = None
    reraise = False

    def __init__(self, config, stop):
        self.config = config
        self.url = config['urls'][self.__class__.__name__]
        self.stop = stop
        self.transactions = {}

    def test_connection(self):
        self.reraise = True
        try:
            self.get_block_hash(1)
        except:
            return False
        self.reraise = False

        return True

    def get_block_time(self):
        if not self.block_time:
            raise NotImplementedError
        
        return self.block_time

    def get_block_hash(self, number = None):
        raise NotImplementedError()

    def get_last_block_number(self):
        raise NotImplementedError()

    def get_block_creation_time(self, number=None):
        raise NotImplementedError

    def get_block(self, number):
        raise NotImplementedError()

    def get_block_transactions(self, number = None):
        raise NotImplementedError()

    def get_transaction(self, tx_hash):
        raise NotImplementedError()

    def get_transaction_io(self, tx_hash):
        raise NotImplementedError()

    def rpc(self, method, *args, **kwargs):
        retry_interval = self.config['retry_interval_min']
        headers = {'content-type': 'application/json'}
        payload = {
            'jsonrpc': '2.0',
            'method': method,
            'params': list(args),
            'id': 0,
        }

        while True:
            try:
                response = requests.post(self.url, json=payload, headers=headers, timeout=(self.config['timeout']['connect'], self.config['timeout']['read']))
                data = response.json()

                if 'error' in data and data['error']:
                    logger.error(data)
                    raise requests.exceptions.RequestException
            except Exception as e:
                if self.reraise:
                    raise e

                if self.stop.is_set():
                    raise InterruptedError

                logger.warn("%s: request failed, will be repeated after %ss", self.__class__.__name__, retry_interval)
                time.sleep(retry_interval)
                retry_interval = min(retry_interval * 2, self.config['retry_interval_max'])

                continue

            return data['result']

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.__class__.__name__


class BTC(Coin):
    block_time = timedelta(minutes=15)

    def get_block_hash(self, number = None):
        if number is None:
            return self.block['hash']

        return self.rpc('getblockhash', number)

    def get_last_block_number(self):
        number = self.rpc('getblockcount')
        return number, self.get_block_hash(number)

    def get_block_creation_time(self, number=None):
        if number is None and self.block is None:
            number, _  = self.get_last_block_number()

        if number is not None:
            self.get_block(number)

        return datetime.fromtimestamp(self.block['time'])

    def get_block(self, number):
        block_hash = self.get_block_hash(number)
        self.block = self.rpc('getblock', block_hash, True)
        return self.block

    def get_block_transactions(self, number = None):
        if number is not None:
            self.get_block(number)

        return self.block['tx']

    def get_transaction(self, tx_hash):
        if tx_hash not in self.transactions:
            self.transactions[tx_hash] = self.rpc('getrawtransaction', tx_hash, 1)
        
        return self.transactions[tx_hash]
        
    def get_transaction_io(self, tx_hash):
        self.transactions = {}
        tx = self.get_transaction(tx_hash)
        vout = reduce(lambda acc, item: item['scriptPubKey'].get('addresses', []) + acc, tx['vout'], [])
        vin = reduce(lambda acc, item: self.process_inputs(item) + acc, tx['vin'], [])
        return {'in': set(vin), 'out': set(vout)}

    def process_inputs(self, input):
        if 'coinbase' in input:
            return []

        txid, index = input['txid'], input['vout']
        tx = self.get_transaction(txid)

        return tx['vout'][index]['scriptPubKey'].get('addresses', [])

class BCH(BTC):
    block_time = timedelta(minutes=10)


class DASH(BTC):
    block_time = timedelta(seconds=150)


class LTC(BTC):
    block_time = timedelta(seconds=150)


class ZEC(BTC):
    block_time = timedelta(seconds=150)


class ETH(Coin):
    block_time = timedelta(seconds=15)
    ERC20_TRANSFER_PREFIX = '0xa9059cbb'

    def get_block_hash(self, number = None):
        if number is None:
            return self.block['hash']

        return self.get_block(number)['hash']

    def get_last_block_number(self):
        self.block = self.rpc('eth_getBlockByNumber', 'latest', False)
        return int(self.block['number'], 16), self.block['hash']

    def get_block_creation_time(self, number=None):
        if number is not None:
            self.get_block(number)

        return datetime.fromtimestamp(int(self.block['timestamp'], 16))

    def get_block(self, number):
        self.block = self.rpc('eth_getBlockByNumber', hex(number), False)
        return self.block

    def get_block_transactions(self, number = None):
        if number is not None:
            self.get_block(number)

        return self.block['transactions']

    def get_transaction(self, tx_hash):
        return self.rpc('eth_getTransactionByHash', tx_hash)

    def get_transaction_io(self, tx_hash):
        tx = self.get_transaction(tx_hash)
        result = {'in': set([tx['from']]), 'out': set([tx['to']])}
        input_data = tx['input']

        if input_data.startswith(self.ERC20_TRANSFER_PREFIX):
            recipient = '0x' + input_data[34:74]
            result['out'].add(recipient)

        return result