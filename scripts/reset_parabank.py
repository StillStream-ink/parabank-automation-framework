"""手动重置 ParaBank 数据。用法：py scripts/reset_parabank.py"""
import sys
from pathlib import Path

# 把项目根加到 sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests.finalize.clean_data import ParaBankCleaner


def main():
    cleaner = ParaBankCleaner()
    before = cleaner.account_count()
    print(f"[before] 账户数量: {before}")

    ok = cleaner.reset()
    print(f"[reset ] 结果: {'成功' if ok else '失败'}")

    after = cleaner.account_count()
    print(f"[after ] 账户数量: {after}")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
