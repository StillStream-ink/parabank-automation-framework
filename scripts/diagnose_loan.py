"""诊断 ParaBank 贷款页面 —— dump 真实 HTML + 每步状态。"""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8080/parabank"
OUT = Path("logs/loan_dump.html")
OUT.parent.mkdir(exist_ok=True)


def login(page):
    page.goto(f"{BASE}/index.htm")
    page.wait_for_load_state("networkidle")
    page.fill("input[name='username']", "john")
    page.fill("input[name='password']", "demo")
    page.click("input[value='Log In']")
    page.wait_for_load_state("networkidle")


def main():
    lines = []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1920, "height": 1080})
        page = ctx.new_page()

        lines.append("========== 1. 登录 ==========")
        login(page)
        lines.append(f"URL: {page.url}")

        lines.append("\n========== 2. 打开申请贷款页 ==========")
        page.goto(f"{BASE}/requestloan.htm")
        page.wait_for_load_state("networkidle")
        lines.append(f"URL: {page.url}")

        # 打印所有 input
        lines.append("\n--- 所有 <input> ---")
        for el in page.locator("input").all():
            html = el.evaluate("e => e.outerHTML")
            lines.append(html)

        # 打印所有 select
        lines.append("\n--- 所有 <select> ---")
        for el in page.locator("select").all():
            html = el.evaluate("e => e.outerHTML")
            lines.append(html)

        # 打印所有 iframe
        lines.append("\n--- 所有 <iframe> ---")
        iframes = page.locator("iframe").all()
        lines.append(f"共 {len(iframes)} 个 iframe")

        # 打印所有 form
        lines.append("\n--- 所有 <form> 的 action/method ---")
        for el in page.locator("form").all():
            action = el.get_attribute("action")
            method = el.get_attribute("method")
            lines.append(f"form action={action} method={method}")

        lines.append("\n========== 3. 尝试填表 ==========")
        try:
            page.fill("input[id='amount']", "1000")
            lines.append("fill input[id='amount'] -> OK")
        except Exception as e:
            lines.append(f"fill input[id='amount'] -> FAIL: {e}")

        # 确认填进去了
        try:
            val = page.input_value("input[id='amount']")
            lines.append(f"input[id='amount'] value = {val}")
        except Exception as e:
            lines.append(f"读 input value FAIL: {e}")

        try:
            page.fill("input[id='downPayment']", "200")
            val = page.input_value("input[id='downPayment']")
            lines.append(f"input[id='downPayment'] value = {val}")
        except Exception as e:
            lines.append(f"fill downPayment FAIL: {e}")

        try:
            page.locator("select[id='fromAccountId']").select_option("54321")
            val = page.locator("select[id='fromAccountId']").input_value()
            lines.append(f"select fromAccountId value = {val}")
        except Exception as e:
            lines.append(f"select FAIL: {e}")

        # 保存点击前 HTML
        (OUT.parent / "loan_before_click.html").write_text(
            page.content(), encoding="utf-8"
        )

        lines.append("\n========== 4. 点击 Apply Now ==========")
        url_before = page.url
        try:
            page.click("input[value='Apply Now']")
            page.wait_for_load_state("networkidle")
            lines.append(f"URL before click: {url_before}")
            lines.append(f"URL after  click: {page.url}")
        except Exception as e:
            lines.append(f"click FAIL: {e}")

        # 保存点击后 HTML
        (OUT.parent / "loan_after_click.html").write_text(
            page.content(), encoding="utf-8"
        )

        # 打印点击后 body 文本前 800 字
        body = page.locator("body").inner_text()
        lines.append("\n--- 点击后页面文本前 800 字 ---")
        lines.append(body[:800])

        b.close()

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"OK -> {OUT.resolve()}")
    print(f"HTML -> {OUT.parent / 'loan_before_click.html'}")
    print(f"HTML -> {OUT.parent / 'loan_after_click.html'}")


if __name__ == "__main__":
    main()