# 修改这一行
from tests.ui_test.pages.base_page import BasePage

class TransferPage(BasePage):
    """转账页面"""
    # 元素定位
    FROM_ACCOUNT = "#fromAccountId"
    TO_ACCOUNT = "#toAccountId"
    AMOUNT_INPUT = "#amount"
    TRANSFER_BUTTON = "input[value='Transfer']"
    SUCCESS_MESSAGE = "text=Transfer Complete!"
    ERROR_MESSAGE = ".error"
    def navigate(self):
        super().navigate("transfer.htm")
    def transfer(self, from_account, to_account, amount):
        """执行转账"""
        self.page.select_option(self.FROM_ACCOUNT, from_account)
        self.page.select_option(self.TO_ACCOUNT, to_account)
        self.fill(self.AMOUNT_INPUT, amount)
        self.click(self.TRANSFER_BUTTON)
        self.page.wait_for_load_state("networkidle")
    def is_transfer_success(self):
        """判断转账是否成功"""
        return self.is_visible(self.SUCCESS_MESSAGE)
    def get_error_message(self):
        """获取错误提示"""
        if self.is_visible(self.ERROR_MESSAGE):
            return self.get_text(self.ERROR_MESSAGE)
        return ""
    def get_account_balance(self, account_id):
        """获取指定账户余额（需在账户总览页操作）"""
        self.navigate("overview.htm")
        self.page.click(f"text={account_id}")
        self.page.wait_for_load_state("networkidle")
        balance = self.get_text("#accountDetails .balance, .balance")
        return balance
