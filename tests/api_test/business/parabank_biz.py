"""ParaBank REST 服务封装。

特性：
- 底层 HTTP 自动重试（tenacity）
- 所有请求自动记录到 Allure 报告（请求 + 响应）
"""
import json

import allure
import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    retry_if_result,
    stop_after_attempt,
    wait_exponential,
)


# ==================== 重试策略 ====================

# 需要重试的网络异常
RETRYABLE_EXCEPTIONS = (
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
    requests.exceptions.ChunkedEncodingError,
)


def _is_server_error(resp):
    """5xx 视为可重试，4xx 不重试（避免幂等问题）。"""
    return 500 <= resp.status_code < 600


def _retry_decorator():
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=(
            retry_if_exception_type(RETRYABLE_EXCEPTIONS)
            | retry_if_result(_is_server_error)
        ),
        reraise=True,
    )


# ==================== Allure 附件 ====================

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


# ==================== 业务封装 ====================

class ParaBankBiz:
    """ParaBank REST 服务封装。

    base_url: http://localhost:8080/parabank/services/bank
    """

    def __init__(self, base_url, auth=None):
        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self.session = requests.Session()

        # Monkey-patch session.request，加 Allure 记录
        _orig_request = self.session.request

        def _wrapped(method, url, **kwargs):
            resp = _orig_request(method, url, **kwargs)
            _attach_to_allure(resp)
            return resp

        self.session.request = _wrapped

    # ==================== 底层（带重试） ====================

    @_retry_decorator()
    def _do_request(self, method, url, **kwargs):
        return self.session.request(method, url, **kwargs)

    def get(self, path, **kwargs):
        return self._do_request("GET", self.base_url + path, **kwargs)

    def post_query(self, path, params=None, **kwargs):
        """参数走 URL query string（@QueryParam 接口）"""
        return self._do_request(
            "POST", self.base_url + path, params=params, auth=self.auth, **kwargs
        )

    def post_json(self, path, params=None, json_data=None, **kwargs):
        """query + JSON body 混用（billpay）"""
        return self._do_request(
            "POST",
            self.base_url + path,
            params=params,
            json=json_data,
            auth=self.auth,
            headers={"Content-Type": "application/json"},
            **kwargs,
        )

    def post_form(self, path, form_data=None, **kwargs):
        """form 编码（保留给旧接口）"""
        return self._do_request(
            "POST", self.base_url + path, data=form_data, auth=self.auth, **kwargs
        )

    def post(self, path, json_data=None, **kwargs):
        """兼容旧调用"""
        return self.post_query(path, params=json_data, **kwargs)

    # ==================== 查询 ====================

    def get_customer_account_list(self, customer_id):
        url = f"{self.base_url}/customers/{customer_id}/accounts"
        return self.get(f"/customers/{customer_id}/accounts")

    def get_single_account_detail(self, account_id):
        return self.get(f"/accounts/{account_id}")

    def get_account_transactions(self, account_id):
        return self.get(f"/accounts/{account_id}/transactions")

    # ==================== 转账 ====================

    def transfer_funds(self, from_acc_id, to_acc_id, amount):
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
        return self.get(f"/login/{username}/{password}")

    def get_customer(self, customer_id):
        return self.get(f"/customers/{customer_id}")

    # ==================== 交易查询 ====================

    def get_transaction_by_id(self, tx_id):
        return self.get(f"/transactions/{tx_id}")

    def get_transactions_by_amount(self, account_id, amount):
        return self.get(f"/accounts/{account_id}/transactions/amount/{amount}")

    def get_transactions_by_month_type(self, account_id, month, type_):
        return self.get(
            f"/accounts/{account_id}/transactions/month/{month}/type/{type_}"
        )

    def get_transactions_by_date_range(self, account_id, from_date, to_date):
        return self.get(
            f"/accounts/{account_id}/transactions/fromDate/{from_date}/toDate/{to_date}"
        )