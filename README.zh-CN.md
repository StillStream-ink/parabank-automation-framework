# ParaBank 自动化测试框架

[English](./README.md) | **简体中文**

[![CI](https://github.com/StillStream-ink/parabank-automation-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/StillStream-ink/parabank-automation-framework/actions)
[![Pytest](https://img.shields.io/badge/Pytest-7.4-green)](https://docs.pytest.org/)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.40-brightgreen)](https://playwright.dev/)
[![Allure](https://img.shields.io/badge/Allure-2.x-orange)](https://docs.qameta.io/allure/)

> 📊 **在线测试报告**：<https://stillstream-ink.github.io/parabank-automation-framework/>
>
> 基于 **pytest + requests + Playwright + pydantic** 的 ParaBank 全栈自动化测试框架。
> 覆盖 **API 接口 + Web UI + 混合场景**，包含 **契约校验 / 数据一致性 / 参数化边界 / 异常注入**。

***

## 📊 项目数据总览

| 指标           | 数值        |
| ------------ | --------- |
| 📝 测试用例总数    | 129       |
| ✅ 通过率（有效）    | 100%      |
| 🛡 已知漏洞守卫    | 43        |
| 🐛 独立漏洞数     | 16        |
| ⏱ 全量执行时间     | \~120 秒   |
| 🎯 smoke 集时间 | \~10 秒    |
| ⭐ 测试评分       | 20.0 / 20 |

***

## 📑 目录

*   [✨ 核心亮点](#-核心亮点)
*   [🛠 技术栈](#-技术栈)
*   [📂 项目结构](#-项目结构)
*   [🚀 快速开始](#-快速开始)
*   [🧪 用例设计思路](#-用例设计思路)
*   [🔍 已发现漏洞](#-已发现漏洞)
*   [⚙️ 工程化能力](#️-工程化能力)
*   [🔗 相关文档](#-相关文档)

***

## ✨ 核心亮点

### 测试能力

*   **双层覆盖**：API 层（pytest + requests）+ UI 层（Playwright + POM）
*   **混合场景**：API 造数据 + UI 验证 / UI 操作 + API 校验 / 三段式端到端
*   **契约校验**：pydantic 模型验证响应字段名/类型/必填
*   **数据一致性**：转账/存款/取款前后余额**精确到分**校验
*   **参数化边界**：0 / 负数 / 超额 / 精度全覆盖
*   **异常场景**：非法参数 / 缺失参数 / 特殊字符 / 超大数值 / 协议层异常

### 工程化

*   **CI/CD**：GitHub Actions 自动构建 ParaBank + 跑测试 + 部署 Allure 报告
*   **质量门禁**：通过率 < 90% 阻断 CI；xfail 不计入分母，按 historyId 去重
*   **HTTP 重试**：tenacity 自动重试（网络异常 + 5xx，3 次退避；4xx 不重试）
*   **报告归档**：每次跑完归档到 `reports/YYYYMMDD_HHMMSS/`
*   **测试评分**：通过率 / 用例规模 / xfail 覆盖 三维度评分（20 分制）
*   **失败可回放**：Playwright Trace Viewer（失败自动保存 + 附 Allure）
*   **marker 分层**：smoke（10 用例 8 秒）/ regression / api / ui / 业务模块

***

## 🛠 技术栈

| 技术             | 版本    | 用途           |
| -------------- | ----- | ------------ |
| Python         | 3.11  | 开发语言         |
| pytest         | 7.4   | 测试框架         |
| requests       | 2.31  | HTTP 客户端     |
| Playwright     | 1.40  | UI 自动化 + POM |
| pydantic       | 2.13  | 响应契约校验       |
| tenacity       | 9.1   | HTTP 自动重试    |
| Allure         | 2.x   | 可视化报告        |
| jsonschema     | 4.26  | JSON 校验      |
| Faker          | 40.39 | 测试数据生成       |
| GitHub Actions | —     | CI/CD        |

***

## 📂 项目结构

```text
parabank-automation-framework/
├── .github/workflows/          # GitHub Actions CI
│   └── ci.yml
├── config/                     # 环境配置
│   └── env_config.py
├── scripts/                    # 工具脚本
│   ├── reset_parabank.py       # 数据重置
│   ├── quality_gate.py         # 质量门禁
│   ├── archive_report.py       # 报告归档
│   ├── scorer.py               # 测试评分
│   └── probes/                 # 诊断工具集
├── tests/
│   ├── api_test/               # API 层
│   │   ├── business/           # 业务封装（ParaBankBiz）
│   │   ├── schemas/            # pydantic 契约模型
│   │   └── scenarios/parabank/ # API 用例
│   │       ├── test_api_soap_parabank.py        # 转账/开户/贷款/账单
│   │       ├── test_api_deposit_withdraw.py     # 存/取款
│   │       ├── test_api_login_customer.py       # 登录/客户信息
│   │       ├── test_api_transaction_query.py    # 交易查询
│   │       ├── test_api_contract.py             # 契约校验
│   │       ├── test_api_balance_consistency.py  # 数据一致性
│   │       ├── test_api_boundary_param.py       # 参数化边界
│   │       └── test_api_exceptions.py           # 异常场景
│   ├── ui_test/                # UI 层
│   │   ├── pages/              # POM 页面对象（11 个）
│   │   └── scenarios/          # UI 用例 + 混合场景
│   └── finalize/               # 数据清理
│       └── clean_data.py
├── conftest.py                 # 全局 fixture
├── pytest.ini                  # pytest 配置
├── requirements.txt
├── run_test.ps1                # 一键运行（Windows）
├── run_test.sh                 # 一键运行（Linux/Mac）
├── Jenkinsfile                 # Jenkins 流水线
├── SECURITY_REPORT.md          # 安全报告（16 条漏洞）
└── README.md                   # 本文件
```
***
## 🚀 快速开始
### 1. 启动被测系统（ParaBank）
```powershell
# 需要 JDK 21 + Maven
cd /path/to/parabank-master
mvn clean package -DskipTests
mvn cargo:run
# 访问 http://localhost:8080/parabank
```
### 2. 安装依赖
```powershell
cd parabank-automation-framework
py -m pip install -r requirements.txt
py -m playwright install chromium
```
### 3. 重置测试数据
```powershell
py scripts/reset_parabank.py
```
### 4. 运行测试
```powershell
# 一键脚本（推荐）
.\\run_test.ps1 -Scope smoke      # smoke 集：10 用例，8 秒
.\\run_test.ps1                    # 全量：129 用例

# 或手动
py -m pytest tests -q                        # 全量
py -m pytest tests/api_test -v               # 仅 API
py -m pytest tests/ui_test -v --headed       # UI + 显示浏览器
py -m pytest tests -m smoke                  # 仅 smoke
```
### 5. 生成 Allure 报告
```powershell
allure generate allure-results --clean -o allure-report
allure open allure-report
```
### 6. 质量门禁
```powershell
py scripts/quality_gate.py
# 期望：[PASS] 质量门禁通过（通过率 100.00%）
```
***

## 🧪 用例设计思路

| 维度 | 数量 | 目的 | 发现漏洞 |
| :--- | :--- | :--- | :--- |
| 功能覆盖 | 51 | 主流程可跑通 | 3 |
| 参数化边界 | 14 | 边界值系统覆盖 | 8 |
| 契约校验 | 8 | 响应字段稳定性 | 0 |
| 数据一致性 | 15 | 金额变化精确性 | 0 |
| 混合场景 | 5 | 跨层状态同步 | 0 |
| 异常注入 | 17 | 健壮性 | 2 |
| **合计** | **129** | **—** | **16** |
***

## 关键设计
1、**参数化边界的"单位投入产出"最高**：每 3.5 个用例发现 1 个 bug

2、**3 个漏洞被 API + UI 双层独立复现**（可信度最高）

3、**43 个 xfail 是已知漏洞的自动守卫** —— 修复后会自动报警（XPASS）

4、**先探测后断言**：所有边界场景先跑探测脚本收集真实行为，再设计断言
***
## 🔍 已发现漏洞

16 条独立漏洞，按严重级别分类：

| 级别 | 数量 | 代表漏洞 |
| :--- | :---: | :--- |
| 🔴 高危 | 9 | 水平越权 / 未授权访问 / 转账负数 / 转账透支 / 存/取款负数 / 取款透支 |
| 🟠 中危 | 7 | 转账 0 元 / 自己转自己 / 无单笔限额 / 参数缺失返回 500 |

详见 [SECURITY_REPORT.md](SECURITY_REPORT.md)。
***

## ⚙️工程化能力

| 能力 | 实现 |
| :--- | :--- |
| CI/CD | GitHub Actions：构建 ParaBank → 跑测试 → 生成报告 → 部署 Pages |
| 质量门禁 | `scripts/quality_gate.py`：通过率 < 90% 阻断，xfail 不算失败 |
| 报告归档 | `scripts/archive_report.py`：按时间戳归档，保留最近 10 份 |
| 测试评分 | `scripts/scorer.py`：三维度 20 分制 |
| HTTP 重试 | tenacity：网络异常 + 5xx 重试 3 次，4xx 不重试 |
| 失败回放 | Playwright Trace Viewer（失败自动保存 + 附 Allure） |
| marker 分层 | smoke / regression / api / ui / 各业务模块 |
***

## 🔗 相关文档

- [SECURITY_REPORT.md](SECURITY_REPORT.md) — 16 条漏洞详情（含复现步骤 + 修复建议）
- `scripts/reset_parabank.py` — 数据重置工具（支持 `--check` / `--quiet`）
- `scripts/probes/` — 诊断工具集（边界探测 / 契约采样 / 页面结构）
- `Jenkinsfile` — Jenkins Windows agent 配置
- `pytest.ini` — pytest 配置（markers / junit / allure）
***

## 📈 测试评分

```powershell
py scripts/scorer.py
```
### 输出
```text
维度               得分 / 满分     说明
--------------------------------------------------
通过率            15.0 / 15     100.00%
用例规模            3.0 / 3      129 用例
xfail 覆盖        2.0 / 2      43 个（发现 bug）
--------------------------------------------------
总分             20.0 / 20

评级：⭐⭐⭐⭐⭐  优秀（可交付）
```
***
本项目由 pytest + Playwright 驱动，所有用例均可一键复现。

##  已知技术债

透明优于完美  以下是已知但暂未修复的问题：

| 编号 | 问题 | 严重级别 | 计划 |
|---|---|---|---|
| TD-01 | `test_api_soap_parabank.py` 存在重复的账户获取代码（约 10 处）| 轻微 | 下一轮提取为 fixture |
| TD-02 | 参数传递风格不统一（位置参数 vs 关键字参数）| 轻微 | 统一为关键字参数 |
| TD-03 | 异常测试混用 `requests` 和 `ParaBankBiz` | 轻微 | 协议层测试走独立客户端 |
| TD-04 | `test_api_contract.py` XML namespace 处理不一致 | 轻微 | 统一通过 `_tag()` 辅助函数解析 |
| TD-05 | 部分用例缺 docstring | 极轻微 | 与 `@allure.title` 对齐补充 |

**已修复（来自代码审查）**：

-  **C-01** 硬编码配置  集中到 `config/test_constants.py`
-  **M-05** HTTP 请求无 timeout  `BaseApi` + `ParaBankBiz` 默认 15 秒
-  **Bug** `.env` 的 `API_BASE_URL` 值错误（多了 `/api`） 已修正

---

*本项目所有用例均可一键复现。*
