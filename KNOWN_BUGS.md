# KNOWN_BUGS.md

本项目通过 `@pytest.mark.xfail(strict=True)` 锁定 **19 个已知缺陷**（覆盖 43 个测试用例）。

修复任一缺陷后，对应 xfail 会变成 `XPASS(strict)`，CI 立即失败，强制移除标记。这是本项目"缺陷守卫"机制的核心。

---

## 一、总览

| 严重度 | 数量 | 说明 |
|---|---|---|
| 🔴 高 | 9 | 安全漏洞 / 资金风险 |
| 🟠 中 | 7 | 参数校验 / 业务逻辑缺失 |
| 🟡 低 | 3 | 错误处理不友好 |
| **合计** | **19** | |

**影响范围**：所有缺陷均集中在 ParaBank 的 `/transfer`、`/deposit`、`/withdraw`、`/billpay`、`/customers` 五个接口。

---

## 二、🔴 高危缺陷（9 个）

### BUG_004：水平越权（多接口）

**影响**：任何登录用户可通过篡改客户 ID 读取或操作他人数据。

| 攻击点 | 说明 | 守卫用例 |
|---|---|---|
| `/customers/{id}` | 读取他人客户信息 | `test_get_customer_horizontal_privilege` |
| `/customers/{id}/accounts` | 读取他人账户列表 | `test_get_other_customer_account_horizontal` |
| `/transfer` | 跨客户转账 | `test_transfer_other_user_account` |
| `/transfer` | 使用 A token 操作 B 账户资金 | `test_transfer_horizontal_privilege` |
| `/accounts/{id}/transactions` | 查询他人交易 | `test_get_transactions_horizontal_privilege` |

**修复建议**：所有接口必须从 token 中解析当前用户 ID，不接受请求参数中的客户 ID。

---

### BUG_005：未授权访问（多接口）

**影响**：无需任何认证即可读取敏感数据。

| 攻击点 | 说明 | 守卫用例 |
|---|---|---|
| `/customers/{id}` | 无 token 可读客户信息 | `test_get_customer_no_auth` |
| `/customers/{id}/accounts` | 无 token 可读账户列表 | `test_get_account_no_auth` |
| `/accounts/{id}/transactions` | 无 token 可查交易流水 | `test_get_transactions_no_auth` |

**修复建议**：所有涉及用户数据的接口加 token 校验中间件，无 token 直接返回 401。

---

### BUG_006：`/transfer` 无幂等（重复扣款）

**影响**：网络重试或用户快速双击，同一笔转账会被执行多次，造成资金损失。

**守卫用例**：`test_transfer_duplicate_submit`、`test_transfer_idempotent`

**修复建议**：引入 `requestId` 幂等键，服务端对同一 key 的重复请求只处理一次。

---

### BUG_102：`/transfer` 允许负数金额（反向扣款）

**影响**：传入 `-100` 时，金额反向流动——转出方余额增加，转入方减少。造成资金凭空转移。

**守卫用例**：`test_transfer_amount_negative`

**修复建议**：转账金额必须 `> 0`，服务端显式校验。

---

### BUG_103：`/transfer` 允许透支

**影响**：余额不足时仍能转账成功，转出方余额变成负数。

**守卫用例**：`test_transfer_over_balance`

**修复建议**：转账前检查 `balance >= amount`，否则返回 4xx。

---

### BUG_202：`/deposit` 允许负数金额

**影响**：传入负数存款等于变相"取款"，可绕过取款限额。

**守卫用例**：`test_deposit_amount_negative`、`test_deposit_negative_no_decrease`

**修复建议**：存款金额必须 `> 0`。

---

### BUG_203：`/withdraw` 允许透支

**影响**：取款超过余额时仍返回 200，余额变负。

**守卫用例**：`test_withdraw_over_balance`、`test_withdraw_over_balance_no_overdraft`

**修复建议**：取款前检查余额。

