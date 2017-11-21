import logging
import smtplib
import requests
from email.mime.text import MIMEText
from config import logger
import config as cfg


class Notifier():
    data = {}
    database = None
    rest = None
    mailer = None

    def __init__(self, database):
        self.rest = Rest()
        self.mailer = Mailer()

        for addr in database.get_addresses():
            if not addr['coin'] in self.data:
                self.data[addr['coin']] = {}

            if not addr['hash'] in self.data[addr['coin']]:
                self.data[addr['coin']][addr['hash']] = {
                    'in': [],
                    'out': [],
                    'in_users': [],
                    'out_users': [],
                    'inout_users': [],
                }

            ptr = self.data[addr['coin']][addr['hash']]

            for type in ['in', 'out', 'inout']:
                ptr[type + '_users'] = database.get_address_users(addr['address_id'], type)

    def process_transaction(self, coin, tx):
        coin_name = str(coin)
        for type in ['in', 'out']:
            intersect = set(self.data[coin_name].keys()) & tx[type]

            for addr in intersect:
                self.data[coin_name][addr][type].append(tx['hash'])

    def notify(self, coin):
        coin_name = str(coin)
        for addr, addr_data in self.data[coin_name].items():

            # notify users with INOUT about IN and OUT tranasctions
            if addr_data['out'] or addr_data['in']:
                for user in addr_data['inout_users']: 
                    self.send(coin_name, user, addr, addr_data['out'] + addr_data['in'])

            if addr_data['out']:
                for user in addr_data['out_users']: 
                    self.send(coin_name, user, addr, addr_data['out'])

            if addr_data['in']:
                for user in addr_data['in_users']: 
                    self.send(coin_name, user, addr, addr_data['in'])

            addr_data['in'] = []
            addr_data['out'] = []

    def send(self, coin, user, addr, txs):
        logger.info("Notifying: {}: user {} about {}".format(coin, user, txs))

        if user['notify'] == 'email':
            self.mailer.send(user, addr, txs)
        elif user['notify'] == 'rest':
            self.rest.send(user, addr, txs)


class Sender():
    def send(self, user, addr, txs):
        raise NotImplementedError()

class Mailer(Sender):
    server = None

    def connect(self):
        self.server = smtplib.SMTP(cfg.SMTP['server'], cfg.SMTP['port'])
        self.server.starttls()
        self.server.login(cfg.SMTP['username'], cfg.SMTP['password'])

    def build_message(self, user, addr, txs):
        return "{} with name {} found in those transactions:\n{}".format(addr, user['name'], '\n'.join(txs))

    def send(self, user, addr, txs):
        msg = MIMEText(self.build_message(user, addr, txs))
        msg['Subject'] = cfg.MAIL['subject']
        msg['From'] = cfg.MAIL['from']
        msg['To'] = user['email']

        self.connect()
        self.server.sendmail(cfg.MAIL['from'], [user['email']], msg.as_string())
        self.server.quit()

class Rest(Sender):
    headers = {'content-type': 'application/json'}

    def build_message(self, user, addr, txs):
        return {
            'user': user['user_id'],
            'address': addr,
            'transactions': txs
            }

    def send(self, user, addr, txs):
        payload = self.build_message(user, addr, txs)
        requests.post(cfg.REST_URL, json=payload, headers=self.headers)

