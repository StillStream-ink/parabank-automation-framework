from dotenv import load_dotenv
import os

# 获取当前文件的上级目录（项目根目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

def get_base_url():
    """获取API接口地址"""
    return os.getenv("API_BASE_URL")

def get_ui_url():
    """获取UI页面地址"""
    return os.getenv("UI_BASE_URL")

def get_db_config():
    """数据库配置，返回字典"""
    return {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "db_name": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PWD")
    }


def get_api_base_url():
    """获取 REST API 服务根路径。

    防御性处理：
    - 去掉结尾 /
    - 若已包含 /services/bank，直接返回
    - 若包含 /api（旧配置），先去掉
    - 最后拼上 /services/bank
    """
    base = (os.getenv("API_BASE_URL") or "http://localhost:8080/parabank").rstrip("/")

    # 已经带完整路径
    if base.endswith("/services/bank"):
        return base

    # 去掉尾部的 /api（历史遗留配置）
    if base.endswith("/api"):
        base = base[:-4]

    return f"{base}/services/bank"