---

### BUG_204：`/withdraw` 允许负数金额

**影响**：传入 `-50` 等于变相存款，绕过业务限制。

**守卫用例**：`test_withdraw_amount_negative`、`test_withdraw_negative_no_increase`

**修复建议**：取款金额必须 `> 0`。

---

### BUG_BILL_001：`/billpay` 未校验余额

**影响**：账单支付金额超过余额时仍返回 200，余额变负。

**守卫用例**：`test_bill_pay_over_balance`

**修复建议**：支付前检查余额。

---

## 三、🟠 中危缺陷（7 个）

| ID | 描述 | 守卫用例 | 修复建议 |
|---|---|---|---|
| BUG_001 / BUG_101 | `/transfer` 允许 0 元转账 | `test_transfer_zero_amount`、`test_transfer_amount_zero`、`test_transfer_zero_should_reject` | 金额必须 `> 0` |
| BUG_104 | `/transfer` 允许自己转自己 | `test_transfer_same_account` | 校验 from ≠ to |
| BUG_105 | `/transfer` 无单笔限额 | `test_transfer_over_single_limit` | 加单笔限额（如 50000） |
| BUG_201 | `/deposit` 允许 0 元 | `test_deposit_amount_zero`、`test_deposit_zero_should_reject` | 金额必须 `> 0` |
| BUG_205 | `/withdraw` 允许 0 元 | `test_withdraw_amount_zero`、`test_withdraw_zero_should_reject` | 金额必须 `> 0` |
| BUG_301 | `/transfer` 缺 amount 参数返回 500 | `test_transfer_missing_amount_returns_4xx` | 返回 400 并带错误信息 |
| BUG_302 | `/transfer` amount 空字符串返回 500 | `test_transfer_empty_amount_returns_4xx` | 同上 |

---

## 四、🟡 低危缺陷（3 个）

| ID | 描述 | 守卫用例 |
|---|---|---|
| BUG_002 | UI 允许负数金额转账 | `test_transfer_negative_amount` |
| BUG_003 | UI 允许余额不足转账 | `test_transfer_insufficient_balance` |
| BUG_202（UI 侧） | UI 未拦截负数存款 | （仅 API 侧守卫） |

> 说明：UI 层的这些缺陷本质是 API 缺陷的映射。修复 API 后 UI 会自然拦截。

---

## 五、缺陷分布统计

| 接口 | 高危 | 中危 | 低危 | 合计 |
|---|---|---|---|---|
| `/transfer` | 4 | 4 | 2 | 10 |
| `/deposit` | 1 | 1 | 1 | 3 |
| `/withdraw` | 2 | 1 | 0 | 3 |
| `/billpay` | 1 | 0 | 0 | 1 |
| `/customers` | 1 | 0 | 0 | 1 |
| 全局（幂等） | 1 | 0 | 0 | 1 |

**结论**：`/transfer` 是缺陷密度最高的接口（10/19），且高危占比 40%。

---

## 六、复现方式

所有缺陷可通过一条命令复现：

```powershell
cd E:\credit-approval-system
py -m pytest tests -q -k "xfail" 2>&1
```

或单独复现某条：

```powershell
py -m pytest tests/api_test/scenarios/parabank/test_api_soap_parabank.py::TestParaBankAPI::test_transfer_amount_negative -v
```

---

## 七、修复后流程

1. 修复某缺陷
2. 移除对应测试用例上的 `@pytest.mark.xfail(strict=True)`
3. 更新本文档，将缺陷移到"已修复"章节
4. 重跑全量测试，确保通过

---

## 八、与 SECURITY_REPORT.md 的关系

- 本文档侧重**测试守卫视角**（哪些用例锁定哪些 bug）
- `SECURITY_REPORT.md` 侧重**安全审计视角**（漏洞复现步骤 + 修复建议）
- 两者是同一批缺陷的不同切面，交叉引用