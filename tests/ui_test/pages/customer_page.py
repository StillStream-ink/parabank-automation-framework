from tests.ui_test.pages.base_page import BasePage

class CustomerPage(BasePage):
    """客户信息页面"""
    # 元素定位
    CUSTOMER_NAME = "text=Customer Name"
    ADDRESS_INFO = "xpath=//td[text()='Address']/following-sibling::td"
    PHONE_INFO = "xpath=//td[text()='Phone']/following-sibling::td"
    UPDATE_PROFILE_LINK = "text=Update Profile"
    SAVE_BUTTON = "input[value='Save']"
    SUCCESS_UPDATE_MSG = "text=Profile Updated"

    def navigate(self):
        """跳转到客户资料页面"""
        super().navigate("updateprofile.htm")

    def update_customer_info(self, address, phone):
        """更新客户地址和手机号"""
        self.fill("input[name='address.street']", address)
        self.fill("input[name='phoneNumber']", phone)
        self.click(self.SAVE_BUTTON)

    def is_update_success(self):
        """判断资料更新是否成功"""
        return self.is_visible(self.SUCCESS_UPDATE_MSG)

    def get_address(self):
        """获取页面展示的地址信息"""
        return self.get_text(self.ADDRESS_INFO)

    def get_phone(self):
        """获取页面展示的手机号"""
        return self.get_text(self.PHONE_INFO)
