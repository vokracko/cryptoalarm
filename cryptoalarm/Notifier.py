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
        self.rest = Rest(database.get_setting('notification_url'))
        self.mailer = Mailer(database.get_setting('email_subject'), 
                            database.get_setting('email_from'), 
                            database.get_setting('email_template'))
        self.load()
        self.last_run = datetime.now()

    def load(self):
        logger.info('Notifier: load')
        self.data = {}

        for coin in self.database.get_coins():
            self.data[coin['name']] = {
                'explorer_url': coin['explorer_url'],
                'data': {},
            }

        for address in self.database.get_addresses():
            if not address['hash'] in self.data[address['coin']]['data']:
                self.data[address['coin']]['data'][address['hash']] = {
                    'in': [],
                    'out': [],
                    'in_users': [],
                    'out_users': [],
                    'inout_users': [],
                }
                # print(json.dumps(self.data, indent=4))

            ptr = self.data[address['coin']]['data'][address['hash']]

            for type in ['in', 'out', 'inout']:
                ptr[type + '_users'] = self.database.get_address_users(address['address_id'], type)

    def add_transaction(self, coin, tx):
        self.queue.put((coin, tx))

    def worker(self, stop):
        while not stop.is_set() or not self.queue.empty(): 
            try:
                coin, tx = self.queue.get(timeout=cfg.NOTIFY_INTERVAL.total_seconds())
            except queue.Empty:
                self.reload()
                continue

            self.process_transaction(coin, tx)
            self.queue.task_done()
            if self.last_run + cfg.NOTIFY_INTERVAL < datetime.now():
                self.reload()

    def reload(self):
        self.notify()
        self.load()
        self.last_run = datetime.now()

    def process_transaction(self, coin, tx):
        coin_name = str(coin)
        for type in ['in', 'out']:
            intersect = set(self.data[coin_name]['data'].keys()) & tx[type]

            for address in intersect:
                self.data[coin_name]['data'][address][type].append(tx['hash'])

    def notify(self):
        logger.info('Notifier: notify')

        for coin_name in self.data:
            for address, address_data in self.data[coin_name]['data'].items():
                explorer_url = self.data[coin_name]['explorer_url']
                # notify users with INOUT about IN and OUT tranasctions
                if address_data['out'] or address_data['in']:
                    for user in address_data['inout_users']: 
                        self.send(coin_name, explorer_url, user, address, address_data['out'] + address_data['in'])

                if address_data['out']:
                    for user in address_data['out_users']: 
                        self.send(coin_name, explorer_url, user, address, address_data['out'])

                if address_data['in']:
                    for user in address_data['in_users']: 
                        self.send(coin_name, explorer_url, user, address, address_data['in'])

                address_data['in'] = []
                address_data['out'] = []

    def send(self, coin, explorer_url, user, address, txs):
        logger.debug('%s: notifying user %s about %s', coin, user, txs)

        if user['notify'] == 'email':
            self.mailer.send(coin, explorer_url, user, address, txs)
        elif user['notify'] == 'rest':
            self.rest.send(coin, explorer_url, user, address, txs)
        elif user['notify'] == 'both':
            self.mailer.send(coin, explorer_url, user, address, txs)
            self.rest.send(coin, explorer_url, user, address, txs)



class Sender():
    def send(self, coin, explorer_url, user, address, txs):
        raise NotImplementedError()

class Mailer(Sender):
    server = None
    template = None
    email = None
    subject = None

    def __init__(self, subject, email, template):
        self.email = email
        self.subject = subject
        self.template = template

    def connect(self):
        self.server = smtplib.SMTP(cfg.SMTP['server'], cfg.SMTP['port'])
        self.server.starttls()
        self.server.login(cfg.SMTP['username'], cfg.SMTP['password'])

    def build_message(self, coin, explorer_url, user, address, txs):
        template = self.template
        if user['email_template']:
            template = user['email_template']

        txs_links = []
        for tx in txs:
            tx_url = explorer_url + tx
            txs_links.append('<a href="{}">{}</a>'.format(tx_url, tx))

        address_url = explorer_url + address
        address_str = '<a href="{}">{}</a>'.format(address_url, address)

        return template.format(address=address_str, coin=coin, name=user['watchlist_name'], txs='\n'.join(txs_links))

    def send(self, coin, explorer_url, user, address, txs):
        body = self.build_message(coin, explorer_url, user, address, txs)
        msg = MIMEText(body, 'html')
        msg['Subject'] = self.subject.format(coin=coin, name=user['watchlist_name'])
        msg['From'] = self.email
        msg['To'] = user['email']

        self.connect()
        self.server.sendmail(self.email, [user['email']], msg.as_string())
        self.server.quit()

class Rest(Sender):
    url = None
    headers = {'content-type': 'application/json'}

    def __init__(self, url):
        self.url = url

    def build_message(self, coin, user, address, txs):
        return {
            'watchlist_id': user['watchlist_id'],
            'transactions': txs,
        }

    def send(self, coin, explorer_url, user, address, txs):
        payload = self.build_message(coin, user, address, txs)
        requests.post(self.url, json=payload, headers=self.headers)

