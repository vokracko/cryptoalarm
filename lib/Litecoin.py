from lib.Bitcoin import Bitcoin
from datetime import timedelta

class Litecoin(Bitcoin):
    block_time = timedelta(seconds=150)