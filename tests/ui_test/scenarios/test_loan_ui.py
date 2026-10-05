from config.test_constants import ACC_A
import allure
import pytest
from tests.ui_test.pages.loan_page import LoanPage


pytestmark = [pytest.mark.ui, pytest.mark.loan]


@allure.epic("ParaBank 银行系统")
@allure.feature("贷款申请模块")
class TestLoanUI:

    @allure.story("正常贷款申请")
    @allure.title("TC_Loan_001: 提交贷款，系统应处理")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_loan_apply_success(self, logged_in_page, ui_base_url):
        with allure.step("1. 打开发起贷款申请页"):
            loan_page = LoanPage(logged_in_page, ui_base_url)
            loan_page.navigate()

        with allure.step("2. 提交申请：贷款 1000，首付 200"):
            loan_page.apply_loan("1000", "200", ACC_A)

        with allure.step("3. 校验系统处理结果"):
            status = loan_page.get_loan_status()
            assert loan_page.is_loan_processed(), "系统未处理贷款请求"
            assert status in ("Approved", "Denied"), f"状态异常: {status}"

    @allure.story("边界异常场景")
    @allure.title("TC_Loan_002: 贷款金额 0，系统应拒绝")
    @allure.severity(allure.severity_level.NORMAL)
    def test_loan_amount_zero(self, logged_in_page, ui_base_url):
        """ParaBank 正确拒绝 0 元贷款（Denied 或 Error）"""
        with allure.step("1. 打开发起贷款申请页"):
            loan_page = LoanPage(logged_in_page, ui_base_url)
            loan_page.navigate()

        with allure.step("2. 提交申请：贷款 0，首付 100"):
            loan_page.apply_loan("0", "100", ACC_A)

        with allure.step("3. 校验系统拒绝 0 元贷款"):
            status = loan_page.get_loan_status()
            assert loan_page.is_loan_processed(), "系统未处理请求"
            assert status in ("Denied", "Error"), f"0 元应被拒绝，实际: {status}"

    @allure.story("边界异常场景")
    @allure.title("TC_Loan_003: 贷款金额远超余额，系统应拒绝")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_loan_exceed_balance(self, logged_in_page, ui_base_url):
        """ParaBank 正确拒绝超额贷款"""
        with allure.step("1. 打开发起贷款申请页"):
            loan_page = LoanPage(logged_in_page, ui_base_url)
            loan_page.navigate()

        with allure.step("2. 提交申请：贷款 999999（超额），首付 100"):
            loan_page.apply_loan("999999", "100", ACC_A)

        with allure.step("3. 校验系统拒绝超额贷款"):
            status = loan_page.get_loan_status()
            assert loan_page.is_loan_processed(), "系统未处理请求"
            assert status in ("Denied", "Error"), f"超额应被拒绝，实际: {status}"