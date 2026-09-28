import requests
BASE = "http://localhost:8080/parabank/services/bank"
AUTH = ("john", "demo")
ACC = "54321"
CUST = "12212"
TX = "12345"

tests = [
    ("登录",       "GET",  f"{BASE}/login/john/demo", None),
    ("客户信息",   "GET",  f"{BASE}/customers/{CUST}", None),
    ("按 ID 查交易","GET",  f"{BASE}/transactions/{TX}", None),
    ("按金额查交易","GET",  f"{BASE}/accounts/{ACC}/transactions/amount/50", None),
    ("按月+类型",  "GET",  f"{BASE}/accounts/{ACC}/transactions/month/All/type/All", None),
    ("按日期区间", "GET",  f"{BASE}/accounts/{ACC}/transactions/fromDate/01-01-2000/toDate/12-31-2030", None),
    ("存款",       "POST", f"{BASE}/deposit", {"accountId": ACC, "amount": "10"}),
    ("取款",       "POST", f"{BASE}/withdraw", {"accountId": ACC, "amount": "10"}),
]

for name, method, url, payload in tests:
    try:
        if method == "GET":
            r = requests.get(url, auth=AUTH, timeout=10)
        else:
            r = requests.post(url, params=payload, auth=AUTH, timeout=10)
        body = r.text[:150].replace("\n", " ")
        print(f"[{r.status_code}] {name:12} | {body}")
    except Exception as e:
        print(f"[ERR] {name:12} | {e}")
