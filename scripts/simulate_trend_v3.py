"""用 smoke 集模拟趋势图（修复：模拟失败也加 smoke 标记）。"""
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIM_FILE = ROOT / "tests" / "test_simulated_failures.py"
RESULTS_DIR = ROOT / "allure-results"
REPORT_DIR = ROOT / "allure-report"
HISTORY_DIR = RESULTS_DIR / "history"


def run(cmd):
    subprocess.run(cmd, cwd=ROOT, check=False, shell=True)


def create_failures(n):
    """生成 n 个失败的 smoke 用例。"""
    if n <= 0:
        if SIM_FILE.exists():
            SIM_FILE.unlink()
        return
    content = '''"""模拟失败用例（跑完自动删除）。"""
import pytest

pytestmark = pytest.mark.smoke

'''
    for i in range(1, n + 1):
        content += f'def test_simulated_failure_{i}():\n    assert False, "模拟回归 #{i}"\n\n'
    SIM_FILE.write_text(content, encoding="utf-8")


def main():
    scenarios = [5, 2, 0, 0]
    labels = ["严重回归：5 个失败", "部分修复：2 个失败", "全部修复", "稳定验证"]

    if RESULTS_DIR.exists():
        shutil.rmtree(RESULTS_DIR)
    RESULTS_DIR.mkdir(parents=True)

    try:
        for i, (n, label) in enumerate(zip(scenarios, labels), 1):
            print(f"\n{'='*60}")
            print(f"[{i}/{len(scenarios)}] {label}")
            print(f"{'='*60}")

            create_failures(n)

            # 清理（保留 history）
            for item in RESULTS_DIR.iterdir():
                if item.name == "history":
                    continue
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()

            run("py scripts/reset_parabank.py --quiet")
            run("py -m pytest tests -m smoke -q --alluredir=allure-results")
            run("allure generate allure-results --clean -o allure-report")

            src = REPORT_DIR / "history"
            if src.exists():
                if HISTORY_DIR.exists():
                    shutil.rmtree(HISTORY_DIR)
                shutil.copytree(src, HISTORY_DIR)

        print("\n完成！")
        print(f"打开报告：allure open {REPORT_DIR}")
    finally:
        if SIM_FILE.exists():
            SIM_FILE.unlink()


if __name__ == "__main__":
    main()