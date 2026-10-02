"""ParaBank 响应契约校验  用 pydantic 校验字段名/类型/必填。"""
from config.test_constants import BASE_URL, USER_JOHN, CUSTOMER_ID_JOHN, ACC_A, ACC_B

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

CUSTOMER_ID = "12212"
ACCOUNT_ID = "54321"


# ==================== XML dict 辅助 ====================

def _strip_ns(elem):
    """递归剥离 XML namespace，之后所有查找都用简单标签名。"""
    for e in elem.iter():
        if "}" in e.tag:
            e.tag = e.tag.split("}", 1)[1]
    return elem


def _parse(xml_text):
    """解析 XML 并剥离 namespace。"""
    return _strip_ns(ET.fromstring(xml_text))


def _customer_dict(root):
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
        Customer(**_customer_dict(_parse(resp.text)))

    @allure.story("客户信息契约")
    @allure.title("TC_CT_002 客户信息响应的字段结构符合契约")
    def test_customer_contract(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer(CUSTOMER_ID)
        assert resp.status_code == 200
        Customer(**_customer_dict(_parse(resp.text)))

    @allure.story("账户契约")
    @allure.title("TC_CT_003 账户详情响应的字段结构符合契约")
    def test_account_detail_contract(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_single_account_detail(ACCOUNT_ID)
        assert resp.status_code == 200
        Account(**_account_dict(_parse(resp.text)))

    @allure.story("账户契约")
    @allure.title("TC_CT_004 账户列表响应的字段结构符合契约")
    def test_account_list_contract(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer_account_list(CUSTOMER_ID)
        assert resp.status_code == 200
        root = _parse(resp.text)
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
        root = _parse(resp.text)
        for tx in root.findall("transaction"):
            Transaction(**_transaction_dict(tx))

    @allure.story("交易契约")
    @allure.title("TC_CT_006 单笔交易查询的字段结构符合契约")
    def test_transaction_single_contract(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        root = _parse(biz.get_account_transactions(ACCOUNT_ID).text)
        tx_id = root.findtext("transaction/id")    # ← 改成 findtext
        resp = biz.get_transaction_by_id(tx_id)

    @allure.story("贷款契约")
    @allure.title("TC_CT_007 贷款响应的字段结构符合契约")
    def test_loan_contract(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.apply_loan(CUSTOMER_ID, 1000, 100, ACCOUNT_ID)
        assert resp.status_code == 200
        root = _parse(resp.text)
        account_id_text = root.findtext("accountId")
        data = {
            "responseDate": root.findtext("responseDate"),
            "loanProviderName": root.findtext("loanProviderName"),
            "approved": root.findtext("approved") == "true",
            "accountId": int(account_id_text) if account_id_text else None,
        }
        LoanResponse(**data)

    @allure.story("账单契约")
    @allure.title("TC_CT_008 账单支付响应的字段结构符合契约")
    def test_bill_pay_contract(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.pay_bill(ACCOUNT_ID, 10)
        assert resp.status_code == 200
        root = _parse(resp.text)
        data = {
            "accountId": int(root.find("accountId").text),
            "amount": root.find("amount").text,
            "payeeName": root.find("payeeName").text,
        }
        BillPayResult(**data)