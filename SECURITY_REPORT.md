# ParaBank 安全问题报告

**测试日期**：2026-09-28（v1.0）/ 2026-10-05（v2.0）
**被测版本**：parabank-master
**测试框架**：parabank-automation-framework（pytest + requests + Playwright）
**报告状态**：v2.0 — 已扩展漏洞覆盖

---

> **📌 当前状态（v2.0）**
>
> - 已确认漏洞：**19 个**（高危 9 / 中危 7 / 低危 3）
> - 测试用例：129（API 103 + UI 26）
> - 守卫数量：**43 个 xfail**（每个漏洞至少 1 条用例锁定）
> - 阻塞缺陷：**无**（v1.0 的 BUG_TRANSFER_001 已不复现）
> - 全量基线：`86 passed, 43 xfailed`
>
> 详细漏洞清单见 [KNOWN_BUGS.md](KNOWN_BUGS.md)。

---

## 一、摘要

### v1.0（2026-09-28 首次基线）

| 项 | 数值 |
| ------ |------ |
| 测试用例总数 | 23 |
| 通过（PASSED） | 8 |
| 已确认漏洞（XFAIL） | 8 |
| 阻塞待验证（SKIPPED） | 7 |
| 未知失败（FAILED） | 0 |
| 意外通过（XPASS） | 0 |

**核心结论：**

- 发现 **8 个已确认安全/业务漏洞**，其中高危 5 个、中危 2 个、低危 1 个
- `/transfer` 接口存在 **1 个阻塞性缺陷**（BUG_TRANSFER_001），导致所有转账相关用例无法验证
- 所有漏洞均通过自动化用例持续守卫，修复后 XFAIL 会自动变为 XPASS 触发回归

### v2.0（2026-10-05 覆盖扩展）

| 项 | 数值 | 相比 v1.0 |
| ------ |------ |------ |
| 测试用例总数 | 129 | +106 |
| 通过（PASSED） | 86 | +78 |
| 已确认漏洞（XFAIL） | 43 | +35 |
| 阻塞待验证（SKIPPED） | 0 | -7 |
| 独立漏洞数 | **19** | +11 |
| 阻塞缺陷 | 0 | -1 |

**v2.0 核心结论：**

- 漏洞覆盖从 8 个扩展到 **19 个**，主要补充存款/取款/贷款/协议层异常
- v1.0 的 `BUG_TRANSFER_001`（转账接口整体不可用）**已不复现**，7 条阻塞用例全部转为正常执行或 xfail
- 新增 `ParaBankRaw` 裸客户端，异常测试绕过 tenacity 重试，执行时间缩短 ~80%
- 所有漏洞由 43 个 xfail 用例守卫，修复后 XPASS 触发 CI 报警

---

## 二、测试环境

| 项 | 值 |
| ------ |------ |
| 被测系统 | ParaBank REST API |
| 部署方式 | 本地 Maven（`mvn cargo:run`） |
| 服务地址 | http://localhost:8080/parabank |
| REST 前缀 | http://localhost:8080/parabank/services/bank |
| 测试账号 | `john` / `demo`（CUSTOMER_ID = 12212） |
| 数据库 | 内嵌 HSQLDB（重启即重置） |

**复现所有漏洞的最小前置步骤：**

```powershell
# 1. 启动 ParaBank
cd E:\parabank-master
mvn cargo:run

# 2. 验证服务
curl.exe -u john:demo "http://localhost:8080/parabank/services/bank/customers/12212/accounts" -i

# 3. 复现单个用例
cd E:\credit-approval-system
py -m pytest tests/api_test/scenarios/parabank/test_api_soap_parabank.py::TestParaBankAPI::test_transfer_amount_negative -v
```

---

## 三、漏洞清单（v2.0 完整版）

> 按严重级别分组。每条漏洞附守卫用例名。
> 完整复现步骤和修复建议见 [KNOWN_BUGS.md](KNOWN_BUGS.md)。

### 🔴 高危漏洞（9 个）

#### BUG_004 水平越权（多接口）

| 项 | 内容 |
| ------ |------ |
| 严重级别 | 高 |
| 影响接口 | `GET /customers/{id}`、`GET /customers/{id}/accounts`、`POST /transfer`、`GET /accounts/{id}/transactions` |
| 守卫用例 | `test_get_customer_horizontal_privilege`、`test_get_other_customer_account_horizontal`、`test_transfer_other_user_account`、`test_transfer_horizontal_privilege`、`test_get_transactions_horizontal_privilege` |
| 修复建议 | 服务端从 token/session 提取当前用户 ID，忽略或校验 URL 中的 `customerId` |

#### BUG_005 未授权访问（多接口）

