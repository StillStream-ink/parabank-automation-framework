"""探测 ParaBank 未覆盖页面的真实 HTML：开户/账单支付/账户详情/登出。"""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8080/parabank"
OUT = Path("logs/ui_pages_a.txt")


def login(page):
    page.goto(f"{BASE}/index.htm")
    page.wait_for_load_state("networkidle")
    page.fill("input[name='username']", "john")
    page.fill("input[name='password']", "demo")
    page.click("input[value='Log In']")
    page.wait_for_load_state("networkidle")


def dump_page(page, url, label):
    lines = [f"\n{'='*60}", f"========== {label} ==========", f"URL: {url}"]
    page.goto(url)
    page.wait_for_load_state("networkidle")
    lines.append(f"最终 URL: {page.url}")

    # input
    lines.append("\n--- <input> ---")
    for el in page.locator("input").all():
        lines.append(el.evaluate("e => e.outerHTML"))

    # select
    lines.append("\n--- <select> ---")
    for el in page.locator("select").all():
        lines.append(el.evaluate("e => e.outerHTML"))

    # button / submit
    lines.append("\n--- <button> / <input type=submit|button> ---")
    for el in page.locator("button, input[type=submit], input[type=button]").all():
        lines.append(el.evaluate("e => e.outerHTML"))

    # form
    lines.append("\n--- <form> ---")
    for el in page.locator("form").all():
        lines.append(el.evaluate("e => e.outerHTML"))

    # body 前 500 字（看整体结构）
    lines.append("\n--- Body 前 500 字 ---")
    lines.append(page.locator("body").inner_text()[:500])

    return lines


def main():
    lines = []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1920, "height": 1080})
        page = ctx.new_page()

        login(page)
        lines.append("登录成功")

        pages = [
            ("https://example.com", ""),   # 占位，下面替换
        ]

        # 1. 开户页
        lines.extend(dump_page(page, f"{BASE}/openaccount.htm", "开户页 openaccount"))

        # 2. 账单支付页
        lines.extend(dump_page(page, f"{BASE}/billpay.htm", "账单支付页 billpay"))

        # 3. 账户详情页（以 54321 为例）
        lines.extend(dump_page(page, f"{BASE}/activity.htm?id=54321", "账户详情页 activity"))

        # 4. 登出页
        lines.extend(dump_page(page, f"{BASE}/logout.htm", "登出页 logout"))

        b.close()

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"OK -> {OUT.resolve()}")


if __name__ == "__main__":
    main()