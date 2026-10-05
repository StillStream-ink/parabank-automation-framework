"""报告自动归档。

用法：
    py scripts/archive_report.py
    py scripts/archive_report.py --force        # 忽略去重，强制归档

行为：
- 把当前 allure-report/ + test-results/junit.xml 复制到 reports/YYYYMMDD_HHMMSS/
- 内容与最新一份归档相同则跳过（避免 CI 触发两次导致重复）
- 保留最近 N 份（默认 10），超出的自动删除
"""
import argparse
import hashlib
import shutil
import sys
from datetime import datetime
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(description="报告自动归档")
    p.add_argument("--keep", type=int, default=10, help="保留最近 N 份，默认 10")
    p.add_argument("--src-report", default="allure-report")
    p.add_argument("--src-junit", default="test-results/junit.xml")
    p.add_argument("--dst", default="reports")
    p.add_argument("--force", action="store_true", help="跳过去重检查，强制归档")
    return p.parse_args()


def _content_hash(report_dir: Path, junit_path: Path) -> str:
    """计算待归档内容的 hash。

    只关心内容，不关心 mtime / 文件名顺序。
    """
    h = hashlib.sha256()

    if junit_path.exists():
        h.update(b"=== junit ===\n")
        h.update(junit_path.read_bytes())

    if report_dir.exists():
        h.update(b"=== allure-report ===\n")
        for f in sorted(report_dir.rglob("*")):
            if f.is_file():
                # 相对路径 + 内容
                h.update(str(f.relative_to(report_dir)).encode("utf-8"))
                h.update(f.read_bytes())

    return h.hexdigest()


def _latest_archive_hash(dst_root: Path) -> str | None:
    """读最新一份归档里的 .content_hash 文件。不存在返回 None。"""
    if not dst_root.exists():
        return None
    archives = sorted(
        [d for d in dst_root.iterdir() if d.is_dir() and d.name[0].isdigit()],
        key=lambda d: d.name,
    )
    if not archives:
        return None
    hash_file = archives[-1] / ".content_hash"
    if hash_file.exists():
        return hash_file.read_text(encoding="utf-8").strip()
    return None


def main():
    args = parse_args()
    src_report = Path(args.src_report)
    src_junit = Path(args.src_junit)
    dst_root = Path(args.dst)

    if not src_report.exists() and not src_junit.exists():
        print("[ERROR] 没有可归档的产物")
        return 1

    # 计算当前内容 hash
    current_hash = _content_hash(src_report, src_junit)

    # 去重：与最新一份比较
    if not args.force:
        latest_hash = _latest_archive_hash(dst_root)
        if latest_hash == current_hash:
            print(f"[SKIP] 内容与最新归档一致，跳过（hash={current_hash[:12]}...）")
            print("       如需强制归档，加 --force")
            return 0

    # 归档
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst_dir = dst_root / timestamp
    dst_dir.mkdir(parents=True, exist_ok=True)

    if src_report.exists():
        shutil.copytree(src_report, dst_dir / "allure-report", dirs_exist_ok=True)
        print(f"[OK] Allure 报告 -> {dst_dir / 'allure-report'}")

    if src_junit.exists():
        shutil.copy2(src_junit, dst_dir / "junit.xml")
        print(f"[OK] JUnit XML  -> {dst_dir / 'junit.xml'}")

    # 写入 hash 供下次比对
    (dst_dir / ".content_hash").write_text(current_hash, encoding="utf-8")

    # 清理超出的旧归档
    all_archives = sorted(
        [d for d in dst_root.iterdir() if d.is_dir() and d.name[0].isdigit()],
        key=lambda d: d.name,
    )
    if len(all_archives) > args.keep:
        for old in all_archives[: len(all_archives) - args.keep]:
            shutil.rmtree(old)
            print(f"[DEL] 清理旧归档: {old.name}")

    print(f"\n归档完成：{dst_dir}")
    print(f"当前归档总数：{len(all_archives)} 份")
    return 0


if __name__ == "__main__":
    sys.exit(main())
