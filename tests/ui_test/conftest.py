import pytest
import allure
from playwright.sync_api import Page, Browser


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
    }


@pytest.fixture
def page(page: Page):
    # 每个用例新建页面，用完自动关闭
    yield page
    page.close()


# 钩子函数：捕获用例执行结果
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


# 失败自动截图
@pytest.fixture(autouse=True)
def screenshot_on_failure(request, page):
    yield
    if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
        screenshot_bytes = page.screenshot(full_page=True)
        allure.attach(
            screenshot_bytes,
            name="用例失败-全屏截图",
            attachment_type=allure.attachment_type.PNG,
        )