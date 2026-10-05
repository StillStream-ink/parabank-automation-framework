from tests.ui_test.pages.base_page import BasePage


class LoginPage(BasePage):
    """登录页面"""
    # 元素定位
    USERNAME_INPUT = "input[name='username']"
    PASSWORD_INPUT = "input[name='password']"
    LOGIN_BUTTON = "input[value='Log In']"
    ERROR_MESSAGE = ".error"
    LOGOUT_LINK = "text=Log Out"
    ACCOUNT_OVERVIEW = "text=Accounts Overview"
    def navigate(self):
        super().navigate("index.htm")
    def login(self, username, password):
        """执行登录"""
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
        self.page.wait_for_load_state("networkidle")
    def verify_login_success(self):
        """验证登录成功"""
        assert self.page.is_visible(self.ACCOUNT_OVERVIEW), "登录失败：未找到账户总览页面"
    def get_error_message(self):
        """获取登录错误提示"""
        return self.get_text(self.ERROR_MESSAGE)
    def logout(self):
        """退出登录"""
        self.click(self.LOGOUT_LINK)
        self.page.wait_for_load_state("networkidle")
