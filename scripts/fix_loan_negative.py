"""临时脚本：修 test_loan_apply_negative_amount。"""
from pathlib import Path

f = Path("tests/api_test/scenarios/parabank/test_api_soap_parabank.py")
text = f.read_text(encoding="utf-8")

old = '''@pytest.mark.xfail(reason="BUG_LOAN_001 高危：ParaBank /requestLoan 未校验负数金额")
@allure.story("贷款-负数金额")
@allure.title("TC_PB_LOAN_003 贷款申请-传入负数金额")
def test_loan_apply_negative_amount(self):
    biz = ParaBankBiz(BASE_URL, USER_JOHN)
    resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
    root = ET.fromstring(resp_list.text)
    from_acc_id = root.find("account/id").text
    resp = biz.apply_loan(
        customer_id=CUSTOMER_ID_JOHN,
        amount=-1000,
        down_payment=100,
        from_account_id=from_acc_id,
    )
    assert resp.status_code != 200'''

new = '''@allure.story("贷款-负数金额")
@allure.title("TC_PB_LOAN_003 贷款申请-传入负数金额应被拒绝")
def test_loan_apply_negative_amount(self):
    biz = ParaBankBiz(BASE_URL, USER_JOHN)
    resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
    root = ET.fromstring(resp_list.text)
    from_acc_id = root.find("account/id").text
    resp = biz.apply_loan(
        customer_id=CUSTOMER_ID_JOHN,
        amount=-1000,
        down_payment=100,
        from_account_id=from_acc_id,
    )
    # ParaBank REST 用 body 里 approved 字段表示业务结果（HTTP 恒为 200）
    assert resp.status_code == 200
    assert "<approved>false</approved>" in resp.text.lower() or "approved>false<" in resp.text.lower(), \\
        f"负数贷款应被拒绝，实际响应: {resp.text[:300]}"'''

if old not in text:
    print(" 未找到待替换的代码段，请检查文件是否已是新版")
else:
    text = text.replace(old, new)
    f.write_text(text, encoding="utf-8")
    print(" test_loan_apply_negative_amount 已更新")
