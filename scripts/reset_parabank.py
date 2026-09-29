"""ParaBank 数据重置工具。

用法：
    py scripts/reset_parabank.py             # 默认：显示前后账户数 + 重置
    py scripts/reset_parabank.py --check     # 只查看当前账户数，不重置
    py scripts/reset_parabank.py --quiet     # 静默重置（只输出结果）
"""
import argparse
import sys
from pathlib import Path

# 把项目根加到 sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests.finalize.clean_data import ParaBankCleaner


def main():
    parser = argparse.ArgumentParser(
        description="ParaBank 数据重置工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--check", action="store_true", help="只检查当前状态，不重置")
    parser.add_argument("--quiet", "-q", action="store_true", help="静默模式")
    args = parser.parse_args()

    cleaner = ParaBankCleaner()

    if args.check:
        count = cleaner.account_count()
        print(f"当前账户数量: {count}")
        return 0

    before = cleaner.account_count()
    if not args.quiet:
        print(f"[before] 账户数量: {before}")

    ok = cleaner.reset()

    if not args.quiet:
        after = cleaner.account_count()
        print(f"[after ] 账户数量: {after}")

    print(f"[reset ] 结果: {'成功' if ok else '失败'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())