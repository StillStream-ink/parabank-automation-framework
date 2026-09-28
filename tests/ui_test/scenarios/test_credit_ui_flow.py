import time
import allure
from tests.ui_test.pages.register_page import RegisterPage


@allure.epic("ParaBank银行系统")
@allure.feature("注册模块")
class TestCreditUIFlow:

    @allure.story("用户注册页面流程")
    @allure.title("TC_UI_001：正常用户注册")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_user_register(self, page, ui_base_url):
        # 用时间戳保证用户名唯一，避免重复注册报错
        unique_user = f"testdemo{int(time.time()) % 1000000}"
        register_page = RegisterPage(page, ui_base_url)
        register_page.goto()
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
        assert page.get_by_text(
            "Your account was created successfully"
        ).is_visible(timeout=8000), "注册失败"