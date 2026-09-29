"""抓取 ParaBank 关键接口响应样本，用于设计契约。"""
import sys
from pathlib import Path

# 把项目根加到 sys.path（从 scripts/ 运行时必需）
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tests.api_test.business.parabank_biz import ParaBankBiz

BASE_URL = "http://localhost:8080/parabank/services/bank"
AUTH = ("john", "demo")

biz = ParaBankBiz(BASE_URL, AUTH)
lines = []


def dump(name, resp, maxlen=1200):
    lines.append(f"\n{'='*60}")
    lines.append(f"=== {name} ===")
    lines.append(f"HTTP {resp.status_code}")
    lines.append(resp.text[:maxlen])


dump("登录", biz.login("john", "demo"))
dump("客户信息", biz.get_customer("12212"))
dump("账户列表", biz.get_customer_account_list("12212"))
dump("账户详情", biz.get_single_account_detail("54321"))
dump("交易流水", biz.get_account_transactions("54321"))
dump("交易按 ID", biz.get_transaction_by_id("12700"))
dump("贷款响应", biz.apply_loan("12212", 1000, 100, "54321"))
dump("账单响应", biz.pay_bill("54321", 10))

Path("logs/contract_samples.txt").write_text("\n".join(lines), encoding="utf-8")
print("OK -> logs/contract_samples.txt")