import allure
import pytest
from tests.ui_test.pages.login_page import LoginPage

pytestmark = [pytest.mark.ui, pytest.mark.login]


@allure.epic("ParaBank 银行系统")
@allure.feature("登录模块")
class TestLoginUI:

    @pytest.mark.smoke
    @allure.story("正常登录")
    @allure.title("TC_Login_001: 正确账号密码登录成功")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_login_success(self, page, ui_base_url):
        with allure.step("1. 打开登录页面"):
            login_page = LoginPage(page, ui_base_url)
            login_page.navigate()

        with allure.step("2. 输入 john / demo 登录"):
            login_page.login("john", "demo")

        with allure.step("3. 校验登录成功"):
            login_page.verify_login_success()

    @allure.story("异常登录")
    @allure.title("TC_Login_002: 错误密码登录失败")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_wrong_pwd(self, page, ui_base_url):
        with allure.step("1. 打开登录页面"):
            login_page = LoginPage(page, ui_base_url)
            login_page.navigate()

        with allure.step("2. 输入 john / wrong123 登录"):
            login_page.login("john", "wrong123")

        with allure.step("3. 校验错误提示"):
            err_msg = login_page.get_error_message()
            assert err_msg != "", "应当返回错误提示"

    @allure.story("异常登录")
    @allure.title("TC_Login_003: 空用户名空密码提交")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_empty(self, page, ui_base_url):
        with allure.step("1. 打开登录页面"):
            login_page = LoginPage(page, ui_base_url)
            login_page.navigate()

        with allure.step("2. 提交空用户名 / 空密码"):
            login_page.login("", "")

        with allure.step("3. 校验错误提示"):
            err_msg = login_page.get_error_message()
            assert err_msg != "", "应当返回错误提示"