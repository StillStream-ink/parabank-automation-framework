from decimal import Decimal

from tests.ui_test.pages.base_page import BasePage


def _parse_dollar(text):
    """'$1351.12' / '-$100.00' / '$0.00' -> Decimal"""
    text = text.strip().replace(",", "").replace("$", "")
    return Decimal(text)


class OverviewPage(BasePage):
    """ParaBank 账户总览页"""

    ACCOUNT_TABLE = "table#accountTable"

    def navigate(self):
        super().navigate("overview.htm")
        self.page.wait_for_load_state("networkidle")

    def get_balance(self, account_id):
        """从总览表读取指定账户的余额（Decimal）。"""
        rows = self.page.locator(f"{self.ACCOUNT_TABLE} tbody tr").all()
        for row in rows:
            cells = row.locator("td").all()
            if len(cells) >= 2 and cells[0].inner_text().strip() == account_id:
                return _parse_dollar(cells[1].inner_text())
        raise AssertionError(f"overview 页未找到账户 {account_id}")

    def get_account_ids(self):
        """返回总览表里的所有账户号列表（不包含表尾的 Total 行）。"""
        ids = []
        rows = self.page.locator(f"{self.ACCOUNT_TABLE} tbody tr").all()
        for row in rows:
            cells = row.locator("td").all()
            if not cells:
                continue
            first = cells[0].inner_text().strip()
            if first.isdigit():
                ids.append(first)
        return ids

    def account_count(self):
        return len(self.get_account_ids())
