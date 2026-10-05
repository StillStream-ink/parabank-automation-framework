"""项目根 conftest。

职责：
- 提供 UI 测试的 base_url
- 提供已登录的 page fixture
- Session 级 ParaBank 数据自动清理
- 生成 Allure 环境信息
"""
import os
import platform
import sys
from pathlib import Path

import pytest

os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from config.env_config import get_ui_url

# ==================== UI 基础 ====================

@pytest.fixture(scope="session")
def ui_base_url():
    return get_ui_url()


@pytest.fixture(scope="function")
def logged_in_page(page, ui_base_url):
    """前置 fixture：自动登录 ParaBank（john/demo），返回登录后的 page。"""
    page.goto(f"{ui_base_url}/index.htm")
    page.fill("input[name='username']", "john")
    page.fill("input[name='password']", "demo")
    page.click("input[type='submit']")
    page.wait_for_url("**/overview.htm")

    yield page

    # teardown：容错登出（页面可能已登出或已关闭）
    try:
        logout_link = page.locator("text=Log Out")
        if logout_link.count() > 0 and logout_link.is_visible():
            page.click("text=Log Out", timeout=3000)
            page.wait_for_load_state("networkidle", timeout=5000)
    except Exception:
        pass


# ==================== ParaBank 数据清理 ====================

@pytest.fixture(scope="session", autouse=True)
def parabank_cleanup():
    """Session 级别自动清理。

    - 若环境变量 PARABANK_CLEANUP=0，跳过清理（调试用）
    - Session 开始时清一次（保证起点干净）
    - Session 结束时清一次（恢复环境给下次跑）
    """
    from tests.finalize.clean_data import ParaBankCleaner

    if os.getenv("PARABANK_CLEANUP", "1") == "0":
        yield
        return

    cleaner = ParaBankCleaner()
    cleaner.reset()
    yield
    cleaner.reset()


# ==================== Allure 环境信息 ====================

@pytest.fixture(scope="session", autouse=True)
def _allure_environment():
    """生成 allure 报告首页的环境信息。"""
    env_file = Path("allure-results/environment.properties")
    env_file.parent.mkdir(parents=True, exist_ok=True)

    props = {
        "Python.Version": sys.version.split()[0],
        "Platform": platform.platform(),
        "OS": platform.system(),
        "Machine": platform.machine(),
        "Test.Framework": "pytest + requests + Playwright",
        "API.BaseURL": "http://localhost:8080/parabank/services/bank",
        "UI.BaseURL": "http://localhost:8080/parabank",
        "Target.System": "ParaBank 6.0.0-SNAPSHOT",
        "Runtime.JDK": "Zulu JDK 21 + Tomcat 11",
    }
    env_file.write_text(
        "\n".join(f"{k}={v}" for k, v in props.items()),
        encoding="utf-8",
    )

    # ========== 生成 categories.json ==========
    import json
    categories = [
        {
            "name": "✅ 通过 (Passed)",
            "matchedStatuses": ["passed"],
        },
        {
            "name": "🐛 已知漏洞守卫 (xfail)",
            "matchedStatuses": ["skipped"],
        },
        {
            "name": "❌ 产品缺陷 (Product Bugs)",
            "matchedStatuses": ["failed"],
            "messageRegex": ".*AssertionError.*",
        },
        {
            "name": "⚠️ 测试缺陷 / 环境问题 (Test Issues)",
            "matchedStatuses": ["broken"],
        },
    ]
    Path("allure-results/categories.json").write_text(
        json.dumps(categories, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # ========== 生成 executor.json ==========
    import os
    executor = {
        "name": "GitHub Actions" if os.getenv("GITHUB_ACTIONS") else "Local Execution",
        "type": "github" if os.getenv("GITHUB_ACTIONS") else "local",
        "buildName": os.getenv("GITHUB_RUN_NUMBER", "Local Run"),
        "reportUrl": "https://stillstream-ink.github.io/parabank-automation-framework/",
        "buildUrl": "https://github.com/StillStream-ink/parabank-automation-framework/actions",
    }
    Path("allure-results/executor.json").write_text(
        json.dumps(executor, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    yield
