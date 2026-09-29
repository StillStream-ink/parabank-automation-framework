# ParaBank 自动化测试  一键运行脚本（Windows PowerShell）
param(
    [ValidateSet("all", "smoke", "regression", "api", "ui")]
    [string]$Scope = "all"
)

$ErrorActionPreference = "Stop"
chcp 65001 | Out-Null

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " ParaBank 自动化测试框架" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. 检查 ParaBank 是否在线
Write-Host "`n[1/5] 检查 ParaBank 是否在线..."
$code = curl.exe -s -o NUL -w "%{http_code}" -u john:demo `
    "http://localhost:8080/parabank/services/bank/customers/12212/accounts"
if ($code -ne "200") {
    Write-Host "ParaBank 未运行！请先启动：" -ForegroundColor Red
    Write-Host "   cd E:\parabank-master && mvn cargo:run"
    exit 1
}
Write-Host "ParaBank 在线" -ForegroundColor Green

# 2. 重置测试数据
Write-Host "`n[2/5] 重置测试数据..."
py scripts\reset_parabank.py --quiet

# 3. 执行测试
Write-Host "`n[3/5] 执行测试 (scope=$Scope)..."
switch ($Scope) {
    "smoke" {
        Write-Host "  运行 smoke 集（快速门禁，10 用例）" -ForegroundColor Yellow
        py -m pytest tests -m "smoke" -v
    }
    "regression" {
        py -m pytest tests -m "regression" -v
    }
    "api" {
        py -m pytest tests/api_test/scenarios/parabank -v
    }
    "ui" {
        py -m pytest tests/ui_test -v
    }
    default {
        Write-Host "  运行全量测试（129 用例，约 60 秒）" -ForegroundColor Yellow
        py -m pytest tests -q
    }
}

# 4. 生成 Allure 报告
Write-Host "`n[4/5] 生成 Allure 报告..."
allure generate allure-results --clean -o allure-report

# 5. 提示
Write-Host "`n[5/5] 完成！" -ForegroundColor Green
Write-Host ""
Write-Host "查看报告：" -ForegroundColor Cyan
Write-Host "   allure open allure-report"