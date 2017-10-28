from lib.Bitcoin import Bitcoin
from datetime import timedelta

class Zcash(Bitcoin):
    block_time = timedelta(seconds=150)

    def process_inputs(self, input):
        if 'coinbase' in input:
            return []
        return [input.get('address')]