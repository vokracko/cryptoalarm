from lib.Coin import Coin
from datetime import timedelta

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
        return {'from': [tx['from']], 'to': [tx['to']]}