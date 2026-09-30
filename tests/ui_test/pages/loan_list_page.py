from tests.ui_test.pages.base_page import BasePage


class LoanListPage(BasePage):
    """ParaBank 账户总览页  可查询贷款信息（通过账户总览入口）"""

    ACCOUNT_OVERVIEW = "text=Accounts Overview"

    def navigate(self):
        super().navigate("overview.htm")
        self.page.wait_for_load_state("networkidle")

    def get_loan_section_text(self):
        """返回页面中包含 'loan' 关键字的正文文本（无则 None）。

        修复：
        - 原方法名 get_first_loan_record 名不副实（不解析具体记录，只返回 body 文本）
        - 删除了未使用的死代码 LOAN_TABLE
        """
        body_text = self.page.locator("body").inner_text()
        if "loan" in body_text.lower():
            return body_text
        return None

    # 兼容旧调用（推荐迁移到 get_loan_section_text）
    def get_first_loan_record(self):
        """[Deprecated] 请使用 get_loan_section_text()。"""
        return self.get_loan_section_text()

    def back_to_home(self):
        super().navigate("index.htm")
