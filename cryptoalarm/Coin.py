import requests
import json
import time
from functools import reduce
from datetime import timedelta
import config as cfg

logger = cfg.logger


class Coin():
    url = None
    block_time = None
    block = None

    def __init__(self, url, stop):
        self.url = url
        self.stop = stop

    def get_block_time(self):
        if not self.block_time:
            raise NotImplementedError
        
        return self.block_time

    def get_block_hash(self, number = None):
        raise NotImplementedError()

    def get_last_block_number(self):
        raise NotImplementedError()

    def get_block(self, number):
        raise NotImplementedError()

    def get_block_transactions(self, number = None):
        raise NotImplementedError()

    def get_transaction(self, tx_hash):
        raise NotImplementedError()

    def get_transaction_io(self, tx_hash):
        raise NotImplementedError()

    def rpc(self, method, *args, **kwargs):
        retry_interval = cfg.RETRY_INTERVAL_MIN
        headers = {'content-type': 'application/json'}
        payload = {
            'jsonrpc': '2.0',
            'method': method,
            'params': list(args),
            'id': 0,
        }

        while not self.stop.is_set():
            try:
                response = requests.post(self.url, json=payload, headers=headers, timeout=(cfg.TIMEOUT['connect'], cfg.TIMEOUT['read']))
                data = response.json()

                if 'error' in data and data['error']:
                    logger.error(data)
                    raise requests.exceptions.RequestException
            except requests.exceptions.RequestException:
                logger.warn("%s: request failed, will be repeated after %ss", self.__class__.__name__, retry_interval)
                time.sleep(retry_interval)
                retry_interval = min(retry_interval * 2, cfg.RETRY_INTERVAL_MAX)
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
        return self.rpc('getblockcount')

    def get_block(self, number):
        block_hash = self.get_block_hash(number)
        self.block = self.rpc('getblock', block_hash, True)
        return self.block

    def get_block_transactions(self, number = None):
        if number is not None:
            self.get_block(number)

        return self.block['tx']

    def get_transaction(self, tx_hash):
        return self.rpc('getrawtransaction', tx_hash, 1)

    def get_transaction_io(self, tx_hash):
        tx = self.get_transaction(tx_hash)
        vout = reduce(lambda acc, item: item['scriptPubKey'].get('addresses', []) + acc, tx['vout'], [])
        vin = reduce(lambda acc, item: self.process_inputs(item) + acc, tx['vin'], [])
        return {'in': set(vin), 'out': set(vout), 'hash': tx_hash}

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

    def process_inputs(self, input):
        if 'coinbase' in input:
            return []
        return [input.get('address')]


class ETH(Coin):
    block_time = timedelta(seconds=15)

    def get_block_hash(self, number = None):
        if number is None:
            return self.block['hash']

        return self.get_block(number)['hash']

    def get_last_block_number(self):
        return int(self.rpc('eth_getBlockByNumber', 'latest', False)['number'], 16)

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
        return {'in': set([tx['from']]), 'out': set([tx['to']]), 'hash': tx_hash}
