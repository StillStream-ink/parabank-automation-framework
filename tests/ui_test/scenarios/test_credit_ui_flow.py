import pytest
import time
import allure
from tests.ui_test.pages.register_page import RegisterPage


pytestmark = [pytest.mark.ui, pytest.mark.login]


@allure.epic("ParaBank 银行系统")
@allure.feature("注册模块")
class TestCreditUIFlow:

    @allure.story("用户注册页面流程")
    @allure.title("TC_UI_001：正常用户注册")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_user_register(self, page, ui_base_url):
        with allure.step("1. 生成唯一用户名（时间戳后缀，避免重复注册）"):
            unique_user = f"testdemo{int(time.time()) % 1000000}"

        with allure.step("2. 打开注册页面"):
            register_page = RegisterPage(page, ui_base_url)
            register_page.goto()

        with allure.step(f"3. 填写注册信息并提交（用户名={unique_user}）"):
            register_page.register(
                firstname="test",
                lastname="demo",
                address="test address",
                city="Guangzhou",
                state="GD",
                zipcode="510000",
                phone="13800138000",
                ssn="123-45-6789",
                username=unique_user,
                pwd="123456",
            )

        with allure.step("4. 校验注册成功提示"):
            assert page.get_by_text(
                "Your account was created successfully"
            ).is_visible(timeout=8000), "注册失败"