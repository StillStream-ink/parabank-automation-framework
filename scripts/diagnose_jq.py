from playwright.sync_api import sync_playwright

BASE = "http://localhost:8080/parabank"

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))

    # ============ 先登录 ============
    page.goto(f"{BASE}/index.htm")
    page.wait_for_load_state("networkidle")
    page.fill("input[name='username']", "john")
    page.fill("input[name='password']", "demo")
    page.click("input[value='Log In']")
    page.wait_for_load_state("networkidle")
    print("登录后 URL:", page.url)

    # ============ 再进贷款页 ============
    page.goto(f"{BASE}/requestloan.htm")
    page.wait_for_load_state("networkidle")
    print("贷款页 URL:", page.url)

    print("typeof jQuery  =", page.evaluate("typeof jQuery"))
    print("jQuery.version =", page.evaluate("typeof jQuery !== 'undefined' ? jQuery.fn.jquery : 'NOT_LOADED'"))
    print("btn 存在?      =", page.evaluate("!!document.querySelector('input[type=button]')"))
    print("btn 的 jQuery 事件 =", page.evaluate("typeof jQuery !== 'undefined' && jQuery._data(document.querySelector('input[type=button]'), 'events') ? 'HAS_EVENTS' : 'NO_EVENTS'"))
    print("script srcs    =", page.evaluate("Array.from(document.scripts).map(s => s.src)"))
    print("pageerrors     =", errors)

    # 手动触发点击，看有没有反应
    print("\n--- 尝试程序化点击 ---")
    page.fill("input[id='amount']", "1000")
    page.fill("input[id='downPayment']", "200")
    page.locator("select[id='fromAccountId']").select_option("54321")
    page.evaluate("document.querySelector('input[type=button]').click()")
    page.wait_for_timeout(3000)
    print("点击后 URL:", page.url)
    print("Result 显示?  =", page.evaluate("document.querySelector('#requestLoanResult').style.display"))
    print("Status 内容   =", page.evaluate("document.querySelector('#loanStatus').innerText"))

    b.close()
