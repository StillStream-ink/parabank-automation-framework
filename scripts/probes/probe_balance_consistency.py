"""探测 ParaBank 转账/存款/取款前后余额变化行为。"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tests.api_test.business.parabank_biz import ParaBankBiz

BASE_URL = "http://localhost:8080/parabank/services/bank"
AUTH = ("john", "demo")

biz = ParaBankBiz(BASE_URL, AUTH)
lines = []


def get_balance(account_id):
    resp = biz.get_single_account_detail(account_id)
    if resp.status_code != 200:
        return None
    root = ET.fromstring(resp.text)
    return float(root.find("balance").text)


def probe(label, action_fn, check_accounts, expect=None):
    """执行 action_fn，前后对比指定账户的余额。"""
    before = {a: get_balance(a) for a in check_accounts}
    resp = action_fn()
    after = {a: get_balance(a) for a in check_accounts}

    lines.append(f"\n{'='*60}")
    lines.append(f"=== {label} ===")
    lines.append(f"HTTP: {resp.status_code} | body: {resp.text[:80]!r}")
    for a in check_accounts:
        delta = None if before[a] is None or after[a] is None else round(after[a] - before[a], 4)
        lines.append(f"  账户 {a}: {before[a]} -> {after[a]}  (delta = {delta})")


# ================== 转账 ==================

probe("转账 100（54321 -> 12345）",
      lambda: biz.transfer_funds("54321", "12345", 100),
      ["54321", "12345"])

probe("转账 0.01（54321 -> 12345）",
      lambda: biz.transfer_funds("54321", "12345", 0.01),
      ["54321", "12345"])

probe("转账 0（54321 -> 12345）",
      lambda: biz.transfer_funds("54321", "12345", 0),
      ["54321", "12345"])

probe("转账 -100（54321 -> 12345）",
      lambda: biz.transfer_funds("54321", "12345", -100),
      ["54321", "12345"])

probe("转账 999999999（54321 -> 12345）",
      lambda: biz.transfer_funds("54321", "12345", 999999999),
      ["54321", "12345"])

probe("转账 100（54321 -> 54321，自己转自己）",
      lambda: biz.transfer_funds("54321", "54321", 100),
      ["54321"])

# ================== 存款 ==================

probe("存款 100 到 54321",
      lambda: biz.deposit("54321", 100),
      ["54321"])

probe("存款 0.01 到 54321",
      lambda: biz.deposit("54321", 0.01),
      ["54321"])

probe("存款 0 到 54321",
      lambda: biz.deposit("54321", 0),
      ["54321"])

probe("存款 -100 到 54321",
      lambda: biz.deposit("54321", -100),
      ["54321"])

# ================== 取款 ==================

probe("取款 100 从 54321",
      lambda: biz.withdraw("54321", 100),
      ["54321"])

probe("取款 0.01 从 54321",
      lambda: biz.withdraw("54321", 0.01),
      ["54321"])

probe("取款 0 从 54321",
      lambda: biz.withdraw("54321", 0),
      ["54321"])

probe("取款 -100 从 54321",
      lambda: biz.withdraw("54321", -100),
      ["54321"])

probe("取款 999999999 从 54321（超额）",
      lambda: biz.withdraw("54321", 999999999),
      ["54321"])

Path("logs/balance_consistency_probe.txt").write_text("\n".join(lines), encoding="utf-8")
print("OK -> logs/balance_consistency_probe.txt")
