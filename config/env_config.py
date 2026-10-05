import os

from dotenv import load_dotenv

# 加载项目根目录下的 .env 文件
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)


def get_ui_url() -> str:
    """获取 UI 页面地址。"""
    return os.getenv("UI_BASE_URL", "http://localhost:8080/parabank")


def get_api_base_url() -> str:
    """获取 REST API 服务根路径。

    防御性处理：
    - 去掉结尾的 /
    - 若已包含 /services/bank，直接返回
    - 若结尾是历史遗留的 /api，去掉后再拼接
    """
    base = (os.getenv("API_BASE_URL") or "http://localhost:8080/parabank").rstrip("/")

    if base.endswith("/services/bank"):
        return base

    if base.endswith("/api"):
        base = base[:-4]

    return f"{base}/services/bank"
