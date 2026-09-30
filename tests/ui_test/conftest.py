"""UI 测试 fixtures。

包含：
- 环境变量控制 headless / slow_mo
- 每个用例自动开启 Playwright Trace，失败时保存 zip + 附加到 Allure
- 失败自动截图并附加到 Allure
"""
import os

import allure
import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """headless 决策：
    - HEADLESS=1 -> 无头
    - HEADLESS=0 -> 有头
    - 未设置 -> 检测 CI 环境（GitHub Actions 自动设 CI=true）-> 无头；本地有头
    """
    explicit = os.getenv("HEADLESS")
    if explicit is not None:
        headless = explicit == "1"
    else:
        headless = os.getenv("CI", "false").lower() == "true"

    return {
        **browser_type_launch_args,
        "headless": headless,
        "slow_mo": int(os.getenv("SLOW_MO", "0")),
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
    }


@pytest.fixture
def page(context, request):
    """覆盖 pytest-playwright 的 page fixture。

    手动控制 Trace：
    - 用例开始：tracing.start
    - 用例失败：保存 trace.zip 到 test-results/playwright/ + 附到 Allure
    - 用例成功：丢弃 trace
    - 无论成败，finally 保证 tracing.stop() 被调用（避免资源泄漏）
    """
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    pg = None
    try:
        pg = context.new_page()
        yield pg
    finally:
        # 无论是否异常，都要 stop + close
        failed = bool(getattr(request.node, "rep_call", None)
                      and request.node.rep_call.failed)

        os.makedirs("test-results/playwright", exist_ok=True)
        safe_name = (
            request.node.name
            .replace("/", "_")
            .replace(":", "_")
            .replace("[", "_")
            .replace("]", "_")
        )

        if failed:
            trace_path = f"test-results/playwright/{safe_name}-trace.zip"
            try:
                context.tracing.stop(path=trace_path)
                allure.attach.file(
                    trace_path,
                    name="Playwright Trace",
                    attachment_type=allure.attachment_type.ZIP,
                )
            except Exception:
                pass
        else:
            try:
                context.tracing.stop()
            except Exception:
                pass

        if pg is not None:
            try:
                pg.close()
            except Exception:
                pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(autouse=True)
def screenshot_on_failure(request, page):
    yield
    if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
        try:
            screenshot_bytes = page.screenshot(full_page=True)
            allure.attach(
                screenshot_bytes,
                name="用例失败-全屏截图",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass
