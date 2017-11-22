import logging
import smtplib
import requests
import queue
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from config import logger
import config as cfg


class Notifier():
    queue = queue.Queue()
    data = {}
    database = None
    rest = None
    mailer = None
    last_run = None

    def __init__(self, database):
        self.database = database
        self.rest = Rest()
        self.mailer = Mailer()
        self.load()

        self.last_run = datetime.now()

    def load(self):
        logger.info('Notifier: load')
        self.data = {}

        for address in self.database.get_addresses():
            if not address['coin'] in self.data:
                self.data[address['coin']] = {}

            if not address['hash'] in self.data[address['coin']]:
                self.data[address['coin']][address['hash']] = {
                    'in': [],
                    'out': [],
                    'in_users': [],
                    'out_users': [],
                    'inout_users': [],
                }

            ptr = self.data[address['coin']][address['hash']]

            for type in ['in', 'out', 'inout']:
                ptr[type + '_users'] = self.database.get_address_users(address['address_id'], type)

    def add_transaction(self, coin, tx):
        self.queue.put((coin, tx))

    def worker(self, stop):
        while not stop.is_set():
            try:
                coin, tx = self.queue.get(timeout=cfg.NOTIFY_INTERVAL.total_seconds())
            except queue.Empty:
                self.reload()
                continue

            self.process_transaction(coin, tx)
            if self.last_run + cfg.NOTIFY_INTERVAL < datetime.now():
                self.reload()

    def reload(self):
        self.notify()
        self.load()
        self.last_run = datetime.now()

    def process_transaction(self, coin, tx):
        coin_name = str(coin)
        for type in ['in', 'out']:
            intersect = set(self.data[coin_name].keys()) & tx[type]

            for address in intersect:
                self.data[coin_name][address][type].append(tx['hash'])

    def notify(self):
        logger.info('Notifier: notify')

        for coin_name in self.data:
            for address, address_data in self.data[coin_name].items():

                # notify users with INOUT about IN and OUT tranasctions
                if address_data['out'] or address_data['in']:
                    for user in address_data['inout_users']: 
                        self.send(coin_name, user, address, address_data['out'] + address_data['in'])

                if address_data['out']:
                    for user in address_data['out_users']: 
                        self.send(coin_name, user, address, address_data['out'])

                if address_data['in']:
                    for user in address_data['in_users']: 
                        self.send(coin_name, user, address, address_data['in'])

                address_data['in'] = []
                address_data['out'] = []

    def send(self, coin, user, address, txs):
        logger.debug('%s: notifying user %s about %s', coin, user, txs)

        if user['notify'] == 'email':
            self.mailer.send(coin, user, address, txs)
        elif user['notify'] == 'rest':
            self.rest.send(coin, user, address, txs)


class Sender():
    def send(self, user, address, txs):
        raise NotImplementedError()

class Mailer(Sender):
    server = None

    def connect(self):
        self.server = smtplib.SMTP(cfg.SMTP['server'], cfg.SMTP['port'])
        self.server.starttls()
        self.server.login(cfg.SMTP['username'], cfg.SMTP['password'])

    def build_message(self, coin, user, address, txs):
        template = cfg.MAIL['template']
        if user['template']:
            template = user['template']

        txs_links = []
        for tx in txs:
            tx_url = cfg.COINS[coin]['explorer'].format(tx)
            txs_links.append('<a href="{}">{}</a>'.format(tx_url, tx))

        address_url = cfg.COINS[coin]['explorer'].format(address)
        address_str = '<a href="{}">{}</a>'.format(address_url, address)

        return template.format(address=address_str, coin=coin, name=user['name'], txs='\n'.join(txs_links))

    def send(self, coin, user, address, txs):
        body = self.build_message(coin, user, address, txs)
        msg = MIMEText(body, 'html')
        msg['Subject'] = cfg.MAIL['subject']
        msg['From'] = cfg.MAIL['from']
        msg['To'] = user['email']

        self.connect()
        self.server.sendmail(cfg.MAIL['from'], [user['email']], msg.as_string())
        self.server.quit()

class Rest(Sender):
    headers = {'content-type': 'application/json'}

    def build_message(self, coin, user, address, txs):
        return {
            'user': user['user_id'],
            'address': address,
            'transactions': txs
        }

    def send(self, user, address, txs):
        payload = self.build_message(coin, user, address, txs)
        requests.post(cfg.REST_URL, json=payload, headers=self.headers)

