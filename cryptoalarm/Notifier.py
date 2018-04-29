import logging
import smtplib
import requests
import queue
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import logger
import config as cfg
from email.utils import formatdate
import time
import re


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

    def test_connection(self):
        self.rest.test_connection()
        self.mailer.test_connection()

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
                    'in': set(),
                    'out': set(),
                    'in_users': [],
                    'out_users': [],
                    'inout_users': [],
                }

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
                self.data[coin_name]['data'][address][type].add(tx['hash'])

    def notify(self):
        logger.info('Notifier: notify')

        for coin_name in self.data:
            for address, address_data in self.data[coin_name]['data'].items():
                explorer_url = self.data[coin_name]['explorer_url']
                # notify users with INOUT about IN and OUT tranasctions
                if address_data['out'] or address_data['in']:
                    for user in address_data['inout_users']: 
                        self.add(coin_name, explorer_url, user, address, address_data['out'] | address_data['in'])

                if address_data['out']:
                    for user in address_data['out_users']: 
                        self.add(coin_name, explorer_url, user, address, address_data['out'])

                if address_data['in']:
                    for user in address_data['in_users']: 
                        self.add(coin_name, explorer_url, user, address, address_data['in'])

                address_data['in'] = []
                address_data['out'] = []
        
        self.mailer.send()
        self.rest.send()

    def add(self, coin, explorer_url, user, address, txs):
        logger.debug('%s: add notification for user %s about %s', coin, user, txs)

        if user['notify'] in ['email', 'both']:
            self.mailer.add(coin, explorer_url, user, address, txs)

        if user['notify'] in ['rest', 'both']:
            self.rest.add(coin, explorer_url, user, address, txs)


class Sender():

    def add(self, coin, explorer_url, user, address, txs):
        self.queue.append((coin, explorer_url, user, address, list(txs)))

    def send(self):
        raise NotImplementedError()
    
    def test_connection(self):
        raise NotImplementedError()


class Mailer(Sender):
    server = None
    template = None
    email = None
    subject = None

    def __init__(self, subject, email, template):
        self.queue = []
        self.email = email
        self.subject = subject
        self.template = template
    
    def test_connection(self):
        logger.error("mail connect")
        self.connect()
        self.server.quit()
        logger.error("mail disconnect")

    def connect(self):
        self.server = smtplib.SMTP(cfg.SMTP['server'], cfg.SMTP['port'])
        self.server.set_debuglevel(True)
        self.server.starttls()
        self.server.login(cfg.SMTP['username'], cfg.SMTP['password'])

    def build_body(self, coin, explorer_url, user, address, txs):
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

    def build_message(self, coin, explorer_url, user, address, txs):
        body = self.build_body(coin, explorer_url, user, address, txs)
        part1 = MIMEText(re.sub('<[^<]+?>', '', body), 'plain')
        part2 = MIMEText('<html>'+body+'</html>', 'html')
        msg = MIMEMultipart('alternative')
        msg.attach(part1)
        msg.attach(part2)
        msg['Subject'] = self.subject.format(coin=coin, name=user['watchlist_name'])
        msg['From'] = self.email
        msg['To'] = user['email']
        msg['Date'] = formatdate(time.time())

        return msg.as_string()

    def send(self):
        try:
            self.connect()

            while self.queue:
                coin, explorer_url, user, address, txs = self.queue[0]
                message = self.build_message(coin, explorer_url, user, address, txs)
                self.server.sendmail(self.email, [user['email']], message)
                self.queue.pop(0)

            self.server.quit()
            logger.info('Notifier: MAIL sent')
        except Exception as e:
            logger.warn('Notifier: MAIL failed')


class Rest(Sender):
    url = None
    headers = {'content-type': 'application/json'}

    def __init__(self, url):
        self.queue = []
        self.url = url

    def test_connection(self):
        requests.post(self.url, json={}, headers=self.headers)

    def add(self, coin, explorer_url, user, address, txs):
        self.queue.append((coin, explorer_url, user, address, list(txs), True))

        if user['rest_url']:
            self.queue.append((coin, explorer_url, user, address, list(txs), False))

    def build_message(self, user, address, coin, txs, internal):
        if internal:
            return {
                'watchlist_id': user['watchlist_id'],
                'transactions': txs,
            }
        else:
            return {
                'address': address,
                'coin': coin,
                'watchlist': user['watchlist_name'],
                'transactions': txs,
            }

    def send(self):
        while self.queue:
            data = self.queue.pop()
            coin, explorer_url, user, address, txs, internal = data
            payload = self.build_message(user, address, coin, txs, internal)

            try:
                url = self.url if internal else user['rest_url']
                response = requests.post(url, json=payload, headers=self.headers)
            except requests.exceptions.Timeout:
                self.queue.append(data)
                logger.warn('Notifier: REST timedout, will be repeated')
            except requests.exceptions.RequestException as e:
                self.queue.append(data)
                logger.warn('Notifier: REST failed')
        
        logger.info('Notifier: REST sent')

