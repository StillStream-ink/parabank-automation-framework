from tests.api_test.services.base_api import BaseApi

class LoanBiz:
    def __init__(self, client: BaseApi):
        self.client = client

    def apply_loan(self, customer_id:int, loan_amount:float, loan_term:int):
        payload = {
            "customer_id": customer_id,
            "loan_amount": loan_amount,
            "loan_term": loan_term
        }
        resp = self.client.post("/api/loan/apply", json_data=payload)
        return resp


class CustomerBiz:
    def __init__(self, client: BaseApi):
        self.client = client

    def register(self, name:str, age:int, income:int, credit_score:int):
        payload = {
            "name": name,
            "age": age,
            "income": income,
            "credit_score": credit_score
        }
        resp = self.client.post("/api/customer/register", json_data=payload)
        return resp
