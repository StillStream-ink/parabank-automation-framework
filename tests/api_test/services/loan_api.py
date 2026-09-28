from tests.api_test.services.base_api import BaseApi

class LoanApi:
    def __init__(self, client):
        self.client = client

    def create_loan(self, customer_id, amount):
        payload = {"customer_id": customer_id, "amount": amount}
        return self.client.post("/loan", json_data=payload)

    def get_loan(self, loan_id):
        return self.client.get(f"/loan/{loan_id}")