| 项 | 内容 |
| ------ |------ |
| 严重级别 | 高 |
| 影响接口 | `GET /customers/{id}`、`GET /customers/{id}/accounts`、`GET /accounts/{id}/transactions` |
| 守卫用例 | `test_get_customer_no_auth`、`test_get_account_no_auth`、`test_get_transactions_no_auth` |
| 修复建议 | 对所有 `/services/bank/**` 加统一鉴权拦截器 |

#### BUG_006 转账无幂等控制

| 项 | 内容 |
| ------ |------ |
| 严重级别 | 高 |
| 接口 | `POST /services/bank/transfer` |
| 守卫用例 | `test_transfer_idempotent`、`test_transfer_duplicate_submit` |
| 修复建议 | 引入客户端幂等号（Idempotency-Key），服务端做去重 |

#### BUG_102 转账允许负数金额

| 项 | 内容 |
| ------ |------ |
| 严重级别 | 高 |
| 接口 | `POST /services/bank/transfer` |
| 守卫用例 | `test_transfer_amount_negative` |
| 修复建议 | `amount > 0` 显式校验 |

#### BUG_103 转账允许透支

| 项 | 内容 |
| ------ |------ |
| 严重级别 | 高 |
| 接口 | `POST /services/bank/transfer` |
| 守卫用例 | `test_transfer_over_balance` |
| 修复建议 | 转账前校验 `balance >= amount` |

#### BUG_202 存款允许负数金额

| 项 | 内容 |
| ------ |------ |
| 严重级别 | 高 |
| 接口 | `POST /services/bank/deposit` |
| 守卫用例 | `test_deposit_amount_negative`、`test_deposit_negative_no_decrease` |
| 修复建议 | `amount > 0` 显式校验 |

#### BUG_203 取款允许透支

| 项 | 内容 |
| ------ |------ |
| 严重级别 | 高 |
| 接口 | `POST /services/bank/withdraw` |
| 守卫用例 | `test_withdraw_over_balance`、`test_withdraw_over_balance_no_overdraft` |
| 修复建议 | 取款前校验余额 |

#### BUG_204 取款允许负数金额

| 项 | 内容 |
| ------ |------ |
| 严重级别 | 高 |
| 接口 | `POST /services/bank/withdraw` |
| 守卫用例 | `test_withdraw_amount_negative`、`test_withdraw_negative_no_increase` |
| 修复建议 | `amount > 0` 显式校验 |

#### BUG_BILL_001 账单支付未校验余额

| 项 | 内容 |
| ------ |------ |
| 严重级别 | 高 |
| 接口 | `POST /services/bank/billpay` |
| 守卫用例 | `test_bill_pay_over_balance` |
| 修复建议 | 支付前校验 `account.balance >= amount` |

### 🟠 中危漏洞（7 个）

| ID | 描述 | 守卫用例 | 修复建议 |
|---|---|---|---|
| BUG_001 / BUG_101 | 转账允许 0 元 | `test_transfer_zero_amount`、`test_transfer_amount_zero`、`test_transfer_zero_should_reject` | `amount > 0` |
| BUG_104 | 转账允许自己转自己 | `test_transfer_same_account` | 校验 from ≠ to |
| BUG_105 | 转账无单笔限额 | `test_transfer_over_single_limit` | 加单笔限额（如 50000） |
| BUG_201 | 存款允许 0 元 | `test_deposit_amount_zero`、`test_deposit_zero_should_reject` | `amount > 0` |
| BUG_205 | 取款允许 0 元 | `test_withdraw_amount_zero`、`test_withdraw_zero_should_reject` | `amount > 0` |
| BUG_301 | 转账缺 `amount` 参数返回 500 | `test_transfer_missing_amount_returns_4xx` | 返回 400 + 错误信息 |
| BUG_302 | 转账 `amount` 空字符串返回 500 | `test_transfer_empty_amount_returns_4xx` | 同上 |

### 🟡 低危漏洞（3 个）

| ID | 描述 | 守卫用例 |
|---|---|---|
| BUG_002 | UI 层允许负数金额转账 | `test_transfer_negative_amount` |
| BUG_003 | UI 层允许余额不足转账 | `test_transfer_insufficient_balance` |
| BUG_XSS_001 | 响应缺少 `X-Content-Type-Options` 等安全头 | （纯记录，无自动化守卫） |

### 已不复现的历史漏洞

| ID | v1.0 描述 | v2.0 状态 |
|---|---|---|
| BUG_TRANSFER_001 | `/transfer` 接口整体不可用（返回 400） | **已不复现** — 转账接口正常工作，v1.0 的 7 条阻塞用例全部恢复 |

---

## 四、v1.0 阻塞用例（已恢复）

