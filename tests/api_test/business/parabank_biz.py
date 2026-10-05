"""ParaBank REST 服务封装。

特性：
- 底层 HTTP 自动重试（tenacity）
- 所有请求自动记录到 Allure 报告（请求 + 响应）
- 所有公开方法带类型注解与 docstring
"""
from __future__ import annotations

import json
from typing import Any

import allure
import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    retry_if_result,
    stop_after_attempt,
    wait_exponential,
)


# 金额类型：支持数字或字符串（SQL 注入测试会传 str）
Amount = int | float | str


# ==================== 重试策略 ====================

# 需要重试的网络异常
RETRYABLE_EXCEPTIONS = (
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
    requests.exceptions.ChunkedEncodingError,
)


def _is_server_error(resp: requests.Response) -> bool:
    """5xx 视为可重试，4xx 不重试（避免幂等问题）。"""
    return 500 <= resp.status_code < 600


def _retry_decorator():
    """构造 tenacity 重试装饰器：网络异常或 5xx 时重试，最多 3 次。"""
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

def _attach_to_allure(resp: requests.Response) -> None:
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

    Args:
        base_url: REST 服务根地址，如 http://localhost:8080/parabank/services/bank
        auth: HTTP Basic 认证元组 (username, password)；None 表示不带认证
        timeout: 请求超时秒数；默认 15

    Attributes:
        base_url: 规范化后的服务地址（结尾无 /）
        auth: 认证元组
        timeout: 超时秒数
        session: requests.Session 实例（已挂 Allure 记录钩子）
    """

    DEFAULT_TIMEOUT: int = 15

    def __init__(
        self,
        base_url: str,
        auth: tuple[str, str] | None = None,
        timeout: int | None = None,
    ) -> None:
        self.base_url: str = base_url.rstrip("/")
        self.auth: tuple[str, str] | None = auth
        self.timeout: int = timeout or self.DEFAULT_TIMEOUT
        self.session: requests.Session = requests.Session()

        # Monkey-patch session.request，加 Allure 记录
        _orig_request = self.session.request

        def _wrapped(method: str, url: str, **kwargs: Any) -> requests.Response:
            resp = _orig_request(method, url, **kwargs)
            _attach_to_allure(resp)
            return resp

        self.session.request = _wrapped  # type: ignore[method-assign]

    # ==================== 底层（带重试） ====================

    @_retry_decorator()
    def _do_request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        """底层请求：统一注入 timeout，并应用重试策略。"""
        kwargs.setdefault("timeout", self.timeout)
        return self.session.request(method, url, **kwargs)

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        """GET 请求。"""
        return self._do_request("GET", self.base_url + path, **kwargs)

    def post_query(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """POST 请求：参数走 URL query string（@QueryParam 接口）。"""
        return self._do_request(
            "POST", self.base_url + path, params=params, auth=self.auth, **kwargs
        )

    def post_json(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """POST 请求：query + JSON body 混用（billpay）。"""
        return self._do_request(
            "POST",
            self.base_url + path,
            params=params,
            json=json_data,
            auth=self.auth,
            headers={"Content-Type": "application/json"},
            **kwargs,
        )

    def post_form(
        self,
        path: str,
        form_data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """POST 请求：form 编码（保留给旧接口）。"""
        return self._do_request(
            "POST", self.base_url + path, data=form_data, auth=self.auth, **kwargs
        )

    def post(
        self,
        path: str,
        json_data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """兼容旧调用：转发到 post_query。"""
        return self.post_query(path, params=json_data, **kwargs)

    # ==================== 查询 ====================

    def get_customer_account_list(self, customer_id: str) -> requests.Response:
        """查询指定客户名下的所有账户。

        Args:
            customer_id: 客户 ID（字符串）
        """
        return self.get(f"/customers/{customer_id}/accounts")

    def get_single_account_detail(self, account_id: str) -> requests.Response:
        """查询单个账户详情。

        Args:
            account_id: 账户 ID（字符串）
        """
        return self.get(f"/accounts/{account_id}")

    def get_account_transactions(self, account_id: str) -> requests.Response:
        """查询账户的所有交易记录。

        Args:
            account_id: 账户 ID（字符串）
        """
        return self.get(f"/accounts/{account_id}/transactions")

    # ==================== 转账 ====================

    def transfer_funds(
        self,
        from_acc_id: str,
        to_acc_id: str,
        amount: Amount,
    ) -> requests.Response:
        """账户间转账。

        Args:
            from_acc_id: 转出账户 ID
            to_acc_id: 转入账户 ID
            amount: 转账金额（正数）
        """
        params = {
            "fromAccountId": from_acc_id,
            "toAccountId": to_acc_id,
            "amount": amount,
        }
        return self.post_query("/transfer", params=params)

    # ==================== 开户 ====================

    def open_new_account(
        self,
        customer_id: str,
        account_type: int,
        from_account_id: str,
    ) -> requests.Response:
        """开立新账户。

        Args:
            customer_id: 客户 ID
            account_type: 0=CHECKING，1=SAVINGS
            from_account_id: 资金来源账户 ID
        """
        params = {
            "customerId": customer_id,
            "newAccountType": account_type,
            "fromAccountId": from_account_id,
        }
        return self.post_query("/createAccount", params=params)

    # ==================== 账单支付 ====================

    def pay_bill(
        self,
        account_id: str,
        amount: Amount,
        payee_name: str = "TestPayee",
    ) -> requests.Response:
        """支付账单。

        Args:
            account_id: 付款账户 ID
            amount: 支付金额
            payee_name: 收款人名称（默认 TestPayee）
        """
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

    def apply_loan(
        self,
        customer_id: str,
        amount: Amount,
        down_payment: Amount,
        from_account_id: str,
    ) -> requests.Response:
        """申请贷款。

        Args:
            customer_id: 客户 ID
            amount: 贷款金额
            down_payment: 首付金额
            from_account_id: 资金来源账户 ID
        """
        params = {
            "customerId": customer_id,
            "amount": amount,
            "downPayment": down_payment,
            "fromAccountId": from_account_id,
        }
        return self.post_query("/requestLoan", params=params)

    # ==================== 存款 / 取款 ====================

    def deposit(self, account_id: str, amount: Amount) -> requests.Response:
        """存款。

        Args:
            account_id: 账户 ID
            amount: 存款金额（正数）
        """
        params = {"accountId": account_id, "amount": amount}
        return self.post_query("/deposit", params=params)

    def withdraw(self, account_id: str, amount: Amount) -> requests.Response:
        """取款。

        Args:
            account_id: 账户 ID
            amount: 取款金额（正数）
        """
        params = {"accountId": account_id, "amount": amount}
        return self.post_query("/withdraw", params=params)

    # ==================== 登录 / 客户信息 ====================

    def login(self, username: str, password: str) -> requests.Response:
        """登录校验。

        Args:
            username: 用户名
            password: 密码
        """
        return self.get(f"/login/{username}/{password}")

    def get_customer(self, customer_id: str) -> requests.Response:
        """查询客户信息。

        Args:
            customer_id: 客户 ID
        """
        return self.get(f"/customers/{customer_id}")

    # ==================== 交易查询 ====================

    def get_transaction_by_id(self, tx_id: str) -> requests.Response:
        """按交易 ID 查询交易。

        Args:
            tx_id: 交易 ID
        """
        return self.get(f"/transactions/{tx_id}")

    def get_transactions_by_amount(
        self,
        account_id: str,
        amount: Amount,
    ) -> requests.Response:
        """按金额查询账户交易。

        Args:
            account_id: 账户 ID
            amount: 目标金额
        """
        return self.get(f"/accounts/{account_id}/transactions/amount/{amount}")

    def get_transactions_by_month_type(
        self,
        account_id: str,
        month: str,
        type_: str,
    ) -> requests.Response:
        """按月份 + 类型查询交易。

        Args:
            account_id: 账户 ID
            month: 月份（如 "All" 或 "January"）
            type_: 交易类型（如 "All" 或 "Credit"）
        """
        return self.get(
            f"/accounts/{account_id}/transactions/month/{month}/type/{type_}"
        )

    def get_transactions_by_date_range(
        self,
        account_id: str,
        from_date: str,
        to_date: str,
    ) -> requests.Response:
        """按日期区间查询交易。

        Args:
            account_id: 账户 ID
            from_date: 起始日期（MM-DD-YYYY）
            to_date: 结束日期（MM-DD-YYYY）
        """
        return self.get(
            f"/accounts/{account_id}/transactions/fromDate/{from_date}/toDate/{to_date}"
        )

    

# ==================== 裸客户端（异常测试专用） ====================

class ParaBankRaw:
    """ParaBank 裸客户端：无重试、无 Allure 记录。

    专供异常测试使用，避免：
    - tenacity 对 5xx 自动重试 3 次（浪费 3-15 秒/用例）
    - 每个异常请求都被附加到 Allure 报告（报告冗余）
    """

    DEFAULT_TIMEOUT: int = 10

    def __init__(
        self,
        base_url: str,
        auth: tuple[str, str] | None = None,
        timeout: int | None = None,
    ) -> None:
        self.base_url: str = base_url.rstrip("/")
        self.auth: tuple[str, str] | None = auth
        self.timeout: int = timeout or self.DEFAULT_TIMEOUT

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        """GET 请求（无重试、无 Allure 记录）。"""
        kwargs.setdefault("timeout", self.timeout)
        kwargs.setdefault("auth", self.auth)
        return requests.get(self.base_url + path, **kwargs)

    def post_query(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """POST 请求：参数走 query string（无重试、无 Allure 记录）。"""
        kwargs.setdefault("timeout", self.timeout)
        kwargs.setdefault("auth", self.auth)
        return requests.post(self.base_url + path, params=params, **kwargs)