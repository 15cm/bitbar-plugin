import json
from urllib import request

class Aria2:
    def __init__(self, host, port, secret = None):
        self.url = "http://%s:%d/jsonrpc" % (host, port)
        self.secret = secret

    def call(self, method, params = None):
        if params and type(params) != list:
            raise Exception('Params should be a list')
        data_dict = {
            'jsonrpc': '2.0',
            'id': '15cm',
            'method': 'aria2.%s' % method
        }
        if self.secret:
            data_dict['params'] = ['token:%s' % self.secret]
            if params:
                data_dict['params'].extend(params)
        else:
            data_dict['params'] = params
        data = json.dumps(data_dict).encode('utf-8')
        res = ''
        with request.urlopen(self.url, data) as req:
            res = json.loads(req.read().decode('utf-8'))['result']
        return res
    def getGlobalStat(self):
        return self.call('getGlobalStat')

    def tellActive(self):
        return self.call('tellActive')

    def tellWaiting(self):
        return self.call('tellWaiting', [-1, 10])

    def tellStopped(self):
        return self.call('tellStopped', [-1, 10])
