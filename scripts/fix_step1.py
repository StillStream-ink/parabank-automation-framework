"""Step 1: 集中配置 + HTTP timeout 修复。

修复问题：
- C-01 硬编码 BASE_URL / 账号
- M-05 HTTP 请求缺 timeout
"""
from pathlib import Path
import re

# ========== 1.1 加 get_api_base_url ==========
f = Path("config/env_config.py")
text = f.read_text(encoding="utf-8")
if "get_api_base_url" not in text:
    text = text.rstrip() + '''


def get_api_base_url():
    """获取 REST API 服务根路径（含 /services/bank）。"""
    base = os.getenv("API_BASE_URL") or "http://localhost:8080/parabank"
    return f"{base.rstrip('/')}/services/bank"
'''
    f.write_text(text, encoding="utf-8")
    print("[OK] env_config.py 已加 get_api_base_url")
else:
    print("[SKIP] env_config.py 已有 get_api_base_url")


# ========== 1.2 创建 config/test_constants.py ==========
tc = Path("config/test_constants.py")
tc.write_text('''"""测试常量集中管理。

所有测试文件从这里 import，避免硬编码。
"""
from config.env_config import get_api_base_url, get_ui_url

# ============ 基础地址 ============
BASE_URL = get_api_base_url()
UI_BASE_URL = get_ui_url() or "http://localhost:8080/parabank"

# ============ 测试账号 ============
USER_JOHN = ("john", "demo")
CUSTOMER_ID_JOHN = "12212"

# ============ 常用账户 ============
ACC_A = "54321"
ACC_B = "12345"

# ============ 超时 ============
DEFAULT_TIMEOUT = 15
''', encoding="utf-8")
print("[OK] config/test_constants.py 已创建")


# ========== 1.3 重写 base_api.py ==========
ba = Path("tests/api_test/services/base_api.py")
ba.write_text('''import requests


class BaseApi:
    """HTTP 请求封装（带默认超时）。"""

    DEFAULT_TIMEOUT = 15

    def __init__(self, base_url, auth=None, timeout=None):
        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.session = requests.Session()

    def _prepare(self, kwargs):
        kwargs.setdefault("timeout", self.timeout)
        if self.auth and "auth" not in kwargs:
            kwargs["auth"] = self.auth
        return kwargs

    def get(self, path, params=None, **kwargs):
        url = self.base_url + path
        return self.session.get(url, params=params, **self._prepare(kwargs))

    def post(self, path, json_data=None, **kwargs):
        url = self.base_url + path
        return self.session.post(url, json=json_data, **self._prepare(kwargs))

    def put(self, path, json_data=None, **kwargs):
        url = self.base_url + path
        return self.session.put(url, json=json_data, **self._prepare(kwargs))

    def delete(self, path, **kwargs):
        url = self.base_url + path
        return self.session.delete(url, **self._prepare(kwargs))
''', encoding="utf-8")
print("[OK] base_api.py 已重写（带 timeout）")


# ========== 1.4 parabank_biz.py 加 timeout ==========
pb = Path("tests/api_test/business/parabank_biz.py")
text = pb.read_text(encoding="utf-8")

if "DEFAULT_TIMEOUT" in text:
    print("[SKIP] parabank_biz.py 已有 timeout")
else:
    old_init = '''    def __init__(self, base_url, auth=None):
        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self.session = requests.Session()'''
    new_init = '''    DEFAULT_TIMEOUT = 15

    def __init__(self, base_url, auth=None, timeout=None):
        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.session = requests.Session()'''
    if old_init in text:
        text = text.replace(old_init, new_init, 1)
        print("[OK] parabank_biz.py __init__ 加 timeout")
    else:
        print("[WARN] __init__ 结构不符，跳过")

    old_req = '''    def _do_request(self, method, url, **kwargs):
        return self.session.request(method, url, **kwargs)'''
    new_req = '''    def _do_request(self, method, url, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        return self.session.request(method, url, **kwargs)'''
    if old_req in text:
        text = text.replace(old_req, new_req, 1)
        print("[OK] parabank_biz.py _do_request 加 timeout")
    else:
        print("[WARN] _do_request 结构不符")

    pb.write_text(text, encoding="utf-8")


# ========== 1.5 批量替换 8 个测试文件的硬编码 ==========
FILES = [
    "tests/api_test/scenarios/parabank/test_api_balance_consistency.py",
    "tests/api_test/scenarios/parabank/test_api_boundary_param.py",
    "tests/api_test/scenarios/parabank/test_api_contract.py",
    "tests/api_test/scenarios/parabank/test_api_deposit_withdraw.py",
    "tests/api_test/scenarios/parabank/test_api_exceptions.py",
    "tests/api_test/scenarios/parabank/test_api_login_customer.py",
    "tests/api_test/scenarios/parabank/test_api_soap_parabank.py",
    "tests/api_test/scenarios/parabank/test_api_transaction_query.py",
]

IMPORT_LINE = "from config.test_constants import BASE_URL, USER_JOHN, CUSTOMER_ID_JOHN, ACC_A, ACC_B"

PATTERNS = [
    re.compile(r'^BASE_URL\s*=\s*["\'].*?["\']\s*$', re.MULTILINE),
    re.compile(r'^USER_JOHN\s*=\s*\(.*?\)\s*$', re.MULTILINE),
    re.compile(r'^CUSTOMER_ID_JOHN\s*=\s*["\'].*?["\']\s*$', re.MULTILINE),
    re.compile(r'^ACC_A\s*=\s*["\'].*?["\']\s*$', re.MULTILINE),
    re.compile(r'^ACC_B\s*=\s*["\'].*?["\']\s*$', re.MULTILINE),
]

print()
print("=" * 60)
for rel in FILES:
    fp = Path(rel)
    if not fp.exists():
        print(f"[MISS] {rel}")
        continue
    text = fp.read_text(encoding="utf-8")

    if "from config.test_constants import" in text:
        print(f"[SKIP] {fp.name} 已 import")
        continue

    removed = 0
    for p in PATTERNS:
        text, n = p.subn("", text)
        removed += n

    # 在最后一个 import 后插入
    lines = text.split("\n")
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            insert_at = i + 1
    lines.insert(insert_at, "")
    lines.insert(insert_at + 1, IMPORT_LINE)

    text = "\n".join(lines)
    fp.write_text(text, encoding="utf-8")
    print(f"[OK]   {fp.name} 删 {removed} 行 + 加 import")

print("=" * 60)
print("Step 1 完成")
