import os
from dotenv import load_dotenv

# 加载项目根目录 .env 文件
load_dotenv()

def get_ui_url():
    # 从.env读取UI地址，没有就默认本地
    return os.getenv("UI_BASE_URL", "http://localhost:8080/parabank")

def get_api_url():
    return os.getenv("API_BASE_URL", "http://localhost:8080/parabank/api")
