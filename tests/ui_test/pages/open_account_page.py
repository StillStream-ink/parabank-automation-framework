from tests.ui_test.pages.base_page import BasePage


class OpenAccountPage(BasePage):
    """ParaBank 开户页"""

    TYPE_SELECT = "select[id='type']"
    FROM_ACCOUNT_SELECT = "select[id='fromAccountId']"
    OPEN_BUTTON = "input[value='Open New Account']"

    def navigate(self):
        super().navigate("openaccount.htm")
        self.page.wait_for_load_state("networkidle")

    def open_account(self, account_type, from_account_id):
        """account_type: 0=CHECKING, 1=SAVINGS"""
        self.page.locator(self.TYPE_SELECT).select_option(str(account_type))
        self.page.locator(self.FROM_ACCOUNT_SELECT).select_option(from_account_id)
        self.click(self.OPEN_BUTTON)
        self.page.wait_for_load_state("networkidle")

    def get_body_text(self):
        return self.page.locator("body").inner_text()

    def is_account_opened(self):
        body = self.get_body_text().lower()
        return ("account opened" in body) or ("congratulations" in body) or ("new account" in body and "opened" in body)
