#!/bin/bash
# ParaBank 自动化测试  一键运行脚本（Bash / Git Bash / Linux）
set -e

echo "=========================================="
echo " ParaBank 自动化测试框架"
echo "=========================================="

# 1. 检查被测系统是否在线
echo ""
echo "[1/5] 检查 ParaBank 是否在线..."
if ! curl -s -o /dev/null -w "%{http_code}" -u john:demo \
     "http://localhost:8080/parabank/services/bank/customers/12212/accounts" \
     | grep -q "200"; then
    echo " ParaBank 未运行！请先启动："
    echo "   cd /path/to/parabank-master && mvn cargo:run"
    exit 1
fi
echo " ParaBank 在线"

# 2. 重置测试数据
echo ""
echo "[2/5] 重置测试数据..."
py scripts/reset_parabank.py --quiet || python scripts/reset_parabank.py --quiet

# 3. 参数决定测试范围
SCOPE="${1:-all}"   # all / smoke / regression / api / ui

case "$SCOPE" in
    smoke)
        echo ""
        echo "[3/5] 运行 smoke 集（快速门禁）..."
        py -m pytest tests -m "smoke" -v
        ;;
    regression)
        echo ""
        echo "[3/5] 运行 regression 集..."
        py -m pytest tests -m "regression" -v
        ;;
    api)
        echo ""
        echo "[3/5] 运行 API 层..."
        py -m pytest tests/api_test/scenarios/parabank -v
        ;;
    ui)
        echo ""
        echo "[3/5] 运行 UI 层..."
        py -m pytest tests/ui_test -v
        ;;
    *)
        echo ""
        echo "[3/5] 运行全量测试（129 用例，约 60 秒）..."
        py -m pytest tests -q
        ;;
esac

# 4. 生成 Allure 报告
echo ""
echo "[4/5] 生成 Allure 报告..."
allure generate allure-results --clean -o allure-report

# 5. 提示
echo ""
echo "[5/5] 完成！"
echo ""
echo "查看报告："
echo "   allure open allure-report"
echo ""