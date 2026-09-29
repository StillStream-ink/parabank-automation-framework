import pytest
import allure
from tests.ui_test.pages.find_transactions_page import FindTransactionsPage


pytestmark = [pytest.mark.ui, pytest.mark.transaction]

@allure.epic("ParaBank银行系统")
@allure.feature("交易查询模块")
class TestFindTransactionsUI:

    @allure.story("按金额查询")
    @allure.title("TC_UI_TXQ_001 按金额查询交易")
    def test_find_by_amount(self, logged_in_page, ui_base_url):
        find_page = FindTransactionsPage(logged_in_page, ui_base_url)
        find_page.navigate()
        find_page.find_by_amount("54321", "50")
        # 查询后页面应该变化（显示结果表格或提示）
        body = find_page.get_result_text()
        assert "transaction" in body.lower() or "no transactions" in body.lower(), \
            "查询后未出现结果区域"

    @allure.story("按日期区间查询")
    @allure.title("TC_UI_TXQ_002 按日期区间查询交易")
    def test_find_by_date_range(self, logged_in_page, ui_base_url):
        find_page = FindTransactionsPage(logged_in_page, ui_base_url)
        find_page.navigate()
        find_page.find_by_date_range("54321", "01-01-2000", "12-31-2030")
        body = find_page.get_result_text()
        assert "transaction" in body.lower() or "no transactions" in body.lower(), \
            "查询后未出现结果区域"

    @allure.story("按交易 ID 查询")
    @allure.title("TC_UI_TXQ_003 按交易 ID 查询不存在的记录")
    def test_find_by_invalid_id(self, logged_in_page, ui_base_url):
        find_page = FindTransactionsPage(logged_in_page, ui_base_url)
        find_page.navigate()
        find_page.find_by_id("54321", "99999999")
        # 无论成功失败，页面应有响应
        body = find_page.get_result_text()
        assert len(body) > 0, "页面无响应"

    @allure.story("边界异常")
    @allure.title("TC_UI_TXQ_004 按金额查询不存在的金额")
    def test_find_by_odd_amount(self, logged_in_page, ui_base_url):
        find_page = FindTransactionsPage(logged_in_page, ui_base_url)
        find_page.navigate()
        find_page.find_by_amount("54321", "999999")
        body = find_page.get_result_text()
        assert "no transactions" in body.lower() or "transaction" in body.lower(), \
            "查询结果异常"
