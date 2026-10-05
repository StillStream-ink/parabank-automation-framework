from config.test_constants import ACC_A
import pytest
import allure

from tests.ui_test.pages.loan_page import LoanPage
from tests.ui_test.pages.loan_list_page import LoanListPage


pytestmark = [pytest.mark.ui, pytest.mark.loan]


@allure.epic("ParaBank 银行系统")
@allure.feature("贷款流程")
def test_submit_loan_apply(logged_in_page, ui_base_url):
    with allure.step("1. 打开发起贷款申请页"):
        loan_page = LoanPage(logged_in_page, ui_base_url)
        loan_page.navigate()

    with allure.step("2. 提交申请：贷款 1000，首付 200"):
        loan_page.apply_loan("1000", "200", ACC_A)

    with allure.step("3. 校验系统处理结果"):
        status = loan_page.get_loan_status()
        assert loan_page.is_loan_processed(), "系统未处理贷款请求"
        assert status in ("Approved", "Denied"), f"状态异常: {status}"


@allure.story("贷款记录查询")
@allure.title("TC_UI_003：提交贷款申请后，页面查询贷款记录")
@allure.severity(allure.severity_level.NORMAL)
def test_query_loan_record(logged_in_page, ui_base_url):
    with allure.step("1. 打开贷款记录页面"):
        loan_list_page = LoanListPage(logged_in_page, ui_base_url)
        loan_list_page.navigate()

    with allure.step("2. 查询第一条贷款记录"):
        record = loan_list_page.get_first_loan_record()

    with allure.step("3. 校验记录存在"):
        assert record is not None, "未查询到贷款记录"


@allure.story("贷款申请-异常校验")
@allure.title("TC_UI_004：贷款金额填负数，系统应拒绝")
@allure.severity(allure.severity_level.NORMAL)
def test_loan_apply_invalid_amount(logged_in_page, ui_base_url):
    with allure.step("1. 打开发起贷款申请页"):
        loan_page = LoanPage(logged_in_page, ui_base_url)
        loan_page.navigate()

    with allure.step("2. 提交申请：贷款 -500，首付 100"):
        loan_page.apply_loan("-500", "100", ACC_A)

    with allure.step("3. 校验系统拒绝负数申请"):
        status = loan_page.get_loan_status()
        assert loan_page.is_loan_processed(), "系统未处理请求"
        assert status in ("Denied", "Error"), f"负数应被拒绝，实际: {status}"