
from config.test_constants import BASE_URL, USER_JOHN, CUSTOMER_ID_JOHN, ACC_A, ACC_B
"""数据一致性测试  精确校验余额变化。

基于 logs/balance_consistency_probe.txt 的真实行为设计。
断言核心：转账/存款/取款前后余额的 delta 是否符合预期。

报告展示：每个用例用 allure.step 拆解为可读步骤。
"""
from decimal import Decimal

import allure
import pytest
import xml.etree.ElementTree as ET

from tests.api_test.business.parabank_biz import ParaBankBiz

# ==================== 辅助 ====================

def _get_balance(biz, account_id):
    with allure.step(f"查询账户 {account_id} 余额"):
        resp = biz.get_single_account_detail(account_id)
        assert resp.status_code == 200, f"查询账户 {account_id} 失败"
        root = ET.fromstring(resp.text)
        return Decimal(root.find("balance").text)

def _assert_delta(biz, account_id, before, expected_delta):
    with allure.step(
        f"校验账户 {account_id} 余额变化：期望 delta = {expected_delta}"
    ):
        after = _get_balance(biz, account_id)
        actual = after - before
        expected = Decimal(str(expected_delta))
        assert actual == expected, (
            f"账户 {account_id} 余额变化不符："
            f"起始 {before} -> 结束 {after}（delta={actual}），期望 delta={expected}"
        )
        allure.attach(
            f"起始余额: {before}\n"
            f"结束余额: {after}\n"
            f"实际变化: {actual}\n"
            f"预期变化: {expected}",
            name=f"账户 {account_id} 余额变化",
            attachment_type=allure.attachment_type.TEXT,
        )

# ==================== 转账一致性 ====================

pytestmark = [pytest.mark.api, pytest.mark.parabank, pytest.mark.p0]

@allure.feature("数据一致性-转账")
class TestTransferConsistency:

    @pytest.mark.smoke
    @allure.story("正常转账")
    @allure.title("TC_DC_TX_001 转账 100：转出方 -100、接收方 +100")
    def test_transfer_normal_balance(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)

        with allure.step("1. 记录转账前双方余额"):
            before_a = _get_balance(biz, ACC_A)
            before_b = _get_balance(biz, ACC_B)

        with allure.step(f"2. 从 {ACC_A} 转账 100 到 {ACC_B}"):
            resp = biz.transfer_funds(ACC_A, ACC_B, 100)
            assert resp.status_code == 200, "转账接口返回非 200"
            allure.attach(resp.text, "转账响应",
                          attachment_type=allure.attachment_type.TEXT)

        with allure.step("3. 校验转出方余额 -100"):
            _assert_delta(biz, ACC_A, before_a, -100)

        with allure.step("4. 校验接收方余额 +100"):
            _assert_delta(biz, ACC_B, before_b, +100)

    @allure.story("正常转账")
    @allure.title("TC_DC_TX_002 转账 0.01：精度精确到分")
    def test_transfer_small_amount_precision(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)

        with allure.step("1. 记录转账前双方余额"):
            before_a = _get_balance(biz, ACC_A)
            before_b = _get_balance(biz, ACC_B)

        with allure.step(f"2. 从 {ACC_A} 转账 0.01 到 {ACC_B}"):
            resp = biz.transfer_funds(ACC_A, ACC_B, 0.01)
            assert resp.status_code == 200

        with allure.step("3. 校验 0.01 精度未丢失"):
            _assert_delta(biz, ACC_A, before_a, -0.01)
            _assert_delta(biz, ACC_B, before_b, 0.01)

    @pytest.mark.xfail(reason="BUG_101：/transfer 允许 0 元转账返回 200，应拒绝")
    @allure.story("边界-零值")
    @allure.title("TC_DC_TX_003 转账 0 元应被拒绝且余额不变")
    def test_transfer_zero_should_reject(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)

        with allure.step("1. 记录转账前余额"):
            before_a = _get_balance(biz, ACC_A)

        with allure.step("2. 尝试转账 0 元"):
            resp = biz.transfer_funds(ACC_A, ACC_B, 0)

        with allure.step("3. 断言：0 元应被拒绝"):
            assert resp.status_code != 200, "0 元转账应被拒绝"

        with allure.step("4. 断言：余额未变"):
            _assert_delta(biz, ACC_A, before_a, 0)

    @pytest.mark.xfail(reason="BUG_102：/transfer 允许负数金额，导致反向转账")
    @allure.story("边界-负数")
    @allure.title("TC_DC_TX_004 转账 -100：不得反向改变余额")
    def test_transfer_negative_no_reverse(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)

        with allure.step("1. 记录转账前双方余额"):
            before_a = _get_balance(biz, ACC_A)
            before_b = _get_balance(biz, ACC_B)

        with allure.step("2. 尝试转账 -100 元（负数）"):
            resp = biz.transfer_funds(ACC_A, ACC_B, -100)

        with allure.step("3. 断言：负数应被拒绝"):
            assert resp.status_code != 200, "负数转账应被拒绝"

        with allure.step("4. 断言：双方余额不变"):
            _assert_delta(biz, ACC_A, before_a, 0)
            _assert_delta(biz, ACC_B, before_b, 0)

    @pytest.mark.xfail(reason="BUG_103：/transfer 允许透支，导致转出方余额变负")
    @allure.story("边界-超额")
    @allure.title("TC_DC_TX_005 转账 999999999：不得造成透支")
    def test_transfer_over_balance_no_overdraft(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)

        with allure.step("1. 记录转账前余额"):
            before_a = _get_balance(biz, ACC_A)

        with allure.step("2. 尝试转账 999999999 元（超额）"):
            resp = biz.transfer_funds(ACC_A, ACC_B, 999999999)

        with allure.step("3. 断言：超额应被拒绝"):
            assert resp.status_code != 200, "超额转账应被拒绝"

        with allure.step("4. 断言：余额未变"):
            _assert_delta(biz, ACC_A, before_a, 0)

    @pytest.mark.xfail(reason="BUG_104：/transfer 允许自己转自己返回 200，应拒绝")
    @allure.story("边界-同账户")
    @allure.title("TC_DC_TX_006 自己转自己：应被拒绝且余额不变")
    def test_transfer_self_should_reject(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)

        with allure.step("1. 记录转账前余额"):
            before_a = _get_balance(biz, ACC_A)

        with allure.step(f"2. 尝试从 {ACC_A} 转到 {ACC_A}（同账户）"):
            resp = biz.transfer_funds(ACC_A, ACC_A, 100)

        with allure.step("3. 断言：同账户转账应被拒绝"):
            assert resp.status_code != 200, "同账户转账应被拒绝"

        with allure.step("4. 断言：余额未变"):
            _assert_delta(biz, ACC_A, before_a, 0)

