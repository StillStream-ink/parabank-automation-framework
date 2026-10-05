"""异常场景测试  非法参数/缺失参数/错误方法/特殊字符/超大数值。

基于 logs/exception_probe.txt 的真实响应设计。

说明：异常场景统一走 ParaBankRaw（无重试、无 Allure），避免 tenacity 干扰。
"""
from config.test_constants import BASE_URL, USER_JOHN, CUSTOMER_ID_JOHN, ACC_A, ACC_B

import pytest
import allure

from tests.api_test.business.parabank_biz import ParaBankBiz, ParaBankRaw


pytestmark = [pytest.mark.api, pytest.mark.parabank, pytest.mark.regression]


# ==================== 转账-缺失参数 ====================

@allure.feature("异常场景-转账参数校验")
class TestTransferInvalidParams:

    @allure.story("缺失必填参数")
    @allure.title("TC_EX_TX_001 缺 fromAccountId 应返回 4xx")
    def test_transfer_missing_from_account(self):
        raw = ParaBankRaw(BASE_URL, USER_JOHN)
        resp = raw.post_query("/transfer", params={"toAccountId": "12456", "amount": 10})
        assert 400 <= resp.status_code < 500

    @pytest.mark.xfail(reason="BUG_301：/transfer 缺 amount 参数返回 500（应 4xx）")
    @allure.story("缺失必填参数")
    @allure.title("TC_EX_TX_002 缺 amount 应返回 4xx（当前 500）")
    def test_transfer_missing_amount_returns_4xx(self):
        raw = ParaBankRaw(BASE_URL, USER_JOHN)
        resp = raw.post_query("/transfer", params={
            "fromAccountId": "12345", "toAccountId": "12456"
        })
        assert resp.status_code < 500, f"应 4xx，实际 {resp.status_code}"

    @pytest.mark.xfail(reason="BUG_302：/transfer amount 空字符串返回 500（应 4xx）")
    @allure.story("非法参数值")
    @allure.title("TC_EX_TX_003 amount 传空串应返回 4xx（当前 500）")
    def test_transfer_empty_amount_returns_4xx(self):
        raw = ParaBankRaw(BASE_URL, USER_JOHN)
        resp = raw.post_query("/transfer", params={
            "fromAccountId": "12345", "toAccountId": "12456", "amount": ""
        })
        assert resp.status_code < 500, f"应 4xx，实际 {resp.status_code}"

    @allure.story("非法参数值")
    @allure.title("TC_EX_TX_004 fromAccountId=-1 应返回 4xx")
    def test_transfer_negative_account_id(self):
        raw = ParaBankRaw(BASE_URL, USER_JOHN)
        resp = raw.post_query("/transfer", params={
            "fromAccountId": -1, "toAccountId": "12456", "amount": 10
        })
        assert 400 <= resp.status_code < 500

    @allure.story("非法参数值")
    @allure.title("TC_EX_TX_005 全缺参数应返回 4xx")
    def test_transfer_all_params_missing(self):
        raw = ParaBankRaw(BASE_URL, USER_JOHN)
        resp = raw.post_query("/transfer", params={})
        assert 400 <= resp.status_code < 500


# ==================== 转账-特殊字符 / 注入 ====================

@allure.feature("异常场景-转账特殊字符")
class TestTransferSpecialChars:

    @pytest.mark.parametrize("bad_amount,desc", [
        ("abc", "字符串"),
        ("100 or 1=1 --", "SQL 注入"),
        ("<script>alert(1)</script>", "XSS"),
        ("一百", "中文"),
    ])
    def test_transfer_special_chars_rejected(self, bad_amount, desc):
        """特殊字符应被拒绝（4xx）"""
        raw = ParaBankRaw(BASE_URL, USER_JOHN)
        resp = raw.post_query("/transfer", params={
            "fromAccountId": "12345", "toAccountId": "12456", "amount": bad_amount
        })
        assert 400 <= resp.status_code < 500, \
            f"amount={desc} 应 4xx，实际 {resp.status_code}"

    def test_transfer_overlong_string(self):
        """超长数字串应被拒绝"""
        raw = ParaBankRaw(BASE_URL, USER_JOHN)
        resp = raw.post_query("/transfer", params={
            "fromAccountId": "12345", "toAccountId": "12456", "amount": "9" * 1000
        })
        assert 400 <= resp.status_code < 500


# ==================== 协议层异常 ====================

@allure.feature("异常场景-协议层")
class TestProtocolExceptions:

    def test_get_on_transfer_returns_405(self):
        """用 GET 调 POST 接口应返回 405"""
        raw = ParaBankRaw(BASE_URL, USER_JOHN)
        resp = raw.get("/transfer")
        assert resp.status_code == 405

    def test_get_on_deposit_returns_405(self):
        raw = ParaBankRaw(BASE_URL, USER_JOHN)
        resp = raw.get("/deposit")
        assert resp.status_code == 405

    def test_unknown_path_returns_404(self):
        """访问不存在的路径应返回 404"""
        raw = ParaBankRaw(BASE_URL, USER_JOHN)
        resp = raw.get("/no_such_endpoint")
        assert resp.status_code == 404

    def test_unknown_account_returns_4xx(self):
        """访问不存在的账户应返回 4xx"""
        raw = ParaBankRaw(BASE_URL, USER_JOHN)
        resp = raw.get("/accounts/99999999")
        assert 400 <= resp.status_code < 500


# ==================== 存款-超大 / 非法数值 ====================

@allure.feature("异常场景-存款数值异常")
class TestDepositNumericExceptions:

    def test_deposit_huge_number_rejected(self):
        """1e100 超大数应被拒绝"""
        raw = ParaBankRaw(BASE_URL, USER_JOHN)
        resp = raw.post_query("/deposit", params={"accountId": ACC_A, "amount": "1e100"})
        assert 400 <= resp.status_code < 500

    @pytest.mark.parametrize("bad_value,desc", [
        ("NaN", "NaN"),
        ("Infinity", "无穷大"),
    ])
    def test_deposit_special_float_rejected(self, bad_value, desc):
        """NaN / Infinity 应被拒绝"""
        raw = ParaBankRaw(BASE_URL, USER_JOHN)
        resp = raw.post_query("/deposit", params={"accountId": ACC_A, "amount": bad_value})
        assert 400 <= resp.status_code < 500, \
            f"deposit amount={desc} 应 4xx，实际 {resp.status_code}"