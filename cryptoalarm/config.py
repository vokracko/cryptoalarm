import logging
import logging.config
from datetime import timedelta

DATABASE = 'dbname=cryptoalarm user=postgres host=127.0.0.1 password=secret'

COINS = {
    # 'BTC': 'http://bitcoin:local321@147.229.9.86:8332',
    'LTC': 'http://bitcoin:local321@147.229.9.86:9332',
    'DASH': 'http://dash:local321@147.229.9.86:9998',
    'ZEC': 'http://bitcoin:local321@147.229.9.86:9997',
    # 'ETH': 'http://localhost:8545',
    # 'BCH': '',
}

SMTP = {
    'server': 'mailtrap.io',
    'port': 2525,
    'username': 'd673e05d055dc4',
    'password': '6bf26fc7b40fe4',
}

NOTIFY_INTERVAL = timedelta(seconds=10)

TIMEOUT = { # in seconds
    'connect': 2,
    'read': 20,
}

LOGGER = {
    'version': 1,
    'formatters': {
        'f': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        },
    },
    'handlers': {
        'h': {
            'class': 'logging.StreamHandler',
            'formatter': 'f',
            'level': logging.DEBUG
        },
    },
    'root': {
        'handlers': ['h'],
        'level': logging.DEBUG,
    },
}

logging.config.dictConfig(LOGGER)
logger = logging.getLogger('cryptoalarm')