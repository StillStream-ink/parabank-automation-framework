"""全量 129 用例 + 大比例失败，生成真实趋势图。

场景：
    第 1 轮：30 个模拟失败
    第 2 轮：10 个模拟失败
    第 3 轮：0 个（全通过）
    第 4 轮：0 个（稳定验证）

用法：py scripts/simulate_trend_full.py
"""
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
    if n <= 0:
        if SIM_FILE.exists():
            SIM_FILE.unlink()
        return
    content = '"""模拟失败用例（跑完自动删除）。"""\n\n'
    for i in range(1, n + 1):
        content += f'def test_simulated_failure_{i}():\n    assert False, "模拟回归 #{i}"\n\n'
    SIM_FILE.write_text(content, encoding="utf-8")


def main():
    scenarios = [30, 10, 0, 0]
    labels = ["严重回归：30 个失败", "部分修复：10 个失败", "全部修复", "稳定验证"]

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
            run("py -m pytest tests -q --alluredir=allure-results")
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