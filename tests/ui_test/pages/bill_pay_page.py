from tests.ui_test.pages.base_page import BasePage


class BillPayPage(BasePage):
    """ParaBank 账单支付页  所有输入框用 name 定位（无 id）"""

    PAYEE_NAME = "input[name='payee.name']"
    ADDRESS = "input[name='payee.address.street']"
    CITY = "input[name='payee.address.city']"
    STATE = "input[name='payee.address.state']"
    ZIP_CODE = "input[name='payee.address.zipCode']"
    PHONE = "input[name='payee.phoneNumber']"
    ACCOUNT_NUMBER = "input[name='payee.accountNumber']"
    VERIFY_ACCOUNT = "input[name='verifyAccount']"
    AMOUNT = "input[name='amount']"
    FROM_ACCOUNT_SELECT = "select[name='fromAccountId']"
    SEND_BUTTON = "input[value='Send Payment']"

    def navigate(self):
        super().navigate("billpay.htm")
        self.page.wait_for_load_state("networkidle")

    def pay_bill(self, payee_name, amount, from_account_id,
                 address="123 Main St", city="San Francisco",
                 state="CA", zipcode="94105", phone="4155550100",
                 account_number="12345678"):
        self.fill(self.PAYEE_NAME, payee_name)
        self.fill(self.ADDRESS, address)
        self.fill(self.CITY, city)
        self.fill(self.STATE, state)
        self.fill(self.ZIP_CODE, zipcode)
        self.fill(self.PHONE, phone)
        self.fill(self.ACCOUNT_NUMBER, account_number)
        self.fill(self.VERIFY_ACCOUNT, account_number)
        self.fill(self.AMOUNT, amount)
        self.page.locator(self.FROM_ACCOUNT_SELECT).select_option(from_account_id)
        self.click(self.SEND_BUTTON)
        self.page.wait_for_load_state("networkidle")

    def get_body_text(self):
        return self.page.locator("body").inner_text()

    def is_payment_success(self):
        body = self.get_body_text().lower()
        return "bill payment" in body and ("complete" in body or "successful" in body or "processed" in body)
