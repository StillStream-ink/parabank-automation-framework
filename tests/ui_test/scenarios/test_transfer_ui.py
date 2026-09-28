import allure
import pytest
from tests.ui_test.pages.transfer_page import TransferPage

BASE_URL = "http://localhost:8080/parabank"

@allure.epic("ParaBank 银行系统")
@allure.feature("转账模块")
class TestTransferUI:
    @allure.story("正常转账")
    @allure.title("TC_Trans_001: 正常金额转账成功")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_transfer_success(self, logged_in_page, ui_base_url):
        transfer_page = TransferPage(logged_in_page, ui_base_url)
        transfer_page.navigate()
        transfer_page.transfer("12567", "12345", "10")
        assert transfer_page.is_transfer_success(), "转账未成功"

    @allure.story("边界值测试")
    @allure.title("TC_Trans_002: 转账金额为 0（已知缺陷 BUG_001）")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.xfail(reason="BUG_001: ParaBank 允许金额为0的转账成功，应拦截", strict=True)
    def test_transfer_zero_amount(self, logged_in_page, ui_base_url):
        transfer_page = TransferPage(logged_in_page, ui_base_url)
        transfer_page.navigate()
        transfer_page.transfer("12567", "12345", "0")
        assert not transfer_page.is_transfer_success(), "金额为 0 时不应转账成功"

    @allure.story("边界值测试")
    @allure.title("TC_Trans_003: 转账金额为负数（已知缺陷 BUG_002）")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.xfail(reason="BUG_002: ParaBank 允许负数金额转账，余额反向变化", strict=True)
    def test_transfer_negative_amount(self, logged_in_page, ui_base_url):
        transfer_page = TransferPage(logged_in_page, ui_base_url)
        transfer_page.navigate()
        transfer_page.transfer("12567", "12345", "-100")
        assert not transfer_page.is_transfer_success(), "负数金额不应转账成功"

    @allure.story("异常转账")
    @allure.title("TC_Trans_004: 转账金额大于账户余额（已知缺陷 BUG_003）")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.xfail(reason="BUG_003: ParaBank 允许余额不足转账，余额变成负数", strict=True)
    def test_transfer_insufficient_balance(self, logged_in_page, ui_base_url):
        """余额 100，转 100.01，差 0.01 边界值"""
        transfer_page = TransferPage(logged_in_page, ui_base_url)
        transfer_page.navigate()
        transfer_page.transfer("12567", "12345", "100.01")
        assert not transfer_page.is_transfer_success(), "余额不足时不应转账成功"
