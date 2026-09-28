# Credit Approval Test Framework
参考ParaBank自动化测试骨架搭建，一体化测试框架：**API接口自动化 + Playwright UI E2E自动化**
共用一套环境配置、测试数据、pytest fixtures，支持混合场景：UI操作页面 + API校验 + 数据库一致性校验。

## 环境安装
```bash
pip install -r requirements.txt
playwright install

## 执行用例

```
# 仅执行接口自动化
pytest -m api

# 仅执行UI自动化
pytest -m ui

# 全部用例执行
pytest

# 生成allure报告
allure generate allure-results --clean
allure open
```

## 目录说明

- tests/api_test：接口自动化模块
- tests/ui_test：UI 网页自动化模块（Playwright+POM）
- tests/data：测试数据
- tests/fixtures：公共夹具
- tests/finalize：测试后置脏数据清理

```

## 16. 项目根目录 run_test.sh
```bash
#!/bin/bash
echo "===== 开始执行API自动化 ====="
pytest -m api
echo "===== API执行完成，开始执行UI自动化 ====="
pytest -m ui
echo "===== 全部用例执行完毕，生成Allure报告 ====="
allure generate allure-results --clean
allure open
```

---

### ✅ UI 相关文件暂时先空着

`tests/ui_test/pages/` 和 `tests/ui_test/scenarios/` 的 py 文件先不用写代码，接口部分跑通之后再来写 POM 页面类和 UI 场景用例。