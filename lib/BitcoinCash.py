from lib.Bitcoin import Bitcoin
from datetime import timedelta

class BitcoinCash(Bitcoin):
    block_time = timedelta(seconds=10)