"""质量门禁脚本。

用法：
    py scripts/quality_gate.py                  # 默认阈值 90%
    py scripts/quality_gate.py --threshold 85   # 自定义阈值
    py scripts/quality_gate.py --no-dedup       # 不去重（默认去重）

逻辑：
    passed / (passed + failed + broken) >= threshold
    - xfail / skipped 不计入分母
    - 按 historyId 去重，保留最新一轮（避免历史累积）
    - 缺少 allure-results 时给出明确提示
"""
import argparse
import json
import sys
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(description="ParaBank 测试质量门禁")
    p.add_argument("--threshold", type=float, default=90.0,
                   help="通过率阈值（%%），默认 90")
    p.add_argument("--results-dir", default="allure-results",
                   help="allure 结果目录")
    p.add_argument("--no-dedup", action="store_true",
                   help="不去重（默认按 historyId 保留最新一轮）")
    return p.parse_args()


def collect_stats(results_dir: Path, dedup: bool = True) -> dict:
    """遍历 allure-results 里的 *-result.json，统计状态。"""
    stats = {"passed": 0, "failed": 0, "broken": 0,
             "skipped": 0, "unknown": 0}

    if not results_dir.exists():
        print(f"[ERROR] 结果目录不存在: {results_dir}")
        sys.exit(2)

    files = list(results_dir.glob("*-result.json"))
    if not files:
        print("[ERROR] 结果目录里没有 *-result.json")
        sys.exit(2)

    # 读取全部
    records = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            records.append(data)
        except Exception:
            stats["unknown"] += 1

    total_raw = len(records)

    # 去重：按 historyId 保留 start 最大的一条（最新一轮）
    if dedup:
        key_to_latest = {}
        for r in records:
            key = r.get("historyId") or r.get("fullName") or r.get("uuid")
            start = r.get("start", 0) or 0
            if key not in key_to_latest or start > (key_to_latest[key].get("start", 0) or 0):
                key_to_latest[key] = r
        records = list(key_to_latest.values())

    total_dedup = len(records)

    # 统计
    for r in records:
        status = r.get("status", "unknown")
        if status == "passed":
            stats["passed"] += 1
        elif status == "failed":
            stats["failed"] += 1
        elif status == "broken":
            stats["broken"] += 1
        elif status == "skipped":
            stats["skipped"] += 1
        else:
            stats["unknown"] += 1

    stats["_total_raw"] = total_raw
    stats["_total_dedup"] = total_dedup
    return stats


def main():
    args = parse_args()
    stats = collect_stats(Path(args.results_dir), dedup=not args.no_dedup)

    total_effective = stats["passed"] + stats["failed"] + stats["broken"]
    total_all = sum(v for k, v in stats.items() if not k.startswith("_"))

    if total_effective == 0:
        print("[ERROR] 有效用例数为 0，无法计算通过率")
        print(f"统计: {stats}")
        sys.exit(2)

    pass_rate = stats["passed"] / total_effective * 100

    print("=" * 60)
    print("  ParaBank 测试质量门禁")
    print("=" * 60)
    if not args.no_dedup:
        print(f"  原始文件数:    {stats['_total_raw']}   (去重后 {stats['_total_dedup']})")
    print(f"  总用例:        {total_all}")
    print(f"  有效用例:      {total_effective}  (不含 skipped)")
    print(f"   passed:     {stats['passed']}")
    print(f"   failed:     {stats['failed']}")
    print(f"   broken:     {stats['broken']}")
    print(f"  非阻塞:        skipped={stats['skipped']}  unknown={stats['unknown']}")
    print("-" * 60)
    print(f"  通过率:        {pass_rate:.2f}%")
    print(f"  阈值:          {args.threshold}%")
    print("=" * 60)

    if pass_rate >= args.threshold:
        print("  [PASS] 质量门禁通过")
        return 0
    else:
        print(f"  [FAIL] 质量门禁未通过（差 {args.threshold - pass_rate:.2f}%）")
        return 1


if __name__ == "__main__":
    sys.exit(main())
