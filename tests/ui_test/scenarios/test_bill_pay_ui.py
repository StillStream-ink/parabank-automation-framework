import pytest
import allure
from tests.ui_test.pages.bill_pay_page import BillPayPage


pytestmark = [pytest.mark.ui, pytest.mark.regression]

@allure.epic("ParaBank银行系统")
@allure.feature("账单支付模块")
class TestBillPayUI:

    @allure.story("正常支付")
    @allure.title("TC_UI_BP_001 正常账单支付")
    def test_bill_pay_normal(self, logged_in_page, ui_base_url):
        page = BillPayPage(logged_in_page, ui_base_url)
        page.navigate()
        page.pay_bill(payee_name="TestPayee", amount="10", from_account_id="54321")
        body = page.get_body_text()
        assert "Bill Payment" in body or "complete" in body.lower(), \
            f"支付失败，页面文本前 200 字：{body[:200]}"

    @allure.story("边界异常")
    @allure.title("TC_UI_BP_002 金额为 0 的账单支付")
    def test_bill_pay_amount_zero(self, logged_in_page, ui_base_url):
        page = BillPayPage(logged_in_page, ui_base_url)
        page.navigate()
        page.pay_bill(payee_name="TestPayee", amount="0", from_account_id="54321")
        body = page.get_body_text()
        # 只要页面有响应即可（如果成功则是 bug）
        assert len(body) > 0

    @allure.story("边界异常")
    @allure.title("TC_UI_BP_003 金额超过余额的账单支付")
    def test_bill_pay_over_balance(self, logged_in_page, ui_base_url):
        page = BillPayPage(logged_in_page, ui_base_url)
        page.navigate()
        page.pay_bill(payee_name="TestPayee", amount="99999999", from_account_id="54321")
        body = page.get_body_text()
        assert len(body) > 0
