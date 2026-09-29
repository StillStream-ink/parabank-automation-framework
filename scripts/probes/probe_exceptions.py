"""探测 ParaBank 对各种异常输入的响应。"""
import sys
import json
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

BASE = "http://localhost:8080/parabank/services/bank"
AUTH = ("john", "demo")
lines = []


def probe(label, method, path, **kwargs):
    url = f"{BASE}{path}"
    try:
        if method == "GET":
            r = requests.get(url, auth=AUTH, timeout=10, **kwargs)
        else:
            r = requests.post(url, auth=AUTH, timeout=10, **kwargs)
        body = r.text[:200].replace("\n", " ")
        lines.append(f"[{r.status_code}] {label}")
        lines.append(f"         URL: {method} {path}")
        lines.append(f"         BODY: {body!r}")
    except Exception as e:
        lines.append(f"[ERR] {label} -> {type(e).__name__}: {e}")
    lines.append("")


# ==================== 1. 非法参数类型 ====================

probe("转账金额传字符串 'abc'", "POST", "/transfer",
      params={"fromAccountId": "12345", "toAccountId": "12456", "amount": "abc"})

probe("转账金额传空字符串", "POST", "/transfer",
      params={"fromAccountId": "12345", "toAccountId": "12456", "amount": ""})

probe("转账 fromAccountId 传字符串", "POST", "/transfer",
      params={"fromAccountId": "abc", "toAccountId": "12456", "amount": 10})

probe("转账 fromAccountId 传负数", "POST", "/transfer",
      params={"fromAccountId": -1, "toAccountId": "12456", "amount": 10})

# ==================== 2. 缺失必填参数 ====================

probe("转账缺 amount 参数", "POST", "/transfer",
      params={"fromAccountId": "12345", "toAccountId": "12456"})

probe("转账缺 fromAccountId", "POST", "/transfer",
      params={"toAccountId": "12456", "amount": 10})

probe("转账所有参数都缺", "POST", "/transfer", params={})

# ==================== 3. 非法字符 / 注入 ====================

probe("转账金额传 SQL 注入", "POST", "/transfer",
      params={"fromAccountId": "12345", "toAccountId": "12456", "amount": "100 or 1=1 --"})

probe("转账金额传 XSS", "POST", "/transfer",
      params={"fromAccountId": "12345", "toAccountId": "12456", "amount": "<script>alert(1)</script>"})

probe("转账金额传中文", "POST", "/transfer",
      params={"fromAccountId": "12345", "toAccountId": "12456", "amount": "一百"})

probe("转账金额传超长字符串", "POST", "/transfer",
      params={"fromAccountId": "12345", "toAccountId": "12456", "amount": "9" * 1000})

# ==================== 4. 错误 HTTP 方法 ====================

probe("用 GET 调 /transfer（应为 POST）", "GET", "/transfer")

probe("用 GET 调 /deposit（应为 POST）", "GET", "/deposit")

# ==================== 5. 非法路径 ====================

probe("访问不存在的路径", "GET", "/no_such_endpoint")

probe("访问不存在的账户详情", "GET", "/accounts/99999999")

# ==================== 6. 超大 payload ====================

probe("存款金额传 1e100（超大数）", "POST", "/deposit",
      params={"accountId": "54321", "amount": "1e100"})

probe("存款金额传 NaN", "POST", "/deposit",
      params={"accountId": "54321", "amount": "NaN"})

probe("存款金额传 Infinity", "POST", "/deposit",
      params={"accountId": "54321", "amount": "Infinity"})

Path("logs/exception_probe.txt").write_text("\n".join(lines), encoding="utf-8")
print("OK -> logs/exception_probe.txt")