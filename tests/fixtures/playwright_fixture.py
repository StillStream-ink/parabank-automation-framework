import pytest
from playwright.sync_api import Browser, Page


@pytest.fixture(scope="function")
def page(browser: Browser):
    context = browser.new_context()
    page: Page = context.new_page()
    yield page
    page.close()
    context.close()
