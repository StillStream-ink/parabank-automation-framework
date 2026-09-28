from tests.ui_test.pages.base_page import BasePage


class LoanPage(BasePage):
    """贷款申请页"""

    LOAN_AMOUNT_INPUT = "input[id='amount']"
    DOWN_PAYMENT_INPUT = "input[id='downPayment']"
    FROM_ACCOUNT_SELECT = "select[id='fromAccountId']"
    APPLY_BUTTON = "input[value='Apply Now']"
    RESULT_PANEL = "#requestLoanResult"
    ERROR_PANEL = "#requestLoanError"
    LOAN_STATUS = "#loanStatus"

    def navigate(self):
        super().navigate("requestloan.htm")
        self.page.wait_for_load_state("networkidle")

    def apply_loan(self, loan_amount, down_payment, account_id):
        self.fill(self.LOAN_AMOUNT_INPUT, loan_amount)
        self.fill(self.DOWN_PAYMENT_INPUT, down_payment)
        self.page.locator(self.FROM_ACCOUNT_SELECT).select_option(account_id)
        self.click(self.APPLY_BUTTON)
        # 等待"结果页"或"错误页"任一出现
        self.page.wait_for_function(
            """() => {
                const r = document.querySelector('#requestLoanResult');
                const e = document.querySelector('#requestLoanError');
                const rVis = r && r.style.display !== 'none' && r.offsetParent !== null;
                const eVis = e && e.style.display !== 'none' && e.offsetParent !== null;
                return rVis || eVis;
            }""",
            timeout=10000,
        )

    def is_loan_processed(self):
        """进入了结果页或错误页之一"""
        try:
            return (
                self.page.locator(self.RESULT_PANEL).is_visible()
                or self.page.locator(self.ERROR_PANEL).is_visible()
            )
        except Exception:
            return False

    def is_loan_error(self):
        """显示了内部错误页"""
        try:
            return self.page.locator(self.ERROR_PANEL).is_visible()
        except Exception:
            return False

    def get_loan_status(self):
        """返回 Approved / Denied / Error / 空字符串"""
        if self.is_loan_error():
            return "Error"
        try:
            return self.page.locator(self.LOAN_STATUS).inner_text().strip()
        except Exception:
            return ""

    def is_loan_approved(self):
        return self.get_loan_status() == "Approved"

    def is_loan_denied(self):
        return self.get_loan_status() == "Denied"

    # 兼容旧代码
    def is_loan_success(self):
        return self.is_loan_processed()

    def get_error_text(self):
        try:
            return self.page.locator("#requestLoanDenied p.error").inner_text().strip()
        except Exception:
            return ""