# ==================== 存款一致性 ====================

@allure.feature("数据一致性-存款")
class TestDepositConsistency:

    @allure.story("正常存款")
    @allure.title("TC_DC_DEP_001 存款 100：余额 +100")
    def test_deposit_normal_balance(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)

        with allure.step("1. 记录存款前余额"):
            before = _get_balance(biz, ACC_A)

        with allure.step(f"2. 存款 100 到 {ACC_A}"):
            resp = biz.deposit(ACC_A, 100)
            assert resp.status_code == 200
            allure.attach(resp.text, "存款响应",
                          attachment_type=allure.attachment_type.TEXT)

        with allure.step("3. 校验余额 +100"):
            _assert_delta(biz, ACC_A, before, +100)

    @allure.story("正常存款")
    @allure.title("TC_DC_DEP_002 存款 0.01：精度保留")
    def test_deposit_small_amount_precision(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)

        with allure.step("1. 记录存款前余额"):
            before = _get_balance(biz, ACC_A)

        with allure.step("2. 存款 0.01"):
            resp = biz.deposit(ACC_A, 0.01)
            assert resp.status_code == 200

        with allure.step("3. 校验精度保留"):
            _assert_delta(biz, ACC_A, before, 0.01)

    @pytest.mark.xfail(reason="BUG_201：/deposit 允许 0 元返回 200，应拒绝")
    @allure.story("边界-零值")
    @allure.title("TC_DC_DEP_003 存款 0 元应被拒绝")
    def test_deposit_zero_should_reject(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)

        with allure.step("1. 记录存款前余额"):
            before = _get_balance(biz, ACC_A)

        with allure.step("2. 尝试存款 0 元"):
            resp = biz.deposit(ACC_A, 0)

        with allure.step("3. 断言：0 元存款应被拒绝"):
            assert resp.status_code != 200, "0 元存款应被拒绝"

        with allure.step("4. 断言：余额未变"):
            _assert_delta(biz, ACC_A, before, 0)

    @pytest.mark.xfail(reason="BUG_202：/deposit 允许负数金额，导致余额反向减少")
    @allure.story("边界-负数")
    @allure.title("TC_DC_DEP_004 存款 -100：不得减少余额")
    def test_deposit_negative_no_decrease(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)

        with allure.step("1. 记录存款前余额"):
            before = _get_balance(biz, ACC_A)

        with allure.step("2. 尝试存款 -100 元"):
            resp = biz.deposit(ACC_A, -100)

        with allure.step("3. 断言：负数存款应被拒绝"):
            assert resp.status_code != 200, "负数存款应被拒绝"

        with allure.step("4. 断言：余额未变"):
            _assert_delta(biz, ACC_A, before, 0)

