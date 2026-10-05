import allure
import pytest

from config.test_constants import ACC_A
from tests.ui_test.pages.find_transactions_page import FindTransactionsPage

pytestmark = [pytest.mark.ui, pytest.mark.transaction]


@allure.epic("ParaBank 银行系统")
@allure.feature("交易查询模块")
class TestFindTransactionsUI:

    @allure.story("按金额查询")
    @allure.title("TC_UI_TXQ_001 按金额查询交易")
    def test_find_by_amount(self, logged_in_page, ui_base_url):
        with allure.step("1. 打开交易查询页面"):
            find_page = FindTransactionsPage(logged_in_page, ui_base_url)
            find_page.navigate()

        with allure.step("2. 按账户 + 金额 50 查询"):
            find_page.find_by_amount(ACC_A, "50")

        with allure.step("3. 校验查询结果区域出现"):
            body = find_page.get_result_text().lower()
            assert "transaction" in body, "查询后未出现结果区域"

    @allure.story("按日期区间查询")
    @allure.title("TC_UI_TXQ_002 按日期区间查询交易")
    def test_find_by_date_range(self, logged_in_page, ui_base_url):
        with allure.step("1. 打开交易查询页面"):
            find_page = FindTransactionsPage(logged_in_page, ui_base_url)
            find_page.navigate()

        with allure.step("2. 按日期区间 2000-01-01 至 2030-12-31 查询"):
            find_page.find_by_date_range(ACC_A, "01-01-2000", "12-31-2030")

        with allure.step("3. 校验长期区间应有交易记录"):
            assert find_page.has_results(), "长期区间查询应有交易记录"

    @allure.story("按交易 ID 查询")
    @allure.title("TC_UI_TXQ_003 按交易 ID 查询不存在的记录")
    def test_find_by_invalid_id(self, logged_in_page, ui_base_url):
        with allure.step("1. 打开交易查询页面"):
            find_page = FindTransactionsPage(logged_in_page, ui_base_url)
            find_page.navigate()

        with allure.step("2. 按不存在的交易 ID 99999999 查询"):
            find_page.find_by_id(ACC_A, "99999999")

        with allure.step("3. 校验页面显示无记录提示"):
            assert not find_page.has_results(), "不存在的交易 ID 应显示无记录提示"

    @allure.story("边界异常")
    @allure.title("TC_UI_TXQ_004 按金额查询不存在的金额")
    def test_find_by_odd_amount(self, logged_in_page, ui_base_url):
        with allure.step("1. 打开交易查询页面"):
            find_page = FindTransactionsPage(logged_in_page, ui_base_url)
            find_page.navigate()

        with allure.step("2. 按不存在的金额 999999 查询"):
            find_page.find_by_amount(ACC_A, "999999")

        with allure.step("3. 校验页面显示无记录提示"):
            assert not find_page.has_results(), "不存在的金额应显示无记录提示"
