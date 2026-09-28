from tests.ui_test.pages.base_page import BasePage


class LoanListPage(BasePage):
    """ParaBank 账户总览页 —— 可查询贷款信息"""

    LOAN_TABLE = "table#loanTable"
    ACCOUNT_OVERVIEW = "text=Accounts Overview"

    def navigate(self):
        super().navigate("overview.htm")
        self.page.wait_for_load_state("networkidle")

    def get_first_loan_record(self):
        """返回页面中含 'Loan' 的文本；找不到返回 None。"""
        body_text = self.page.locator("body").inner_text()
        if "loan" in body_text.lower():
            return body_text
        return None

    def back_to_home(self):
        super().navigate("index.htm")