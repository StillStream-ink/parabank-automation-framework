"""混合场景测试：API 造数据 + UI 验证 / UI 操作 + API 校验。

特点：每个用例都同时用到 ParaBankBiz（API）和 Playwright（UI）。
"""
import xml.etree.ElementTree as ET
from decimal import Decimal

import allure
import pytest

from config.test_constants import (
    ACC_A,
    ACC_B,
    BASE_URL,
    USER_JOHN,
)
from config.test_constants import (
    CUSTOMER_ID_JOHN as CUSTOMER_ID,
)
from tests.api_test.business.parabank_biz import ParaBankBiz
from tests.ui_test.pages.overview_page import OverviewPage


def _api_balance(account_id):
    biz = ParaBankBiz(BASE_URL, USER_JOHN)
    resp = biz.get_single_account_detail(account_id)
    assert resp.status_code == 200
    root = ET.fromstring(resp.text)
    return Decimal(root.find("balance").text)


pytestmark = [pytest.mark.ui, pytest.mark.regression]


@allure.epic("ParaBank 银行系统")
@allure.feature("混合场景-API与UI联动")
class TestMixedScenarios:

    # ==================== 场景 1：API 操作 + UI 验证 ====================

    @pytest.mark.smoke
    @allure.story("API 转账 -> UI 验证余额")
    @allure.title("TC_MIX_001 API 转账 100 后，UI 应显示新余额")
    def test_api_transfer_ui_verify(self, logged_in_page, ui_base_url):
        with allure.step(f"1. API 记录 {ACC_A} 转账前余额"):
            biz = ParaBankBiz(BASE_URL, USER_JOHN)
            before = _api_balance(ACC_A)

        with allure.step(f"2. API 从 {ACC_A} 转账 100 到 {ACC_B}"):
            resp = biz.transfer_funds(ACC_A, ACC_B, 100)
            assert resp.status_code == 200, "API 转账失败"

        with allure.step("3. API 校验余额减少 100"):
            after = _api_balance(ACC_A)
            assert after == before - 100

        with allure.step("4. UI 打开 overview 页面，校验显示同一余额"):
            page = OverviewPage(logged_in_page, ui_base_url)
            page.navigate()
            ui_balance = page.get_balance(ACC_A)
            assert ui_balance == after, (
                f"UI 显示余额 {ui_balance} 与 API 查询结果 {after} 不一致"
            )

    @allure.story("API 开户 -> UI 验证账户数")
    @allure.title("TC_MIX_002 API 开新账户后，UI 账户数应 +1")
    def test_api_open_account_ui_verify(self, logged_in_page, ui_base_url):
        with allure.step("1. UI 打开 overview，记录初始账户数"):
            biz = ParaBankBiz(BASE_URL, USER_JOHN)
            page = OverviewPage(logged_in_page, ui_base_url)
            page.navigate()
            before_count = page.account_count()
            assert before_count > 0

        with allure.step(f"2. API 开立 SAVINGS 账户（资金来源 {ACC_A}）"):
            resp = biz.open_new_account(CUSTOMER_ID, account_type=1, from_account_id=ACC_A)
            assert resp.status_code == 200

        with allure.step("3. UI 刷新页面，账户数应 +1"):
            page.navigate()
            after_count = page.account_count()
            assert after_count == before_count + 1, (
                f"UI 显示账户数未变化：{before_count} -> {after_count}"
            )

    # ==================== 场景 2：UI 操作 + API 验证 ====================

    @allure.story("UI 转账 -> API 验证余额")
    @allure.title("TC_MIX_003 UI 转账后，API 查询应反映余额变化")
    def test_ui_transfer_api_verify(self, logged_in_page, ui_base_url):
        with allure.step(f"1. API 记录 {ACC_A} / {ACC_B} 转账前余额"):
            before_a = _api_balance(ACC_A)
            before_b = _api_balance(ACC_B)

        with allure.step(f"2. UI 打开转账页，从 {ACC_A} 转 100 到 {ACC_B}"):
            logged_in_page.goto(f"{ui_base_url}/transfer.htm")
            logged_in_page.wait_for_load_state("networkidle")
            logged_in_page.fill("input#amount", "100")
            logged_in_page.locator("select#fromAccountId").select_option(ACC_A)
            logged_in_page.locator("select#toAccountId").select_option(ACC_B)
            logged_in_page.click("input[value='Transfer']")
            logged_in_page.wait_for_load_state("networkidle")

        with allure.step("3. UI 校验出现转账成功提示"):
            body = logged_in_page.locator("body").inner_text()
            assert "Transfer Complete" in body or "successfully" in body.lower(), (
                f"UI 转账未显示成功：{body[:200]}"
            )

        with allure.step("4. API 校验双方余额变动正确"):
            after_a = _api_balance(ACC_A)
            after_b = _api_balance(ACC_B)
            assert after_a == before_a - 100, f"转出方余额未减少：{before_a} -> {after_a}"
            assert after_b == before_b + 100, f"接收方余额未增加：{before_b} -> {after_b}"

    @allure.story("UI 开户 -> API 验证账户列表")
    @allure.title("TC_MIX_004 UI 开新账户后，API 查询应返回新账户")
    def test_ui_open_account_api_verify(self, logged_in_page, ui_base_url):
        with allure.step("1. API 记录开户前账户 ID 集合"):
            biz = ParaBankBiz(BASE_URL, USER_JOHN)
            resp = biz.get_customer_account_list(CUSTOMER_ID)
            root = ET.fromstring(resp.text)
            before_ids = {acc.find("id").text for acc in root.findall("account")}

        with allure.step(f"2. UI 开立 SAVINGS 账户（资金来源 {ACC_A}）"):
            logged_in_page.goto(f"{ui_base_url}/openaccount.htm")
            logged_in_page.wait_for_load_state("networkidle")
            logged_in_page.locator("select#type").select_option("1")  # SAVINGS
            logged_in_page.locator("select#fromAccountId").select_option(ACC_A)
            logged_in_page.click("input[value='Open New Account']")
            logged_in_page.wait_for_load_state("networkidle")

        with allure.step("3. API 重新查询，校验新增恰好 1 个账户"):
            resp2 = biz.get_customer_account_list(CUSTOMER_ID)
            root2 = ET.fromstring(resp2.text)
            after_ids = {acc.find("id").text for acc in root2.findall("account")}
            new_ids = after_ids - before_ids
            assert len(new_ids) == 1, (
                f"预期新增 1 个账户，实际新增 {len(new_ids)} 个：{new_ids}"
            )

    # ==================== 场景 3：三段式端到端 ====================

    @allure.story("端到端：API 造数据 -> UI 走流程 -> API 校验")
    @allure.title("TC_MIX_005 API 存款 -> UI 转账 -> API 校验最终余额")
    def test_e2e_three_stage(self, logged_in_page, ui_base_url):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)

        with allure.step(f"1. API 存款 500 到 {ACC_A}（造数据）"):
            resp = biz.deposit(ACC_A, 500)
            assert resp.status_code == 200
            stage1_balance = _api_balance(ACC_A)

        with allure.step(f"2. UI 转账 200 从 {ACC_A} 到 {ACC_B}"):
            logged_in_page.goto(f"{ui_base_url}/transfer.htm")
            logged_in_page.wait_for_load_state("networkidle")
            logged_in_page.fill("input#amount", "200")
            logged_in_page.locator("select#fromAccountId").select_option(ACC_A)
            logged_in_page.locator("select#toAccountId").select_option(ACC_B)
            logged_in_page.click("input[value='Transfer']")
            logged_in_page.wait_for_load_state("networkidle")

        with allure.step("3. API 校验最终余额（精确到分）"):
            final_balance = _api_balance(ACC_A)
            assert final_balance == stage1_balance - 200, (
                f"最终余额不符：阶段1={stage1_balance}, 阶段3={final_balance}, 预期差 200"
            )
