"""测试常量集中管理。

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
