import logging
import logging.config
from datetime import timedelta

DATABASE = 'dbname=cryptoalarm user=postgres'
REST_URL = 'http://localhost/endpoint'

COINS = {
    # 'BTC': {
    #     'rpc': 'http://bitcoin:local321@147.229.9.86:8332',
    #     'explorer': 'https://blockchain.info/search?search={}',
    # },
    'LTC': {
        'rpc': 'http://bitcoin:local321@147.229.9.86:9332',
        'explorer': 'http://explorer.litecoin.net/search?q={}',
    },
    'DASH': {
        'rpc': 'http://dash:local321@147.229.9.86:9998',
        'explorer': 'https://explorer.dash.org/search?q={}'
    },
    'ZEC': {
        'rpc': 'http://bitcoin:local321@147.229.9.86:9997',
        'explorer': 'https://explorer.zcha.in/search?q={}',
    },
    # 'ETH': {
    #   'rpc': 'http://localhost:8545',
    #   'explorer': '',
    #},
    # 'BCH' : {
    #   'rpc': '',
    #   'explorer': '',
    #},
}

SMTP = {
    'server': 'mailtrap.io',
    'port': 2525,
    'username': 'd673e05d055dc4',
    'password': '6bf26fc7b40fe4',
}

MAIL = {
    'from': 'cryptoalarm@example.com',
    'subject': 'Cryptoalarm notify',
    'template': 'Monitorovaná adresa {name} {address} pro {coin} byla nalezena v těchto transakcích:\n{txs}',
}

NOTIFY_INTERVAL = timedelta(minutes=1)

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