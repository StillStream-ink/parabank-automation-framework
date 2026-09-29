"""ParaBank 响应契约校验  用 pydantic 校验字段名/类型/必填。"""
import pytest
import xml.etree.ElementTree as ET

import allure

from tests.api_test.business.parabank_biz import ParaBankBiz
from tests.api_test.schemas.parabank_schemas import (
    Account,
    BillPayResult,
    Customer,
    LoanResponse,
    Transaction,
)

BASE_URL = "http://localhost:8080/parabank/services/bank"
USER_JOHN = ("john", "demo")
CUSTOMER_ID = "12212"
ACCOUNT_ID = "54321"


# ==================== XML  dict 辅助 ====================

def _tag(elem):
    """去掉 namespace 前缀。"""
    return elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag


def _customer_dict(xml_text):
    root = ET.fromstring(xml_text)
    return {
        "id": int(root.find("id").text),
        "firstName": root.find("firstName").text,
        "lastName": root.find("lastName").text,
        "address": {
            "street": root.find("address/street").text,
            "city": root.find("address/city").text,
            "state": root.find("address/state").text,
            "zipCode": root.find("address/zipCode").text,
        },
        "phoneNumber": root.find("phoneNumber").text,
        "ssn": root.find("ssn").text,
    }


def _account_dict(elem):
    return {
        "id": int(elem.find("id").text),
        "customerId": int(elem.find("customerId").text),
        "type": elem.find("type").text,
        "balance": elem.find("balance").text,
    }


def _transaction_dict(elem):
    return {
        "id": int(elem.find("id").text),
        "accountId": int(elem.find("accountId").text),
        "type": elem.find("type").text,
        "date": elem.find("date").text,
        "amount": elem.find("amount").text,
        "description": elem.find("description").text,
    }


def _find_child_text(root, name):
    """在带 namespace 的根节点下查找无 namespace 的子节点文本。"""
    for child in root:
        if _tag(child) == name:
            return child.text
    return None


# ==================== 用例 ====================

pytestmark = [pytest.mark.api, pytest.mark.parabank]

@allure.feature("ParaBank-响应契约校验")
class TestContract:

    @pytest.mark.smoke
    @allure.story("客户信息契约")
    @allure.title("TC_CT_001 登录响应的字段结构符合契约")
    def test_login_contract(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.login("john", "demo")
        assert resp.status_code == 200
        Customer(**_customer_dict(resp.text))

    @allure.story("客户信息契约")
    @allure.title("TC_CT_002 客户信息响应的字段结构符合契约")
    def test_customer_contract(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer(CUSTOMER_ID)
        assert resp.status_code == 200
        Customer(**_customer_dict(resp.text))

    @allure.story("账户契约")
    @allure.title("TC_CT_003 账户详情响应的字段结构符合契约")
    def test_account_detail_contract(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_single_account_detail(ACCOUNT_ID)
        assert resp.status_code == 200
        Account(**_account_dict(ET.fromstring(resp.text)))

    @allure.story("账户契约")
    @allure.title("TC_CT_004 账户列表响应的字段结构符合契约")
    def test_account_list_contract(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer_account_list(CUSTOMER_ID)
        assert resp.status_code == 200
        root = ET.fromstring(resp.text)
        accounts = root.findall("account")
        assert len(accounts) > 0, "账户列表为空"
        for acc in accounts:
            Account(**_account_dict(acc))

    @allure.story("交易契约")
    @allure.title("TC_CT_005 交易流水的字段结构符合契约")
    def test_transaction_list_contract(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_account_transactions(ACCOUNT_ID)
        assert resp.status_code == 200
        root = ET.fromstring(resp.text)
        for tx in root.findall("transaction"):
            Transaction(**_transaction_dict(tx))

    @allure.story("交易契约")
    @allure.title("TC_CT_006 单笔交易查询的字段结构符合契约")
    def test_transaction_single_contract(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        tx_id = (
            ET.fromstring(biz.get_account_transactions(ACCOUNT_ID).text)
            .find("transaction/id")
            .text
        )
        resp = biz.get_transaction_by_id(tx_id)
        assert resp.status_code == 200
        Transaction(**_transaction_dict(ET.fromstring(resp.text)))

    @allure.story("贷款契约")
    @allure.title("TC_CT_007 贷款响应的字段结构符合契约")
    def test_loan_contract(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.apply_loan(CUSTOMER_ID, 1000, 100, ACCOUNT_ID)
        assert resp.status_code == 200
        root = ET.fromstring(resp.text)
        approved_text = _find_child_text(root, "approved")
        account_id_text = _find_child_text(root, "accountId")
        data = {
            "responseDate": _find_child_text(root, "responseDate"),
            "loanProviderName": _find_child_text(root, "loanProviderName"),
            "approved": approved_text == "true",
            "accountId": int(account_id_text) if account_id_text else None,
        }
        LoanResponse(**data)

    @allure.story("账单契约")
    @allure.title("TC_CT_008 账单支付响应的字段结构符合契约")
    def test_bill_pay_contract(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.pay_bill(ACCOUNT_ID, 10)
        assert resp.status_code == 200
        root = ET.fromstring(resp.text)
        data = {
            "accountId": int(root.find("accountId").text),
            "amount": root.find("amount").text,
            "payeeName": root.find("payeeName").text,
        }
        BillPayResult(**data)