import xml.etree.ElementTree as ET

import allure
import pytest

from config.test_constants import BASE_URL, CUSTOMER_ID_JOHN, USER_JOHN
from tests.api_test.business.parabank_biz import ParaBankBiz

pytestmark = [pytest.mark.api, pytest.mark.parabank, pytest.mark.login]

@allure.feature("ParaBank-登录/客户信息接口")
class TestLoginCustomer:

    # ==================== 登录 ====================

    @pytest.mark.smoke
    @allure.story("登录-正常")
    @allure.title("TC_PB_LOGIN_001 正确账号密码登录")
    def test_login_success(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.login("john", "demo")
        assert resp.status_code == 200
        root = ET.fromstring(resp.text)
        assert root.find("id").text == CUSTOMER_ID_JOHN

    @allure.story("登录-异常")
    @allure.title("TC_PB_LOGIN_002 错误密码登录")
    def test_login_wrong_password(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.login("john", "wrong_password")
        assert resp.status_code != 200, "错误密码应被拒绝"

    @allure.story("登录-异常")
    @allure.title("TC_PB_LOGIN_003 不存在的用户名登录")
    def test_login_invalid_user(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.login("no_such_user", "xxx")
        assert resp.status_code != 200

    # ==================== 客户信息 ====================

    @allure.story("客户信息-正常")
    @allure.title("TC_PB_CUST_001 查询本人客户信息")
    def test_get_customer_normal(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer(CUSTOMER_ID_JOHN)
        assert resp.status_code == 200
        root = ET.fromstring(resp.text)
        assert root.find("firstName").text == "John"
        assert root.find("lastName").text == "Smith"

    @pytest.mark.xfail(reason="BUG_004 高危：/customers/{id} 水平越权，可读他人信息")
    @allure.story("客户信息-安全")
    @allure.title("TC_PB_CUST_002 查询其他客户信息-水平越权")
    def test_get_customer_horizontal_privilege(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer("99999")
        assert resp.status_code in (401, 403, 404), "越权查询应被拒绝"

    @pytest.mark.xfail(reason="BUG_005 高危：/customers/{id} 未授权访问")
    @allure.story("客户信息-安全")
    @allure.title("TC_PB_CUST_003 未授权查询客户信息")
    def test_get_customer_no_auth(self):
        biz = ParaBankBiz(BASE_URL, auth=None)
        resp = biz.get_customer(CUSTOMER_ID_JOHN)
        assert resp.status_code in (401, 403), "未授权应被拒绝"
