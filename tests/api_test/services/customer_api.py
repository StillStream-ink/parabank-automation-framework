from tests.api_test.services.base_api import BaseApi

class CustomerApi:
    def __init__(self, client):
        self.client = client

    def create_customer(self, name):
        payload = {"name": name}
        return self.client.post("/customer", json_data=payload)
