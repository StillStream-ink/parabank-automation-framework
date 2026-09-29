import pytest
import allure
from tests.ui_test.pages.logout_page import LogoutPage


pytestmark = [pytest.mark.ui, pytest.mark.login]

@allure.epic("ParaBank银行系统")
@allure.feature("登出模块")
class TestLogoutUI:

    @allure.story("正常登出")
    @allure.title("TC_UI_LOGOUT_001 登出后跳转到登录页")
    def test_logout(self, logged_in_page, ui_base_url):
        page = LogoutPage(logged_in_page, ui_base_url)
        page.navigate()
        assert page.is_on_login_page(), f"未跳转到登录页，当前 URL: {page.page.url}"
        assert page.has_login_form(), "登录页未显示登录表单"
