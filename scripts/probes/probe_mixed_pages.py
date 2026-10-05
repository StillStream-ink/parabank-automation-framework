"""探测 ParaBank overview / transfer 页，用于混合场景设计。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from playwright.sync_api import sync_playwright

BASE = "http://localhost:8080/parabank"
OUT = Path("logs/mixed_page_probe.txt")


def login(page):
    page.goto(f"{BASE}/index.htm")
    page.wait_for_load_state("networkidle")
    page.fill("input[name='username']", "john")
    page.fill("input[name='password']", "demo")
    page.click("input[value='Log In']")
    page.wait_for_load_state("networkidle")


def dump(page, url, label):
    lines = [f"\n{'='*60}", f"=== {label} ===", f"URL: {url}"]
    page.goto(url)
    page.wait_for_load_state("networkidle")
    lines.append(f"最终 URL: {page.url}")

    lines.append("\n--- <input> ---")
    for el in page.locator("input").all():
        lines.append(el.evaluate("e => e.outerHTML"))

    lines.append("\n--- <select> ---")
    for el in page.locator("select").all():
        lines.append(el.evaluate("e => e.outerHTML"))

    lines.append("\n--- <button> / <input type=button|submit> ---")
    for el in page.locator("button, input[type=submit], input[type=button]").all():
        lines.append(el.evaluate("e => e.outerHTML"))

    # 关键：看账户总览页有没有账户列表表格
    lines.append("\n--- Body 前 800 字 ---")
    lines.append(page.locator("body").inner_text()[:800])

    # 提取所有 <table> 的 id / class
    lines.append("\n--- 所有 <table> id/class ---")
    for el in page.locator("table").all():
        tid = el.get_attribute("id") or ""
        tclass = el.get_attribute("class") or ""
        lines.append(f"table id={tid!r} class={tclass!r}")

    return lines


def main():
    lines = []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1920, "height": 1080})
        page = ctx.new_page()

        login(page)
        lines.append("登录成功")

        lines.extend(dump(page, f"{BASE}/overview.htm", "账户总览页 overview"))
        lines.extend(dump(page, f"{BASE}/transfer.htm", "转账页 transfer"))

        b.close()

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"OK -> {OUT.resolve()}")


if __name__ == "__main__":
    main()
