import pytest
from playwright.sync_api import Page, Browser
from tests.api_test.services.base_api import BaseApi
from config.env_config import get_base_url, get_ui_url
from zeep import Client

@pytest.fixture(scope="module")
def soap_client():
    wsdl_url = "http://localhost:8080/parabank/services/ParaBank?wsdl"
    client = Client(wsdl_url)
    return client

# ===================== API Fixture =====================
@pytest.fixture(scope="module")
def api_client():
    client = BaseApi(base_url=get_base_url())
    yield client

# ===================== Playwright UI Fixture =====================
@pytest.fixture(scope="function")
def page(browser: Browser):
    page: Page = browser.new_page()
    yield page
    page.close()

@pytest.fixture(scope="session")
def ui_base_url():
    return get_ui_url()

@pytest.fixture(scope="function")
def logged_in_page(page: Page, ui_base_url):
    """前置夹具：自动登录ParaBank，返回登录完成后的页面"""
    page.goto(f"{ui_base_url}/index.htm")
    # parabank 默认账号密码 john / demo
    page.fill("input[name='username']", "john")
    page.fill("input[name='password']", "demo")
    page.click("input[type='submit']")
    page.wait_for_url("**/overview.htm")
    yield page
    # 用例执行完毕，登出，保证数据隔离
    page.click("text=Log Out")

def pytest_collection_modifyitems(config, items):
    """自动给credit目录下所有用例添加xfail标记"""
    for item in items:
        if "tests/api_test/scenarios/credit/" in item.nodeid:
            item.add_marker(pytest.mark.xfail(
                reason="信贷Django后端服务127.0.0.1:8000未启动，启动服务后可正常执行",
                strict=False
            ))


# ==================== ParaBank 数据清理 ====================
@pytest.fixture(scope="session", autouse=True)
def parabank_cleanup():
    """Session 级别自动清理。

    行为：
    - 若环境变量 PARABANK_CLEANUP=0，跳过清理（调试用）
    - Session 开始时清一次（保证起点干净）
    - Session 结束时清一次（恢复环境给下次跑）
    """
    import os
    from tests.finalize.clean_data import ParaBankCleaner

    if os.getenv("PARABANK_CLEANUP", "1") == "0":
        yield
        return

    cleaner = ParaBankCleaner()
    cleaner.reset()
    yield
    cleaner.reset()
