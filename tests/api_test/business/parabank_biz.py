import json

import allure
import requests




def _attach_to_allure(resp):
    """把请求/响应记录到 Allure 报告。"""
    try:
        req = resp.request
        req_info = f"{req.method} {req.url}"
        if req.body:
            body = req.body if isinstance(req.body, str) else str(req.body)
            req_info += f"\n\n{body[:2000]}"
        allure.attach(req_info, name="请求", attachment_type=allure.attachment_type.TEXT)

        resp_info = f"HTTP {resp.status_code}"
        if resp.text:
            resp_info += f"\n\n{resp.text[:3000]}"
        allure.attach(resp_info, name="响应", attachment_type=allure.attachment_type.TEXT)
    except Exception:
        pass


class ParaBankBiz:
    """ParaBank REST 服务封装。

    base_url: http://localhost:8080/parabank/services/bank
    """

    def __init__(self, base_url, auth=None):
        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self.session = requests.Session()
        # 让所有请求自动记录到 Allure
        _orig_request = self.session.request
        def _wrapped(method, url, **kwargs):
            resp = _orig_request(method, url, **kwargs)
            _attach_to_allure(resp)
            return resp
        self.session.request = _wrapped

    # ==================== 底层 ====================

    def post_query(self, path, params=None, **kwargs):
        """参数走 URL query string（@QueryParam 接口）"""
        url = self.base_url + path
        return self.session.post(url, params=params, auth=self.auth, **kwargs)

    def post_json(self, path, params=None, json_data=None, **kwargs):
        """query + JSON body 混用（billpay）"""
        url = self.base_url + path
        return self.session.post(
            url,
            params=params,
            json=json_data,
            auth=self.auth,
            headers={"Content-Type": "application/json"},
            **kwargs,
        )

    def post_form(self, path, form_data=None, **kwargs):
        """form 编码（保留给旧接口）"""
        url = self.base_url + path
        return self.session.post(url, data=form_data, auth=self.auth, **kwargs)

    def post(self, path, json_data=None, **kwargs):
        """兼容旧调用"""
        return self.post_query(path, params=json_data, **kwargs)

    # ==================== 查询 ====================

    def get_customer_account_list(self, customer_id):
        url = f"{self.base_url}/customers/{customer_id}/accounts"
        return self.session.get(url, auth=self.auth)

    def get_single_account_detail(self, account_id):
        url = f"{self.base_url}/accounts/{account_id}"
        return self.session.get(url, auth=self.auth)

    def get_account_transactions(self, account_id):
        url = f"{self.base_url}/accounts/{account_id}/transactions"
        return self.session.get(url, auth=self.auth)

    # ==================== 转账 ====================

    def transfer_funds(self, from_acc_id, to_acc_id, amount):
        """ParaBank /transfer 用 @QueryParam，参数必须放 URL query string。"""
        params = {
            "fromAccountId": from_acc_id,
            "toAccountId": to_acc_id,
            "amount": amount,
        }
        return self.post_query("/transfer", params=params)

    # ==================== 开户 ====================

    def open_new_account(self, customer_id, account_type, from_account_id):
        """account_type: 0=CHECKING, 1=SAVINGS"""
        params = {
            "customerId": customer_id,
            "newAccountType": account_type,
            "fromAccountId": from_account_id,
        }
        return self.post_query("/createAccount", params=params)

    # ==================== 账单支付 ====================

    def pay_bill(self, account_id, amount, payee_name="TestPayee"):
        params = {"accountId": account_id, "amount": amount}
        payee = {
            "name": payee_name,
            "address": {
                "street": "123 Main St",
                "city": "San Francisco",
                "state": "CA",
                "zipCode": "94105",
            },
            "phoneNumber": "415-555-0100",
        }
        return self.post_json("/billpay", params=params, json_data=payee)

    # ==================== 贷款 ====================

    def apply_loan(self, customer_id, amount, down_payment, from_account_id):
        params = {
            "customerId": customer_id,
            "amount": amount,
            "downPayment": down_payment,
            "fromAccountId": from_account_id,
        }
        return self.post_query("/requestLoan", params=params)

    # ==================== 存款 / 取款 ====================

    def deposit(self, account_id, amount):
        params = {"accountId": account_id, "amount": amount}
        return self.post_query("/deposit", params=params)

    def withdraw(self, account_id, amount):
        params = {"accountId": account_id, "amount": amount}
        return self.post_query("/withdraw", params=params)

    # ==================== 登录 / 客户信息 ====================

    def login(self, username, password):
        url = f"{self.base_url}/login/{username}/{password}"
        return self.session.get(url, auth=self.auth)

    def get_customer(self, customer_id):
        url = f"{self.base_url}/customers/{customer_id}"
        return self.session.get(url, auth=self.auth)

    # ==================== 交易查询 ====================

    def get_transaction_by_id(self, tx_id):
        url = f"{self.base_url}/transactions/{tx_id}"
        return self.session.get(url, auth=self.auth)

    def get_transactions_by_amount(self, account_id, amount):
        url = f"{self.base_url}/accounts/{account_id}/transactions/amount/{amount}"
        return self.session.get(url, auth=self.auth)

    def get_transactions_by_month_type(self, account_id, month, type_):
        url = f"{self.base_url}/accounts/{account_id}/transactions/month/{month}/type/{type_}"
        return self.session.get(url, auth=self.auth)

    def get_transactions_by_date_range(self, account_id, from_date, to_date):
        url = f"{self.base_url}/accounts/{account_id}/transactions/fromDate/{from_date}/toDate/{to_date}"
        return self.session.get(url, auth=self.auth)