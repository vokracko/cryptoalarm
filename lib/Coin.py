import requests
import json

class Coin():
    url = None
    block_time = None
    block = None

    def __init__(self, url):
        self.url = url

    def get_block_time(self):
        if not self.block_time:
            raise NotImplementedError
        
        return self.block_time

    def get_best_block_hash(self):
        raise NotImplementedError()

    def get_block(self, hash):
        raise NotImplementedError()

    def get_block_height(self):
        raise NotImplementedError()

    def get_parent_block_hash(self, hash = None):
        raise NotImplementedError()

    def get_block_transactions(self, hash):
        raise NotImplementedError()

    def get_transaction(self, hash):
        raise NotImplementedError()

    def get_transaction_io(self, hash):
        raise NotImplementedError()

    def rpc(self, method, *args, **kwargs):
        headers = {'content-type': 'application/json'}
        payload = {
            'jsonrpc': '2.0',
            'method': method,
            'params': [item for item in args],
            'id': 0,
        }

        # print(json.dumps(payload))
        response = requests.post(self.url, json=payload, headers=headers)
        # TODO error handling
        # print(response.json())
        return response.json()['result']

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.__class__.__name__
