from tests.ui_test.pages.base_page import BasePage


class RegisterPage(BasePage):
    """ParaBank 注册页"""

    FIRST_NAME = "input[name='customer.firstName']"
    LAST_NAME = "input[name='customer.lastName']"
    ADDRESS = "input[name='customer.address.street']"
    CITY = "input[name='customer.address.city']"
    STATE = "input[name='customer.address.state']"
    ZIP_CODE = "input[name='customer.address.zipCode']"
    PHONE = "input[name='customer.phoneNumber']"
    SSN = "input[name='customer.ssn']"
    USERNAME = "input[name='customer.username']"
    PASSWORD = "input[name='customer.password']"
    CONFIRM_PASSWORD = "input[name='repeatedPassword']"
    REGISTER_BUTTON = "input[value='Register']"

    def goto(self):
        """直接访问注册页（ParaBank 注册页 URL 是 register.htm）"""
        super().navigate("register.htm")
        self.page.wait_for_load_state("networkidle")

    # 兼容别名
    def navigate(self):
        self.goto()

    def register(self, firstname, lastname, address, city, state,
                 zipcode, phone, ssn, username, pwd):
        self.fill(self.FIRST_NAME, firstname)
        self.fill(self.LAST_NAME, lastname)
        self.fill(self.ADDRESS, address)
        self.fill(self.CITY, city)
        self.fill(self.STATE, state)
        self.fill(self.ZIP_CODE, zipcode)
        self.fill(self.PHONE, phone)
        self.fill(self.SSN, ssn)
        self.fill(self.USERNAME, username)
        self.fill(self.PASSWORD, pwd)
        self.fill(self.CONFIRM_PASSWORD, pwd)
        self.click(self.REGISTER_BUTTON)
        self.page.wait_for_load_state("networkidle")

    def get_success_text(self):
        return self.page.locator("h1.title").text_content()