# ==================== 取款一致性 ====================

@allure.feature("数据一致性-取款")
class TestWithdrawConsistency:

    @allure.story("正常取款")
    @allure.title("TC_DC_WD_001 取款 100：余额 -100")
    def test_withdraw_normal_balance(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)

        with allure.step("1. 先存款 500 保证余额充足"):
            biz.deposit(ACC_A, 500)

        with allure.step("2. 记录取款前余额"):
            before = _get_balance(biz, ACC_A)

        with allure.step("3. 取款 100"):
            resp = biz.withdraw(ACC_A, 100)
            assert resp.status_code == 200

        with allure.step("4. 校验余额 -100"):
            _assert_delta(biz, ACC_A, before, -100)

    @allure.story("正常取款")
    @allure.title("TC_DC_WD_002 取款 0.01：精度保留")
    def test_withdraw_small_amount_precision(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)

        with allure.step("1. 先存款 500 保证余额充足"):
            biz.deposit(ACC_A, 500)

        with allure.step("2. 记录取款前余额"):
            before = _get_balance(biz, ACC_A)

        with allure.step("3. 取款 0.01"):
            resp = biz.withdraw(ACC_A, 0.01)
            assert resp.status_code == 200

        with allure.step("4. 校验精度保留"):
            _assert_delta(biz, ACC_A, before, -0.01)

    @pytest.mark.xfail(reason="BUG_205：/withdraw 允许 0 元返回 200，应拒绝")
    @allure.story("边界-零值")
    @allure.title("TC_DC_WD_003 取款 0 元应被拒绝")
    def test_withdraw_zero_should_reject(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)

        with allure.step("1. 记录取款前余额"):
            before = _get_balance(biz, ACC_A)

        with allure.step("2. 尝试取款 0 元"):
            resp = biz.withdraw(ACC_A, 0)

        with allure.step("3. 断言：0 元取款应被拒绝"):
            assert resp.status_code != 200, "0 元取款应被拒绝"

        with allure.step("4. 断言：余额未变"):
            _assert_delta(biz, ACC_A, before, 0)

    @pytest.mark.xfail(reason="BUG_204：/withdraw 允许负数金额，导致余额反向增加")
    @allure.story("边界-负数")
    @allure.title("TC_DC_WD_004 取款 -100：不得增加余额")
    def test_withdraw_negative_no_increase(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)

        with allure.step("1. 记录取款前余额"):
            before = _get_balance(biz, ACC_A)

        with allure.step("2. 尝试取款 -100 元"):
            resp = biz.withdraw(ACC_A, -100)

        with allure.step("3. 断言：负数取款应被拒绝"):
            assert resp.status_code != 200, "负数取款应被拒绝"

        with allure.step("4. 断言：余额未变"):
            _assert_delta(biz, ACC_A, before, 0)

    @pytest.mark.xfail(reason="BUG_203：/withdraw 允许透支，导致余额变负")
    @allure.story("边界-超额")
    @allure.title("TC_DC_WD_005 取款 999999999：不得造成透支")
    def test_withdraw_over_balance_no_overdraft(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)

        with allure.step("1. 记录取款前余额"):
            before = _get_balance(biz, ACC_A)

        with allure.step("2. 尝试取款 999999999 元（超额）"):
            resp = biz.withdraw(ACC_A, 999999999)

        with allure.step("3. 断言：超额取款应被拒绝"):
            assert resp.status_code != 200, "超额取款应被拒绝"

        with allure.step("4. 断言：余额未变"):
            _assert_delta(biz, ACC_A, before, 0)