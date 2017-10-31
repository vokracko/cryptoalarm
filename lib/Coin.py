import requests
import json
from functools import reduce
from datetime import timedelta


class Coin():
    url = None
    block_time = None
    block = None

    def __init__(self, url):
        self.url = url

    def get_block_time(self):
        if not self.block_time:
            raise NotImplementedError
        
        return self.block_time

    def get_best_block_hash(self):
        raise NotImplementedError()

    def get_block(self, hash):
        raise NotImplementedError()

    def get_block_height(self):
        raise NotImplementedError()

    def get_parent_block_hash(self, hash = None):
        raise NotImplementedError()

    def get_block_transactions(self, hash):
        raise NotImplementedError()

    def get_transaction(self, hash):
        raise NotImplementedError()

    def get_transaction_io(self, hash):
        raise NotImplementedError()

    def rpc(self, method, *args, **kwargs):
        headers = {'content-type': 'application/json'}
        payload = {
            'jsonrpc': '2.0',
            'method': method,
            'params': [item for item in args],
            'id': 0,
        }

        # print(json.dumps(payload))
        response = requests.post(self.url, json=payload, headers=headers)
        # TODO error handling
        # print(response.json())
        return response.json()['result']

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.__class__.__name__


class Bitcoin(Coin):
    block_time = timedelta(minutes=15)

    def get_best_block_hash(self):
        return self.rpc('getbestblockhash')

    def get_block(self, hash):
        self.block = self.rpc('getblock', hash, True)
        return self.block

    def get_block_height(self, hash = None):
        if hash is not None:
            self.get_block(hash)

        return int(self.block.get('height', 0))

    def get_parent_block_hash(self, hash = None):
        if hash is not None:
            self.get_block(hash)

        return self.block['previousblockhash']

    def get_block_transactions(self, hash = None):
        if hash is not None:
            self.get_block(hash)

        return self.block['tx']

    def get_transaction(self, hash):
        return self.rpc('getrawtransaction', hash, 1)

    def get_transaction_io(self, hash):
        tx = self.get_transaction(hash)
        vout = reduce(lambda acc, item: item['scriptPubKey'].get('addresses', []) + acc, tx['vout'], [])
        vin = reduce(lambda acc, item: self.process_inputs(item) + acc, tx['vin'], [])
        return {'in': set(vin), 'out': set(vout), 'hash': hash}

    def process_inputs(self, input):
        if 'coinbase' in input:
            return []

        txid, index = input['txid'], input['vout']
        tx = self.get_transaction(txid)

        return tx['vout'][index]['scriptPubKey'].get('addresses', [])


class BitcoinCash(Bitcoin):
    block_time = timedelta(seconds=10)


class Dash(Bitcoin):
    block_time = timedelta(seconds=150)


class Litecoin(Bitcoin):
    block_time = timedelta(seconds=150)


class Zcash(Bitcoin):
    block_time = timedelta(seconds=150)

    def process_inputs(self, input):
        if 'coinbase' in input:
            return []
        return [input.get('address')]


class Ethereum(Coin):
    block_time = timedelta(seconds=15)

    def get_best_block_hash(self):
        return self.rpc('eth_getBlockByNumber', 'latest', False)['hash']

    def get_block(self, hash):
        self.block = self.rpc('eth_getBlockByHash', hash, False)
        return self.block

    def get_block_height(self):
        return int(self.block.get('number', 0), 16)
    
    def get_parent_block_hash(self, hash = None):
        if hash is not None:
            self.get_block(hash)

        return self.block['parentHash']

    def get_block_transactions(self, hash = None):
        if hash is not None:
            self.get_block(hash)

        return self.block['transactions']

    def get_transaction(self, hash):
        return self.rpc('eth_getTransactionByHash', hash)

    def get_transaction_io(self, hash):
        tx = self.get_transaction(hash)
        return {'in': set([tx['from']]), 'out': set([tx['to']]), 'hash': hash}
