import pytest
import allure
from config.test_constants import ACC_A
from tests.ui_test.pages.account_activity_page import AccountActivityPage


pytestmark = [pytest.mark.ui, pytest.mark.regression]


@allure.epic("ParaBank 银行系统")
@allure.feature("账户详情模块")
class TestAccountActivityUI:

    @allure.story("查看账户详情")
    @allure.title("TC_UI_ACC_001 查看账户余额")
    def test_view_account_balance(self, logged_in_page, ui_base_url):
        with allure.step(f"1. 打开账户 {ACC_A} 详情页"):
            page = AccountActivityPage(logged_in_page, ui_base_url)
            page.navigate(ACC_A)

        with allure.step("2. 校验账户号和余额字段展示"):
            body = page.get_body_text()
            assert ACC_A in body, "页面未显示账户号"
            assert "Balance:" in body, "页面未显示余额"
            assert "Available:" in body, "页面未显示可用余额"

    @allure.story("交易筛选")
    @allure.title("TC_UI_ACC_002 按月份和类型筛选交易")
    def test_filter_transactions(self, logged_in_page, ui_base_url):
        with allure.step(f"1. 打开账户 {ACC_A} 详情页"):
            page = AccountActivityPage(logged_in_page, ui_base_url)
            page.navigate(ACC_A)

        with allure.step("2. 按月份=All、类型=All 筛选"):
            page.filter_by("All", "All")

        with allure.step("3. 校验筛选后页面正常"):
            body = page.get_body_text()
            assert "Account Activity" in body or "Date" in body, "筛选后页面异常"