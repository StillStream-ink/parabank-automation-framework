from tests.api_test.services.base_api import BaseApi

class ParaBankApi(BaseApi):
    def __init__(self, base_url):
        super().__init__(base_url)

    # 查询客户名下所有账户
    def get_customer_accounts(self, customer_id, auth):
        url = f"/customers/{customer_id}/accounts"
        # 如果auth不为空，放到params里传给底层请求
        kwargs = {}
        if auth:
            kwargs["auth"] = auth
        return self.get(url,** kwargs)

    # 查询单个账户详情
    def get_account_detail(self, account_id, auth):
        url = f"/accounts/{account_id}"
        kwargs = {}
        if auth:
            kwargs["auth"] = auth
        return self.get(url, **kwargs)

    # 查询账户交易流水
    def get_account_transactions(self, account_id, auth):
        url = f"/accounts/{account_id}/transactions"
        kwargs = {}
        if auth:
            kwargs["auth"] = auth
        return self.get(url,** kwargs)

    # 账户转账
    def transfer_funds(self, payload, auth):
        url = "/transfers"
        kwargs = {}
        if auth:
            kwargs["auth"] = auth
        return self.post(url, json=payload, **kwargs)
