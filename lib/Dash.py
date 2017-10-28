from lib.Bitcoin import Bitcoin
from datetime import timedelta

class Dash(Bitcoin):
    block_time = timedelta(seconds=150)

    pass