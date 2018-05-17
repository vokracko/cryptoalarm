import logging
import smtplib
import requests
import queue
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
import time
import re

logger = logging.getLogger(__name__)

class Notifier():
    queue = queue.Queue()
    data = {}
    database = None
    senders = []
    last_notify = None
    last_load = None

    def __init__(self, config, database):
        self.database = database
        self.config = config
        self.load()
        self.last_notify = datetime.now()

        mailer = Mailer(config,
            database.get_setting('email_subject'), 
            database.get_setting('email_from'), 
            database.get_setting('email_template')
        )
        self.senders = [mailer, Rest()]

    def test_connection(self):
        for sender in self.senders:
            sender.test_connection()

    def load(self):
        logger.info('load')
        self.data = {}

        for coin in self.database.get_coins():
            self.data[coin['name']] = {
                'explorer_url': coin['explorer_url'],
                'data': {},
            }

        for address in self.database.get_addresses():
            if not address['hash'] in self.data[address['coin']]['data']:
                self.data[address['coin']]['data'][address['hash']] = {
                    'txs': {'in': set(), 'out': set()},
                    'users': {'in': [], 'out': [], 'inout': []},
                }

            ptr = self.data[address['coin']]['data'][address['hash']]

            for type in ['in', 'out', 'inout']:
                ptr['users'][type] = self.database.get_address_users(address['address_id'], type)

        self.last_load = datetime.now()

    def add_transaction(self, coin, block_number, block_id, hash, addresses):
        self.queue.put((coin, block_number, block_id, hash, addresses))

    def worker(self, stop):
        while not stop.is_set() or not self.queue.empty(): 
            try:
                coin, block_number, block_id, hash, addresses = self.queue.get(timeout=self.config['notify_interval'])
            except queue.Empty:
                self.notify()
                continue

            self.process_transaction(coin, block_number, block_id, hash, addresses)
            self.queue.task_done()
            if self.last_notify + timedelta(seconds=self.config['notify_interval']) < datetime.now():
                self.notify()

            if self.last_load + timedelta(seconds=self.config['reload_interval']) < datetime.now():
                self.load()

        logger.info('sending remaining notifications')
        self.notify()

    def process_transaction(self, coin, block_number, block_id, hash, addresses):
        coin_name = str(coin)
        for type in ['in', 'out']:
            intersect = set(self.data[coin_name]['data'].keys()) & addresses[type]

            for address in intersect:
                self.data[coin_name]['data'][address]['txs'][type].add((block_number, block_id, hash))

    def notify(self):
        logger.info('notify')

        for coin_name in self.data:
            for address, address_data in self.data[coin_name]['data'].items():
                explorer_url = self.data[coin_name]['explorer_url']
                # notify users with INOUT about IN and OUT tranasctions
                if address_data['txs']['out'] or address_data['txs']['in']:
                    for user in address_data['users']['inout']: 
                        self.add(coin_name, explorer_url, user, address, address_data['txs']['out'] | address_data['txs']['in'])

                if address_data['txs']['out']:
                    for user in address_data['users']['out']: 
                        self.add(coin_name, explorer_url, user, address, address_data['txs']['out'])

                if address_data['txs']['in']:
                    for user in address_data['users']['in']: 
                        self.add(coin_name, explorer_url, user, address, address_data['txs']['in'])

                address_data['in'] = set()
                address_data['out'] = set()
        
        for sender in self.senders:
            sender.send()

        self.database.commit()
        self.last_notify = datetime.now()

    def add(self, coin, explorer_url, user, address, txs):
        logger.debug('%s: add notification for user %s about %s', coin, user, txs)
        self.database.insert_notifications(user['watchlist_id'], txs)

        for sender in self.senders:
            if user['notify'] in sender.types:
                sender.add(coin, explorer_url, user, address, txs)


class Sender():
    types = []

    def add(self, coin, explorer_url, user, address, txs):
        self.queue.append((coin, explorer_url, user, address, list(txs)))

    def send(self):
        raise NotImplementedError()
    
    def test_connection(self):
        pass


class Mailer(Sender):
    server = None
    template = None
    email = None
    subject = None
    types = ['mail', 'both']

    def __init__(self, config, subject, email, template):
        self.queue = []
        self.config = config
        self.email = email
        self.subject = subject
        self.template = template
    
    def test_connection(self):
        self.connect()
        self.server.quit()

    def connect(self):
        self.server = smtplib.SMTP(self.config['smtp']['server'], self.config['smtp']['port'])
        self.server.starttls()
        self.server.login(self.config['smtp']['username'], self.config['smtp']['password'])

    def build_body(self, coin, explorer_url, user, address, txs):
        template = self.template
        if user['email_template']:
            template = user['email_template']

        txs_links = []
        for block_number, block_id, tx in txs:
            tx_url = explorer_url + tx
            txs_links.append('#{} <a href="{}">{}</a>'.format(block_number, tx_url, tx))

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
                coin, explorer_url, user, address, txs = self.queue.pop()
                message = self.build_message(coin, explorer_url, user, address, txs)
                self.server.sendmail(self.email, [user['email']], message)

            self.server.quit()
            logger.info('MAIL sent')
        except Exception as e:
            logger.warn('MAIL failed')


class Rest(Sender):
    types = ['rest', 'both']

    def __init__(self):
        self.queue = []
    
    def add(self, coin, explorer_url, user, address, txs):
        if not user['rest_url']:
            return

        super(Rest, self).add(coin, explorer_url, user, address, txs)

    def build_message(self, coin, user, address, txs):
        txs = [list(tx) for tx in txs]
        
        return {
            "address": address,
            "coin": coin,
            "watchlist": user['watchlist_name'],
            "transactions": [[tx[0], tx[2]] for tx in txs], # block number and tx hash
        }

    def send(self):
        new_queue = []
        while self.queue:
            data = self.queue.pop()
            coin, explorer_url, user, address, txs = data
            payload = self.build_message(coin, user, address, txs)

            try:
                response = requests.post(user['rest_url'], json=payload)
            except requests.exceptions.Timeout:
                new_queue.append(data)
                logger.warn('REST timedout, will be repeated')
            except requests.exceptions.RequestException as e:
                self.queue.append(data)
                logger.warn('REST failed')
        
        self.queue = new_queue
        logger.info('REST sent')

