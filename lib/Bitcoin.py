from lib.Coin import Coin
from functools import reduce
from datetime import timedelta

class Bitcoin(Coin):
    block_time = timedelta(minutes=15)

    def get_best_block_hash(self):
        return self.rpc('getbestblockhash')

    def get_block(self, hash):
        self.block = self.rpc('getblock', hash, True)
        return self.block

    def get_block_height(self):
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
        to = reduce(lambda acc, item: item['scriptPubKey'].get('addresses', []) + acc, tx['vout'], [])
        from_ = reduce(lambda acc, item: self.process_inputs(item) + acc, tx['vin'], [])
        return {'from': from_, 'to': to}

    def process_inputs(self, input):
        if 'coinbase' in input:
            return []

        txid, index = input['txid'], input['vout']
        tx = self.get_transaction(txid)

        return tx['vout'][index]['scriptPubKey'].get('addresses', [])