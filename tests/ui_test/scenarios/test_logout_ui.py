import allure
import pytest

from tests.ui_test.pages.logout_page import LogoutPage

pytestmark = [pytest.mark.ui, pytest.mark.login]


@allure.epic("ParaBank 银行系统")
@allure.feature("登出模块")
class TestLogoutUI:

    @allure.story("正常登出")
    @allure.title("TC_UI_LOGOUT_001 登出后跳转到登录页")
    def test_logout(self, logged_in_page, ui_base_url):
        with allure.step("1. 执行登出操作"):
            page = LogoutPage(logged_in_page, ui_base_url)
            page.navigate()

        with allure.step("2. 校验跳转到登录页"):
            assert page.is_on_login_page(), f"未跳转到登录页，当前 URL: {page.page.url}"

        with allure.step("3. 校验登录表单显示"):
            assert page.has_login_form(), "登录页未显示登录表单"
