import requests

class BaseApi:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    def get(self, path, params=None, **kwargs):
        """GET请求封装"""
        url = self.base_url + path
        resp = self.session.get(url, params=params, **kwargs)
        return resp

    def post(self, path, json_data=None, **kwargs):
        """POST请求封装，保留json_data入参，内部映射成requests的json参数"""
        url = self.base_url + path
        resp = self.session.post(url, json=json_data,** kwargs)
        return resp

    def put(self, path, json_data=None, **kwargs):
        """PUT请求封装"""
        url = self.base_url + path
        resp = self.session.put(url, json=json_data, **kwargs)
        return resp

    def delete(self, path, **kwargs):
        """DELETE请求封装"""
        url = self.base_url + path
        resp = self.session.delete(url,** kwargs)
        return resp
