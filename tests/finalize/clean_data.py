"""ParaBank 测试数据清理。

核心策略：调用官方 /initializeDB 接口，将数据库重置为初始状态。
"""
import logging

import allure
import requests

from config.env_config import get_ui_url

log = logging.getLogger(__name__)


class ParaBankCleaner:
    """ParaBank 数据清理器。"""

    def __init__(self, base_url=None, auth=("john", "demo")):
        # base_url 形如 http://localhost:8080/parabank/services/bank
        self.base_url = (base_url or self._default_base_url()).rstrip("/")
        self.auth = auth

    @staticmethod
    def _default_base_url():
        """从 .env 推导 REST 服务根路径。"""
        ui_base = get_ui_url() or "http://localhost:8080/parabank"
        return f"{ui_base.rstrip('/')}/services/bank"

    def reset(self):
        """调用 initializeDB 重置数据。返回 True 表示成功。"""
        url = f"{self.base_url}/initializeDB"
        try:
            with allure.step(f"重置 ParaBank 数据：POST {url}"):
                resp = requests.post(url, auth=self.auth, timeout=15)
            if resp.status_code in (200, 204):
                log.info("[cleanup] ParaBank 数据已重置 (HTTP %s)", resp.status_code)
                return True
            log.warning(
                "[cleanup] 重置失败：HTTP %s body=%s",
                resp.status_code, resp.text[:200],
            )
            return False
        except Exception as e:
            log.warning("[cleanup] 重置异常：%s", e)
            return False

    def account_count(self, customer_id="12212"):
        """返回当前客户名下的账户数量，用于验证清理效果。"""
        url = f"{self.base_url}/customers/{customer_id}/accounts"
        try:
            resp = requests.get(url, auth=self.auth, timeout=10)
            if resp.status_code != 200:
                return -1
            return resp.text.count("<account>")
        except Exception:
            return -1
