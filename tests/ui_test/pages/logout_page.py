from tests.ui_test.pages.base_page import BasePage


class LogoutPage(BasePage):
    """ParaBank 登出页  访问后重定向到登录页"""

    def navigate(self):
        super().navigate("logout.htm")
        self.page.wait_for_load_state("networkidle")

    def is_on_login_page(self):
        """判断当前是否已登出（在登录页）"""
        url = self.page.url
        return "index.htm" in url or "login" in url.lower()

    def has_login_form(self):
        return self.page.locator("input[name='username']").count() > 0
