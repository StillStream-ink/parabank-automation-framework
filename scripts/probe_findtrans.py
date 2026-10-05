"""探测 ParaBank 交易查询页在"有结果"/"无结果"时的真实文本。"""
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://localhost:8080/parabank"
OUT = Path("logs/findtrans_dump.txt")


def login(page):
    page.goto(f"{BASE}/index.htm")
    page.wait_for_load_state("networkidle")
    page.fill("input[name='username']", "john")
    page.fill("input[name='password']", "demo")
    page.click("input[type='submit']")
    page.wait_for_url("**/overview.htm")


def dump_after_query(page, label):
    page.wait_for_load_state("networkidle")
    # 取 body 文本
    body = page.locator("body").inner_text()
    # 取页面主区域 HTML（右半部分）
    main_html = page.locator("#rightPanel").inner_html() if page.locator("#rightPanel").count() > 0 else "（找不到 #rightPanel）"

    lines = [
        f"\n{'='*60}",
        f"=== {label} ===",
        f"URL: {page.url}",
        "\n--- Body 文本（前 1500 字）---",
        body[:1500],
        "\n--- #rightPanel HTML（前 2000 字）---",
        main_html[:2000],
    ]
    return lines


def main():
    lines = []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1920, "height": 1080})
        page = ctx.new_page()

        login(page)
        lines.append("登录成功")

        # 查询 1：不存在的交易 ID
        page.goto(f"{BASE}/findtrans.htm")
        page.wait_for_load_state("networkidle")
        page.locator("select#accountId").select_option("54321")
        page.fill("input#transactionId", "99999999")
        page.click("button#findById")
        lines.extend(dump_after_query(page, "查询不存在的交易 ID（99999999）"))

        # 查询 2：不存在的金额
        page.goto(f"{BASE}/findtrans.htm")
        page.wait_for_load_state("networkidle")
        page.locator("select#accountId").select_option("54321")
        page.fill("input#amount", "999999")
        page.click("button#findByAmount")
        lines.extend(dump_after_query(page, "查询不存在的金额（999999）"))

        # 查询 3：合法金额（应有结果）
        page.goto(f"{BASE}/findtrans.htm")
        page.wait_for_load_state("networkidle")
        page.locator("select#accountId").select_option("54321")
        page.fill("input#amount", "1000")
        page.click("button#findByAmount")
        lines.extend(dump_after_query(page, "查询合法金额（1000）"))

        b.close()

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"OK -> {OUT.resolve()}")


if __name__ == "__main__":
    main()
