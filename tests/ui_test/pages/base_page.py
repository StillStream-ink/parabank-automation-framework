
class BasePage:
    def __init__(self, page, ui_base_url):
        self.page = page
        self.ui_base_url = ui_base_url

    def navigate(self, path: str):
        """拼接ui基础地址，访问页面"""
        full_url = f"{self.ui_base_url}/{path}"
        self.page.goto(full_url)

    def fill(self, locator, value):
        self.page.locator(locator).fill(value)

    def click(self, locator):
        self.page.locator(locator).click()

    def is_visible(self, locator, timeout=3000):
        return self.page.locator(locator).is_visible(timeout=timeout)

    def get_text(self, locator):
        return self.page.locator(locator).text_content()

