from tests.ui_test.pages.base_page import BasePage


class AccountActivityPage(BasePage):
    """ParaBank 账户详情页"""

    MONTH_SELECT = "select[id='month']"
    TYPE_SELECT = "select[id='transactionType']"
    GO_BUTTON = "input[value='Go']"

    def navigate(self, account_id="54321"):
        self.page.goto(f"{self.ui_base_url}/activity.htm?id={account_id}")
        self.page.wait_for_load_state("networkidle")

    def filter_by(self, month, transaction_type):
        self.page.locator(self.MONTH_SELECT).select_option(month)
        self.page.locator(self.TYPE_SELECT).select_option(transaction_type)
        self.click(self.GO_BUTTON)
        self.page.wait_for_load_state("networkidle")

    def get_body_text(self):
        return self.page.locator("body").inner_text()

    def has_account_number(self, account_id):
        return account_id in self.get_body_text()

    def has_balance_section(self):
        body = self.get_body_text()
        return "Balance:" in body and "Available:" in body
