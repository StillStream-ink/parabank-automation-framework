import allure
import pytest
import xml.etree.ElementTree as ET

from tests.api_test.business.parabank_biz import ParaBankBiz

BASE_URL = "http://localhost:8080/parabank/services/bank"
USER_JOHN = ("john", "demo")
ACCOUNT_ID = "54321"


pytestmark = [pytest.mark.api, pytest.mark.parabank, pytest.mark.deposit, pytest.mark.withdraw]

@allure.feature("ParaBank-存款/取款接口")
class TestDepositWithdraw:

    # ==================== 存款 ====================

    @pytest.mark.smoke
    @allure.story("存款-正常")
    @allure.title("TC_PB_DEP_001 正常存款 100 元")
    def test_deposit_normal(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.deposit(ACCOUNT_ID, 100)
        assert resp.status_code == 200
        assert "successfully deposited" in resp.text.lower()

    @pytest.mark.xfail(reason="BUG_201：/deposit 允许金额为 0，缺少参数校验")
    @allure.story("存款-边界")
    @allure.title("TC_PB_DEP_002 存款金额为 0")
    def test_deposit_amount_zero(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.deposit(ACCOUNT_ID, 0)
        assert resp.status_code != 200, "存款 0 元应被拒绝"

    @pytest.mark.xfail(reason="BUG_202 高危：/deposit 允许负数金额")
    @allure.story("存款-边界")
    @allure.title("TC_PB_DEP_003 存款金额为负")
    def test_deposit_amount_negative(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.deposit(ACCOUNT_ID, -100)
        assert resp.status_code != 200, "存款负数应被拒绝"

    @allure.story("存款-异常")
    @allure.title("TC_PB_DEP_004 存款到不存在的账户")
    def test_deposit_invalid_account(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.deposit("99999999", 100)
        assert resp.status_code != 200, "不存在的账户应被拒绝"

    # ==================== 取款 ====================

    @allure.story("取款-正常")
    @allure.title("TC_PB_WD_001 正常取款 10 元")
    def test_withdraw_normal(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        biz.deposit(ACCOUNT_ID, 100)
        resp = biz.withdraw(ACCOUNT_ID, 10)
        assert resp.status_code == 200
        assert "successfully withdrew" in resp.text.lower()

    @pytest.mark.xfail(reason="BUG_203 高危：/withdraw 未校验余额，允许透支")
    @allure.story("取款-异常")
    @allure.title("TC_PB_WD_002 取款金额超过余额")
    def test_withdraw_over_balance(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.withdraw(ACCOUNT_ID, 99999999)
        assert resp.status_code != 200, "取款超余额应被拒绝"

    @pytest.mark.xfail(reason="BUG_204 高危：/withdraw 允许负数金额")
    @allure.story("取款-边界")
    @allure.title("TC_PB_WD_003 取款金额为负")
    def test_withdraw_amount_negative(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.withdraw(ACCOUNT_ID, -50)
        assert resp.status_code != 200, "取款负数应被拒绝"

    @pytest.mark.xfail(reason="BUG_205：/withdraw 允许金额为 0，缺少参数校验")
    @allure.story("取款-边界")
    @allure.title("TC_PB_WD_004 取款金额为 0")
    def test_withdraw_amount_zero(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.withdraw(ACCOUNT_ID, 0)
        assert resp.status_code != 200, "取款 0 元应被拒绝"
