from config.test_constants import ACC_A
import pytest
import allure
from tests.ui_test.pages.open_account_page import OpenAccountPage


pytestmark = [pytest.mark.ui, pytest.mark.regression]


@allure.epic("ParaBank 银行系统")
@allure.feature("开户模块")
class TestOpenAccountUI:

    @pytest.mark.smoke
    @allure.story("正常开户")
    @allure.title("TC_UI_OA_001 开立新的储蓄账户")
    def test_open_savings_account(self, logged_in_page, ui_base_url):
        with allure.step("1. 打开开户页面"):
            page = OpenAccountPage(logged_in_page, ui_base_url)
            page.navigate()

        with allure.step("2. 开立储蓄账户（type=1=SAVINGS）"):
            page.open_account(account_type=1, from_account_id=ACC_A)

        with allure.step("3. 校验开户成功提示"):
            body = page.get_body_text()
            assert "Account Opened" in body or "Congratulations" in body or "new account" in body.lower(), \
                f"开户失败，页面文本前 200 字：{body[:200]}"

    @allure.story("正常开户")
    @allure.title("TC_UI_OA_002 开立新的支票账户")
    def test_open_checking_account(self, logged_in_page, ui_base_url):
        with allure.step("1. 打开开户页面"):
            page = OpenAccountPage(logged_in_page, ui_base_url)
            page.navigate()

        with allure.step("2. 开立支票账户（type=0=CHECKING）"):
            page.open_account(account_type=0, from_account_id=ACC_A)

        with allure.step("3. 校验开户成功提示"):
            body = page.get_body_text()
            assert "Account Opened" in body or "Congratulations" in body or "new account" in body.lower(), \
                f"开户失败，页面文本前 200 字：{body[:200]}"