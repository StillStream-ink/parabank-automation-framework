import requests


class BaseApi:
    """HTTP 请求封装（带默认超时）。"""

    DEFAULT_TIMEOUT = 15

    def __init__(self, base_url, auth=None, timeout=None):
        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.session = requests.Session()

    def _prepare(self, kwargs):
        kwargs.setdefault("timeout", self.timeout)
        if self.auth and "auth" not in kwargs:
            kwargs["auth"] = self.auth
        return kwargs

    def get(self, path, params=None, **kwargs):
        url = self.base_url + path
        return self.session.get(url, params=params, **self._prepare(kwargs))

    def post(self, path, json_data=None, **kwargs):
        url = self.base_url + path
        return self.session.post(url, json=json_data, **self._prepare(kwargs))

    def put(self, path, json_data=None, **kwargs):
        url = self.base_url + path
        return self.session.put(url, json=json_data, **self._prepare(kwargs))

    def delete(self, path, **kwargs):
        url = self.base_url + path
        return self.session.delete(url, **self._prepare(kwargs))
