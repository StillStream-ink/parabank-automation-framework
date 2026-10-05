# ParaBank Automation Testing Framework

**English** | [简体中文](./README.zh-CN.md)

[![CI](https://github.com/StillStream-ink/parabank-automation-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/StillStream-ink/parabank-automation-framework/actions)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Pytest](https://img.shields.io/badge/Pytest-7.4-green)](https://docs.pytest.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.40-brightgreen)](https://playwright.dev/)
[![Allure](https://img.shields.io/badge/Allure-2.x-orange)](https://docs.qameta.io/allure/)
[![Ruff](https://img.shields.io/badge/Ruff-0.16-purple)](https://docs.astral.sh/ruff/)


> 📊 **Live Test Report**：<https://stillstream-ink.github.io/parabank-automation-framework/>
>
> A full-stack automation testing framework for ParaBank built with **pytest + requests + Playwright + pydantic**.
> Covers **REST API + Web UI + Hybrid Scenarios**, including Contract Validation / Data **Consistency / Boundary Parametrization / Exception Injection**.

***

## 📊 Project Overview

| Metric | Value |
| :--- | :--- |
| 📝 Total Test Cases | 129 (API 103 + UI 26) |
| ✅ Pass Rate (Effective) | 100% |
| 🛡 Known Bug Guards | 43 |
| 🐛 Independent Bugs Found | 19 |
| ⏱ Full Run Duration | ~85s |
| 🎯 Smoke Suite Duration | ~10s |
| ⭐ Test Score | 20.0 / 20 |

***

## ✨ Highlights

### Testing Capabilities

- **Dual-Layer Coverage**: API (pytest + requests) + UI (Playwright + POM)
- **Hybrid Scenarios**: API setup → UI verification / UI action → API verification / 3-stage E2E
- **Contract Validation**: pydantic models verify response field names/types/required
- **Data Consistency**: Precise-to-cent balance assertions for transfer/deposit/withdraw
- **Boundary Parametrization**: 0 / negative / over-balance / precision edge cases
- **Exception Scenarios**: Invalid params / missing params / special chars / oversized numbers / protocol-level
- **Unified XML Handling**: All SOAP responses stripped of namespace via `_parse()` helper
- **Allure Step Coverage**: Every UI scenario decomposed into readable `allure.step()` blocks

### Engineering

- **CI/CD**: GitHub Actions builds ParaBank, runs API & UI tests separately, deploys Allure report
- **Code Quality**: ruff (lint + format) enforced via pre-commit hooks
- **Quality Gate**: Blocks CI when pass rate < 90%; xfail excluded, deduped by historyId
- **HTTP Retry**: tenacity auto-retry on network errors + 5xx (3 attempts); 4xx not retried
- **Raw Client**: `ParaBankRaw` for exception tests — no retry, no Allure overhead
- **Report Archive**: Auto-archive to `reports/YYYYMMDD_HHMMSS/`; content-hash dedup
- **Test Scoring**: 3-dimension scoring (pass rate / test size / xfail coverage), 20 points
- **Trace Replay**: Playwright Trace Viewer (auto-save on failure + attach to Allure)
- **Marker Layering**: smoke (10 cases, 8s) / regression / api / ui / business modules

***

## 🛠 Tech Stack

| Tech | Version | Purpose |
| :--- | :--- | :--- |
| Python | 3.11 | Language |
| pytest | 7.4 | Test framework |
| requests | 2.31 | HTTP client |
| Playwright | 1.40 | UI automation + POM |
| pydantic | 2.13 | Response contract validation |
| tenacity | 9.1 | HTTP auto-retry |
| Allure | 2.x | Visual reporting |
| ruff | 0.16 | Lint + format |
| pre-commit | 4.x | Git hooks |
| GitHub Actions | — | CI/CD |

***

## 📂 Project Structure

```text
parabank-automation-framework/
├── .github/workflows/          # GitHub Actions CI (split API / UI jobs)
├── .pre-commit-config.yaml     # pre-commit hooks (ruff)
├── ruff.toml                   # ruff lint & format config
├── .gitattributes              # line ending policy
├── config/                     # Environment config
├── scripts/                    # Utility scripts
│   ├── reset_parabank.py       # Data reset
│   ├── quality_gate.py         # Quality gate
│   ├── archive_report.py       # Report archiver (hash-deduped)
│   ├── scorer.py               # Test scorer
│   └── probes/                 # Diagnostic tools
├── tests/
│   ├── api_test/               # API layer (business / schemas / scenarios)
│   │   └── business/
│   │       └── parabank_biz.py # ParaBankBiz + ParaBankRaw
│   ├── ui_test/                # UI layer (pages / scenarios, all with allure.step)
│   └── finalize/               # Data cleanup
├── conftest.py                 # Global fixtures
├── pytest.ini                  # pytest config
├── requirements.txt
├── run_test.ps1                # One-click runner (Windows)
├── run_test.sh                 # One-click runner (Linux/Mac)
├── Jenkinsfile                 # Jenkins pipeline
├── KNOWN_BUGS.md               # 19 known defects (xfail guards)
└── SECURITY_REPORT.md          # Security audit report
```

***

## 🚀 Quick Start

### 1. Start ParaBank (System Under Test)

```powershell
cd /path/to/parabank-master
mvn clean package -DskipTests
mvn cargo:run
# Visit http://localhost:8080/parabank
```

### 2. Install Dependencies

```powershell
cd parabank-automation-framework
py -m pip install -r requirements.txt
py -m playwright install chromium
py -m pre_commit install        # Install git hooks
```

### 3. Reset Test Data

```powershell
py scripts/reset_parabank.py
```

### 4. Run Tests

```powershell
.\\run_test.ps1 -Scope smoke      # Smoke suite: 10 cases, 8s
.\\run_test.ps1                    # Full: 129 cases

py -m pytest tests -q                        # Full
py -m pytest tests/api_test -v               # API only
py -m pytest tests/ui_test -v --headed       # UI + headed browser
```

### 5. Generate Allure Report

```powershell
allure generate allure-results --clean -o allure-report
allure open allure-report
```

### 6. Quality Gate

```powershell
py scripts/quality_gate.py
# Expected: [PASS] Quality gate passed (pass rate 100.00%)
```

***

## 🧪 Test Design

| Dimension | Count | Purpose | Bugs Found |
| :--- | :--- | :--- | :--- |
| Functional | 51 | Happy paths | 3 |
| Boundary Param | 14 | Systematic boundary coverage | 8 |
| Contract | 8 | Response field stability | 0 |
| Data Consistency | 15 | Balance change precision | 0 |
| Hybrid Scenarios | 5 | Cross-layer state sync | 0 |
| Exception Injection | 17 | Robustness | 2 |
| **Total** | **129** | | **19** |

**Key Design Points:**

1. **Boundary param has the highest ROI:** 1 bug per 3.5 cases
2. **Bugs reproduced at both API + UI layers independently**
3. **43 xfails are automated guards for 19 known bugs** (auto-alert when fixed)
4. **Probe-first, then assert:** probe scripts collect real behavior before designing assertions
5. **Raw client for exception tests:** `ParaBankRaw` bypasses tenacity retry, reducing exception-suite time

***

## 🔍 Discovered Bugs

| Severity | Count | Examples |
| :--- | :--- | :--- |
| 🔴 High | 9 | Horizontal privilege escalation / Unauthorized access / Negative transfer / Overdraft |
| 🟠 Medium | 7 | Zero transfer / Self-transfer / No single-limit / Missing param returns 500 |
| 🟡 Low | 3 | UI-side validation gaps |

See [KNOWN_BUGS.md](KNOWN_BUGS.md) for the full list with reproduction steps.
See [SECURITY_REPORT.md](SECURITY_REPORT.md) for the security audit view.

***

## ⚙️ Engineering Capabilities

| Capability | Implementation |
| :--- | :--- |
| CI/CD | GitHub Actions: Build ParaBank → Run API tests → Run UI tests (headless) → Generate report → Deploy Pages |
| Code Quality | `ruff.toml` + `.pre-commit-config.yaml`; enforced locally and in CI |
| Quality Gate | `scripts/quality_gate.py`: Blocks CI if pass rate < 90% (xfail is not considered a failure) |
| Report Archiving | `scripts/archive_report.py`: Timestamped archiving + SHA256 content dedup, retains the last 10 copies |
| Test Scoring | `scripts/scorer.py`: 3-dimension, 20-point scale |
| HTTP Retry | tenacity: Retries 3 times on network errors + 5xx, does not retry on 4xx |
| Raw Client | `ParaBankRaw`: no retry, no Allure attach — for exception tests |
| Failure Replay | Playwright Trace Viewer (auto-save on failure + attached Allure report) |
| Marker Layering | smoke / regression / api / ui / business modules |

***

## 🔗 Related Documentation

- [KNOWN_BUGS.md](KNOWN_BUGS.md) — 19 known defects with reproduction steps + xfail guards
- [SECURITY_REPORT.md](SECURITY_REPORT.md) — Security audit report
- `scripts/reset_parabank.py` — Data reset tool (supports `--check` / `--quiet`)
- `scripts/probes/` — Diagnostic toolkit (boundary probing / contract sampling / page structure)
- `Jenkinsfile` — Jenkins Windows agent configuration
- `pytest.ini` — pytest configuration (markers / junit / allure)
- [OPTIMIZATION.md](OPTIMIZATION.md)  — Detailed summary of optimizations for this round
***

## 📈 Test Score

```powershell
py scripts/scorer.py
```

### Output

```text
Dimension          Score / Max     Description
--------------------------------------------------
Pass Rate          15.0 / 15       100.00%
Test Case Scale    3.0 / 3         129 test cases
Xfail Coverage     2.0 / 2         43 cases (bugs found)
--------------------------------------------------
Total Score        20.0 / 20

Rating: ⭐⭐⭐⭐⭐  Excellent (Ready for Delivery)
```

***

Driven by pytest + Playwright, all test cases can be reproduced with a single command.

## ✅ Technical Debt Status

The following technical debt items (previously listed as known issues) have been **addressed** in this iteration:

| ID | Issue | Status | Resolution |
|---|---|---|---|
| TD-01 | Duplicate account-fetching code in `test_api_soap_parabank.py` | ✅ Done | Extracted `biz` / `accounts` / `two_accounts` / `first_account` fixtures |
| TD-02 | Inconsistent parameter passing style | ✅ Partial | Type hints + docstrings added; keyword args for 3+ param calls |
| TD-03 | Exception tests mix `requests` and `ParaBankBiz` | ✅ Done | Introduced `ParaBankRaw` (no retry, no Allure) for exception tests |
| TD-04 | XML namespace handling inconsistent in `test_api_contract.py` | ✅ Done | Unified via `_parse()` / `_strip_ns()` helpers |
| TD-05 | Some test methods lack docstrings | ⏭️ Skipped | `@allure.title` already serves as scenario documentation; adding docstrings would be redundant |

**Also fixed in this iteration**:

- **Encoding issues** in `config/env_config.py` (GBK → UTF-8) and structural break fixed
- **Dead code removal**: `tests/fixtures/db_fixture.py` (PostgreSQL leftover), `tests/config/` (duplicate)
- **Hardcoded account IDs** replaced with `ACC_A` / `ACC_B` / `CUSTOMER_ID_JOHN` constants
- **Fake-green tests fixed**: `test_transaction_single_contract` (missing assertion), `test_transfer_horizontal_privilege` (undefined `biz`)
- **BOM / CRLF** inconsistencies resolved; `.gitattributes` added

---

*All test cases can be reproduced with a single command.*