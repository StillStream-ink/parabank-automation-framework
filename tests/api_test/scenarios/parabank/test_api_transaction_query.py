import xml.etree.ElementTree as ET

import allure
import pytest

from config.test_constants import ACC_A, BASE_URL, USER_JOHN
from tests.api_test.business.parabank_biz import ParaBankBiz

ACCOUNT_ID = ACC_A

def _get_first_tx_id(biz, account_id=ACCOUNT_ID):
    """从账户交易流水中取第一个交易 ID。"""
    resp = biz.get_account_transactions(account_id)
    root = ET.fromstring(resp.text)
    tx = root.find("transaction")
    return tx.find("id").text if tx is not None else None

pytestmark = [pytest.mark.api, pytest.mark.parabank, pytest.mark.transaction]

@allure.feature("ParaBank-交易查询接口")
class TestTransactionQuery:

    # ==================== 按 ID 查询 ====================

    @allure.story("交易查询-按 ID")
    @allure.title("TC_PB_TXQ_001 按 ID 查询存在的交易")
    def test_get_transaction_by_id(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        tx_id = _get_first_tx_id(biz)
        assert tx_id, "账户没有交易记录，无法测试"

        resp = biz.get_transaction_by_id(tx_id)
        assert resp.status_code == 200
        root = ET.fromstring(resp.text)
        assert root.find("id").text == tx_id

    @allure.story("交易查询-按 ID")
    @allure.title("TC_PB_TXQ_002 按 ID 查询不存在的交易")
    def test_get_transaction_by_invalid_id(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_transaction_by_id("99999999")
        assert resp.status_code != 200, "不存在的交易应返回 4xx"

    # ==================== 按金额查询 ====================

    @allure.story("交易查询-按金额")
    @allure.title("TC_PB_TXQ_003 按金额查询交易")
    def test_get_transactions_by_amount(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        # 查一个不太可能存在的金额，验证接口可用（返回空列表也是正常）
        resp = biz.get_transactions_by_amount(account_id=ACCOUNT_ID, amount=100)
        assert resp.status_code == 200
        assert "<transactions>" in resp.text

    # ==================== 按月份+类型查询 ====================

    @allure.story("交易查询-按月+类型")
    @allure.title("TC_PB_TXQ_004 按月份+类型查询（All/All）")
    def test_get_transactions_by_month_type(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_transactions_by_month_type(
            account_id=ACCOUNT_ID, month="All", type_="All"
        )
        assert resp.status_code == 200
        assert "<transactions>" in resp.text

    # ==================== 按日期区间查询 ====================

    @allure.story("交易查询-按日期区间")
    @allure.title("TC_PB_TXQ_005 按日期区间查询")
    def test_get_transactions_by_date_range(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_transactions_by_date_range(
            account_id=ACCOUNT_ID, from_date="01-01-2000", to_date="12-31-2030"
        )
        assert resp.status_code == 200
        assert "<transactions>" in resp.text

    # ==================== 安全 ====================

    @pytest.mark.xfail(reason="BUG_005 高危：交易查询接口未授权访问")
    @allure.story("交易查询-安全")
    @allure.title("TC_PB_TXQ_006 未授权查询交易")
    def test_get_transactions_no_auth(self):
        biz = ParaBankBiz(BASE_URL, auth=None)
        resp = biz.get_account_transactions(ACCOUNT_ID)
        assert resp.status_code in (401, 403), "未授权应被拒绝"

    @pytest.mark.xfail(reason="BUG_004 高危：交易查询水平越权")
    @allure.story("交易查询-安全")
    @allure.title("TC_PB_TXQ_007 查询他人账户交易-水平越权")
    def test_get_transactions_horizontal_privilege(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        # 用 john 的身份查一个不属于他的账户
        resp = biz.get_account_transactions("99999999")
        assert resp.status_code in (401, 403, 404), "越权查询应被拒绝"