v1.0 中以下 7 条用例因 `BUG_TRANSFER_001` 被 `pytest.skip()`：

| # | 用例 | v2.0 状态 |
| ------ |------ |------ |
| 1 | `test_transfer_amount_zero` | ✅ 已执行（xfail） |
| 2 | `test_transfer_amount_negative` | ✅ 已执行（xfail） |
| 3 | `test_transfer_over_balance` | ✅ 已执行（xfail） |
| 4 | `test_transfer_over_single_limit` | ✅ 已执行（xfail） |
| 5 | `test_transfer_duplicate_submit` | ✅ 已执行（xfail） |
| 6 | `test_transfer_response_schema` | ✅ 已执行（passed） |
| 7 | `test_transfer_sql_inject` | ✅ 已执行（passed） |

**v2.0 中无 SKIPPED 用例。**
**注**：v1.0 用于探测 `/transfer` 状态的 `_transfer_is_broken(biz)` 辅助函数已在 v2.0 中移除，因为该缺陷不再复现。
---

## 五、正常功能（v2.0 摘要）

129 个用例中，**86 个通过**，覆盖：

- 账户查询（本人列表 / 单账户详情 / 交易流水）
- 转账正常流程 + 响应结构校验 + SQL 注入防御
- 开户（SAVINGS / CHECKING）
- 账单支付正常金额
- 贷款申请（正常 / 超授信被拒）
- 存款 / 取款正常流程
- 契约校验（8 个 pydantic 模型）
- 数据一致性（精确到分）
- 参数化边界（0 / 负数 / 超额 / 精度）
- UI 全流程（登录 / 登出 / 转账 / 开户 / 贷款 / 账户详情）
- 混合场景（API 造数据 + UI 验证 / UI 操作 + API 校验）

---

## 六、测试基线与回归

### v1.0 基线（2026-09-28）

```text
8 passed, 7 skipped, 8 xfailed in 1.92s
```

### v2.0 基线（2026-10-05）

```text
86 passed, 43 xfailed in 78.95s
```

**回归命令：**

```powershell
cd E:\credit-approval-system

# 全量
py -m pytest tests -q

# 仅 API
py -m pytest tests/api_test -v

# 仅安全相关
py -m pytest tests/api_test -v -k "no_auth or horizontal or privilege"
```

**修复后预期变化：**

- 对应 `@pytest.mark.xfail(strict=True)` 会变为 `XPASS(strict)` → **CI 失败** → 强制移除 xfail 标记并更新文档

**严格模式（pytest.ini）：**

```ini
[pytest]
xfail_strict = true
```

---

## 七、建议修复优先级

| 优先级 | 漏洞 | 理由 |
| ------ |------ |------ |
| **P0** | BUG_004 水平越权（多接口） | 可读取任意客户资金信息 |
| **P0** | BUG_005 未授权访问（多接口） | 无需登录即可读数据 |
| **P0** | BUG_006 转账无幂等 | 重复提交可能多次扣款 |
| **P0** | BUG_102 转账负数 | 资金反向流动 |
| **P0** | BUG_103 转账透支 | 余额变负 |
| **P0** | BUG_203 取款透支 | 余额变负 |
| **P1** | BUG_202 存款负数 | 变相绕过取款限额 |
| **P1** | BUG_204 取款负数 | 变相存款 |
| **P1** | BUG_BILL_001 账单不校验余额 | 业务资金可透支 |
| **P1** | BUG_104/105 转账自身/无限额 | 业务规则缺失 |
| **P2** | BUG_101/201/205 零金额 | 参数校验缺失 |
| **P2** | BUG_301/302 缺参返回 500 | 错误处理不友好 |
| **P3** | BUG_XSS_001 缺安全头 | 纵深防御 |

---

## 八、附录

### 8.1 漏洞统计图（v2.0）

```text
高危 ████████████████████  9
中危 ████████████████      7
低危 ██████                3
```

### 8.2 相关文件

- 测试用例：`tests/api_test/scenarios/parabank/`
- 业务封装：`tests/api_test/business/parabank_biz.py`（`ParaBankBiz` + `ParaBankRaw`）
- 漏洞文档：`KNOWN_BUGS.md`
- CI 配置：`.github/workflows/ci.yml`

### 8.3 变更记录

| 日期 | 版本 | 变更 |
| ------ |------ |------ |
| 2026-09-28 | v1.0 | 首次基线，识别 8 漏洞 + 1 阻塞 |
| 2026-10-05 | v2.0 | 漏洞覆盖扩展至 19 个；`BUG_TRANSFER_001` 已不复现；引入 `ParaBankRaw`；43 xfail 守卫 |

---

本报告由 parabank-automation-framework 自动化测试框架生成，所有结论均可通过上述用例一键复现。