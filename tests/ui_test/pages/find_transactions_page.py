from tests.ui_test.pages.base_page import BasePage


class FindTransactionsPage(BasePage):
    """ParaBank 交易查询页"""

    ACCOUNT_SELECT = "select[id='accountId']"
    TX_ID_INPUT = "input[id='transactionId']"
    TX_DATE_INPUT = "input[id='transactionDate']"
    FROM_DATE_INPUT = "input[id='fromDate']"
    TO_DATE_INPUT = "input[id='toDate']"
    AMOUNT_INPUT = "input[id='amount']"

    FIND_BY_ID_BTN = "button[id='findById']"
    FIND_BY_DATE_BTN = "button[id='findByDate']"
    FIND_BY_RANGE_BTN = "button[id='findByDateRange']"
    FIND_BY_AMOUNT_BTN = "button[id='findByAmount']"

    def navigate(self):
        super().navigate("findtrans.htm")
        self.page.wait_for_load_state("networkidle")

    def find_by_id(self, account_id, tx_id):
        self.page.locator(self.ACCOUNT_SELECT).select_option(account_id)
        self.fill(self.TX_ID_INPUT, tx_id)
        self.click(self.FIND_BY_ID_BTN)
        self.page.wait_for_load_state("networkidle")

    def find_by_amount(self, account_id, amount):
        self.page.locator(self.ACCOUNT_SELECT).select_option(account_id)
        self.fill(self.AMOUNT_INPUT, amount)
        self.click(self.FIND_BY_AMOUNT_BTN)
        self.page.wait_for_load_state("networkidle")

    def find_by_date_range(self, account_id, from_date, to_date):
        self.page.locator(self.ACCOUNT_SELECT).select_option(account_id)
        self.fill(self.FROM_DATE_INPUT, from_date)
        self.fill(self.TO_DATE_INPUT, to_date)
        self.click(self.FIND_BY_RANGE_BTN)
        self.page.wait_for_load_state("networkidle")

    def find_by_date(self, account_id, date):
        self.page.locator(self.ACCOUNT_SELECT).select_option(account_id)
        self.fill(self.TX_DATE_INPUT, date)
        self.click(self.FIND_BY_DATE_BTN)
        self.page.wait_for_load_state("networkidle")

    def get_result_text(self):
        """返回页面主体文本，用于判断是否有结果"""
        return self.page.locator("body").inner_text()

    def has_results(self):
        """页面上是否出现了交易记录表格"""
        body = self.get_result_text()
        return "Transaction" in body or "No transactions" in body
