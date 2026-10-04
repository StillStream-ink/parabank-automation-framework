
from config.test_constants import BASE_URL, USER_JOHN, CUSTOMER_ID_JOHN, ACC_A, ACC_B
"""转账/存款/取款 边界值参数化用例（精简版）。

精简原则：每个参数值代表一个独立风险类别。
- 正常值：0.01（精度）+ 1（最小正数）
- 边界值：0（零值缺失）
- 异常值：大额（透支）+ 负数（反向操作）
"""
import pytest
import allure
import xml.etree.ElementTree as ET

from tests.api_test.business.parabank_biz import ParaBankBiz

def _two_accounts(biz):
    resp = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
    root = ET.fromstring(resp.text)
    acc_list = root.findall("account")
    return acc_list[0].find("id").text, acc_list[1].find("id").text

# ============================================================
# 转账
# ============================================================
pytestmark = [pytest.mark.api, pytest.mark.parabank, pytest.mark.regression]

@allure.feature("转账-参数化边界")
class TestTransferParam:

    @pytest.mark.parametrize("amount", [
        pytest.param(0.01, id="precision"),
        pytest.param(1, id="min-amount"),
    ])
    def test_transfer_valid_amount(self, amount):
        """合法正数金额转账应成功"""
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        from_acc, to_acc = _two_accounts(biz)
        resp = biz.transfer_funds(from_acc, to_acc, amount)
        assert resp.status_code == 200
        assert "successfully transferred" in resp.text.lower()

    @pytest.mark.parametrize("amount", [
        pytest.param(0, id="zero", marks=pytest.mark.xfail(reason="BUG_101：/transfer 允许金额为 0")),
        pytest.param(999999999, id="over-limit", marks=pytest.mark.xfail(reason="BUG_103：/transfer 允许透支")),
    ])
    def test_transfer_invalid_amount(self, amount):
        """非法金额应被拒绝"""
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        from_acc, to_acc = _two_accounts(biz)
        resp = biz.transfer_funds(from_acc, to_acc, amount)
        assert resp.status_code != 200, f"非法金额 {amount} 应被拒绝，实际 HTTP {resp.status_code}"

    @pytest.mark.parametrize("amount", [
        pytest.param(-1, id="negative", marks=pytest.mark.xfail(reason="BUG_102：/transfer 允许负数金额")),
    ])
    def test_transfer_negative_amount(self, amount):
        """负数金额应被拒绝"""
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        from_acc, to_acc = _two_accounts(biz)
        resp = biz.transfer_funds(from_acc, to_acc, amount)
        assert resp.status_code != 200

# ============================================================
# 存款
# ============================================================
@allure.feature("存款-参数化边界")
class TestDepositParam:

    @pytest.mark.parametrize("amount", [
        pytest.param(0.01, id="precision"),
        pytest.param(100, id="normal"),
    ])
    def test_deposit_valid_amount(self, amount):
        """合法金额存款应成功（存款无上限）"""
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.deposit(ACC_A, amount)
        assert resp.status_code == 200
        assert "successfully deposited" in resp.text.lower()

    @pytest.mark.parametrize("amount", [
        pytest.param(0, id="zero", marks=pytest.mark.xfail(reason="BUG_201：/deposit 允许金额为 0")),
    ])
    def test_deposit_zero(self, amount):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.deposit(ACC_A, amount)
        assert resp.status_code != 200

    @pytest.mark.parametrize("amount", [
        pytest.param(-1, id="negative", marks=pytest.mark.xfail(reason="BUG_202：/deposit 允许负数金额")),
    ])
    def test_deposit_negative_amount(self, amount):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.deposit(ACC_A, amount)
        assert resp.status_code != 200

# ============================================================
# 取款
# ============================================================
@allure.feature("取款-参数化边界")
class TestWithdrawParam:

    @pytest.mark.parametrize("amount", [
        pytest.param(0.01, id="precision"),
        pytest.param(100, id="normal"),
    ])
    def test_withdraw_valid_amount(self, amount):
        """合法小金额取款应成功（先存款保证余额充足）"""
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        biz.deposit(ACC_A, 100)
        resp = biz.withdraw(ACC_A, amount)
        assert resp.status_code == 200
        assert "successfully withdrew" in resp.text.lower()

    @pytest.mark.parametrize("amount", [
        pytest.param(0, id="zero", marks=pytest.mark.xfail(reason="BUG_205：/withdraw 允许金额为 0")),
        pytest.param(999999999, id="over-balance", marks=pytest.mark.xfail(reason="BUG_203：/withdraw 允许透支")),
    ])
    def test_withdraw_invalid_amount(self, amount):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.withdraw(ACC_A, amount)
        assert resp.status_code != 200

    @pytest.mark.parametrize("amount", [
        pytest.param(-1, id="negative", marks=pytest.mark.xfail(reason="BUG_204：/withdraw 允许负数金额")),
    ])
    def test_withdraw_negative_amount(self, amount):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.withdraw(ACC_A, amount)
        assert resp.status_code != 200