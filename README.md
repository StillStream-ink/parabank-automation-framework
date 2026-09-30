# ParaBank Automation Testing Framework

**English** | [简体中文](./README.zh-CN.md)

[![CI](https://github.com/StillStream-ink/parabank-automation-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/StillStream-ink/parabank-automation-framework/actions)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Pytest](https://img.shields.io/badge/Pytest-7.4-green)](https://docs.pytest.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.40-brightgreen)](https://playwright.dev/)
[![Allure](https://img.shields.io/badge/Allure-2.x-orange)](https://docs.qameta.io/allure/)


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
| 🐛 Independent Bugs Found | 16 |
| ⏱ Full Run Duration | ~120s |
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

### Engineering

- **CI/CD**: GitHub Actions builds ParaBank, runs tests, deploys Allure report
- **Quality Gate**: Blocks CI when pass rate < 90%; xfail excluded, deduped by historyId
- **HTTP Retry**: tenacity auto-retry on network errors + 5xx (3 attempts); 4xx not retried
- **Report Archive**: Auto-archive to `reports/YYYYMMDD_HHMMSS/`
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
| GitHub Actions | — | CI/CD |

***

## 📂 Project Structure

```text
parabank-automation-framework/
├── .github/workflows/          # GitHub Actions CI
├── config/                     # Environment config
├── scripts/                    # Utility scripts
│   ├── reset_parabank.py       # Data reset
│   ├── quality_gate.py         # Quality gate
│   ├── archive_report.py       # Report archiver
│   ├── scorer.py               # Test scorer
│   └── probes/                 # Diagnostic tools
├── tests/
│   ├── api_test/               # API layer (business / schemas / scenarios)
│   ├── ui_test/                # UI layer (pages / scenarios)
│   └── finalize/               # Data cleanup
├── conftest.py                 # Global fixtures
├── pytest.ini                  # pytest config
├── requirements.txt
├── run_test.ps1                # One-click runner (Windows)
├── run_test.sh                 # One-click runner (Linux/Mac)
├── Jenkinsfile                 # Jenkins pipeline
└── SECURITY_REPORT.md          # Security report (16 findings)
```
***
## 🚀 Quick Start
### 1.Start ParaBank (System Under Test)
```powershell
cd /path/to/parabank-master
mvn clean package -DskipTests
mvn cargo:run
# Visit http://localhost:8080/parabank
```
### 2.Install Dependencies
```powershell
cd parabank-automation-framework
py -m pip install -r requirements.txt
py -m playwright install chromium
```
### 3.Reset Test Data
```powershell
py scripts/reset_parabank.py
```
### 4.Run Tests
```powershell
.\\run_test.ps1 -Scope smoke      # Smoke suite: 10 cases, 8s
.\\run_test.ps1                    # Full: 129 cases

py -m pytest tests -q                        # Full
py -m pytest tests/api_test -v               # API only
py -m pytest tests/ui_test -v --headed       # UI + headed browser
```
### 5.Generate Allure Report
```powershell
allure generate allure-results --clean -o allure-report
allure open allure-report
```
### 6.Quality Gate
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
| **Total** | **129** | | **16** |

**Key Design Points:**

1. **Boundary param has the highest ROI:** 1 bug per 3.5 cases
2. **3 bugs reproduced at both API + UI layers independently**
3. **43 xfails are automated guards for known bugs** (auto-alert when fixed)
4. **Probe-first, then assert:** probe scripts collect real behavior before designing assertions

***
## 🔍 Discovered Bugs

| Severity | Count | Examples |
| :--- | :--- | :--- |
| 🔴 High | 9 | Horizontal privilege escalation / Unauthorized access / Negative transfer / Overdraft |
| 🟠 Medium | 7 | Zero transfer / Self-transfer / No single-limit / Missing param returns 500 |

See [SECURITY_REPORT.md](SECURITY_REPORT.md) for details.
***

## ⚙️ Engineering Capabilities

| Capability | Implementation |
| :--- | :--- |
| CI/CD | GitHub Actions: Build ParaBank → Run tests → Generate report → Deploy Pages |
| Quality Gate | `scripts/quality_gate.py`: Blocks CI if pass rate < 90% (xfail is not considered a failure) |
| Report Archiving | `scripts/archive_report.py`: Timestamped archiving, retains the last 10 copies |
| Test Scoring | `scripts/scorer.py`: 3-dimension, 20-point scale |
| HTTP Retry | tenacity: Retries 3 times on network errors + 5xx, does not retry on 4xx |
| Failure Replay | Playwright Trace Viewer (auto-save on failure + attached Allure report) |
| Marker Layering | smoke / regression / api / ui / business modules |

***

## 🔗 Related Documentation

- [SECURITY_REPORT.md](SECURITY_REPORT.md) — Details of 16 bugs (including reproduction steps + fix suggestions)
- `scripts/reset_parabank.py` — Data reset tool (supports `--check` / `--quiet`)
- `scripts/probes/` — Diagnostic toolkit (boundary probing / contract sampling / page structure)
- `Jenkinsfile` — Jenkins Windows agent configuration
- `pytest.ini` — pytest configuration (markers / junit / allure)

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

##  Known Technical Debt

Transparency over perfection  these are known issues not yet addressed:

| ID | Issue | Severity | Plan |
|---|---|---|---|
| TD-01 | Duplicate account-fetching code in `test_api_soap_parabank.py` (~10 occurrences) | Minor | Extract as fixture in next iteration |
| TD-02 | Inconsistent parameter passing style (positional vs keyword) | Minor | Standardize to keyword args |
| TD-03 | Exception tests mix `requests` and `ParaBankBiz` | Minor | Route protocol-layer tests through a dedicated client |
| TD-04 | XML namespace handling inconsistent in `test_api_contract.py` | Minor | Unify all parsing through `_tag()` helper |
| TD-05 | Some test methods lack docstrings | Trivial | Add docstrings aligned with `@allure.title` |

**Fixed (from code review)**:

-  **C-01** Hardcoded config  centralized in `config/test_constants.py`
-  **M-05** HTTP requests lacked timeout  default 15s in `BaseApi` + `ParaBankBiz`
-  **Bug** `API_BASE_URL` in `.env` had wrong value (extra `/api`)  fixed

---

*All test cases can be reproduced with a single command.*
