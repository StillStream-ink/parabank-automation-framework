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
