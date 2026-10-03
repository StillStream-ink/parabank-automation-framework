import pytest
import allure
import xml.etree.ElementTree as ET

from tests.api_test.business.parabank_biz import ParaBankBiz
from config.test_constants import BASE_URL, USER_JOHN, CUSTOMER_ID_JOHN

pytestmark = [pytest.mark.api, pytest.mark.parabank, pytest.mark.transfer]

@allure.feature("ParaBank-REST接口测试")
class TestParaBankAPI:
    # ================== 账户查询 ==================
    @pytest.mark.smoke
    @allure.story("账户模块-查询本人账户列表")
    @allure.title("TC_PB_ACC_001 查询本人账户列表")
    def test_get_self_account_list(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        assert resp.status_code == 200
        root = ET.fromstring(resp.text)
        assert len(root.findall("account")) > 0

    @pytest.mark.xfail(reason="BUG_004 高危：水平越权漏洞，可读取其他客户账户")
    @allure.story("安全-水平越权")
    @allure.title("TC_PB_SEC_001 查询其他客户账户-水平越权")
    def test_get_other_customer_account_horizontal(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer_account_list(customer_id="99999")
        assert resp.status_code in [401, 403]

    @pytest.mark.xfail(reason="BUG_005 高危：未授权访问账户列表，无认证即可读取")
    @allure.story("安全-未授权访问")
    @allure.title("TC_PB_SEC_002 查询账户-不带鉴权信息")
    def test_get_account_no_auth(self):
        biz = ParaBankBiz(BASE_URL, auth=None)
        resp = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        assert resp.status_code in [401, 403]

    @allure.story("账户模块-账户详情")
    @allure.title("TC_PB_ACC_002 查询单个账户详情")
    def test_get_single_account_detail(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp_list.text)
        acc_id = root.find("account/id").text
        resp = biz.get_single_account_detail(acc_id)
        assert resp.status_code == 200

    @allure.story("账户-交易记录查询")
    @allure.title("TC_PB_QRY_001 查询账户交易记录")
    def test_get_account_transactions(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp_list.text)
        acc_id = root.find("account/id").text
        resp = biz.get_account_transactions(acc_id)
        assert resp.status_code == 200

    # ================== 转账 ==================
    @pytest.mark.smoke
    @allure.story("转账-正常转账")
    @allure.title("TC_PB_TX_001 本人账户之间正常金额转账")
    def test_transfer_funds_normal(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp.text)
        acc_list = root.findall("account")
        from_acc_id = acc_list[0].find("id").text
        to_acc_id = acc_list[1].find("id").text
        transfer_resp = biz.transfer_funds(from_acc_id, to_acc_id, 10)
        assert transfer_resp.status_code == 200

    @pytest.mark.xfail(reason="BUG_101：/transfer 未校验转账金额，允许 0 元转账")
    @allure.story("转账-边界")
    @allure.title("TC_PB_TX_002 转账金额等于0")
    def test_transfer_amount_zero(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp.text)
        acc_list = root.findall("account")
        from_acc_id = acc_list[0].find("id").text
        to_acc_id = acc_list[1].find("id").text
        transfer_resp = biz.transfer_funds(from_acc_id, to_acc_id, 0)
        assert transfer_resp.status_code != 200

    @pytest.mark.xfail(reason="BUG_102 高危：/transfer 未校验负数金额，会造成反向扣款")
    @allure.story("转账-边界")
    @allure.title("TC_PB_TX_003 转账金额负数")
    def test_transfer_amount_negative(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp.text)
        acc_list = root.findall("account")
        from_acc_id = acc_list[0].find("id").text
        to_acc_id = acc_list[1].find("id").text
        transfer_resp = biz.transfer_funds(from_acc_id, to_acc_id, -50)
        assert transfer_resp.status_code != 200

    @pytest.mark.xfail(reason="BUG_103 高危：/transfer 未校验余额，允许透支")
    @allure.story("转账-异常")
    @allure.title("TC_PB_TX_004 转账金额大于账户余额")
    def test_transfer_over_balance(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp.text)
        acc_list = root.findall("account")
        from_acc_id = acc_list[0].find("id").text
        to_acc_id = acc_list[1].find("id").text
        transfer_resp = biz.transfer_funds(from_acc_id, to_acc_id, 999999)
        assert transfer_resp.status_code != 200

    @pytest.mark.xfail(reason="BUG_104：/transfer 未校验转出转入账户不同，允许自己转自己")
    @allure.story("转账-异常")
    @allure.title("TC_PB_TX_005 转出转入为同一个账户")
    def test_transfer_same_account(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp.text)
        acc_id = root.find("account/id").text
        transfer_resp = biz.transfer_funds(acc_id, acc_id, 10)
        assert "error" in transfer_resp.text.lower() or transfer_resp.status_code != 200

    @pytest.mark.xfail(reason="BUG_105：/transfer 未校验单笔限额，允许任意金额")
    @allure.story("转账-边界")
    @allure.title("TC_PB_TX_006 转账超过单笔限额50001")
    def test_transfer_over_single_limit(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp.text)
        acc_list = root.findall("account")
        from_acc_id = acc_list[0].find("id").text
        to_acc_id = acc_list[1].find("id").text
        transfer_resp = biz.transfer_funds(from_acc_id, to_acc_id, 50001)
        assert transfer_resp.status_code != 200

    @pytest.mark.xfail(reason="BUG_006：/transfer 无幂等，重复请求会多次扣款")
    @allure.story("转账-安全防重")
    @allure.title("TC_PB_TX_007 快速重复提交转账")
    def test_transfer_duplicate_submit(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp.text)
        acc_list = root.findall("account")
        from_acc_id = acc_list[0].find("id").text
        to_acc_id = acc_list[1].find("id").text
        r1 = biz.transfer_funds(from_acc_id, to_acc_id, 100)
        r2 = biz.transfer_funds(from_acc_id, to_acc_id, 100)
        assert r2.status_code != 200

    @pytest.mark.xfail(reason="BUG_004 高危：跨客户转账水平越权")
    @allure.story("转账-安全越权")
    @allure.title("TC_PB_TX_008 转账到其他用户账户")
    def test_transfer_other_user_account(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp.text)
        acc_list = root.findall("account")
        from_acc_id = acc_list[0].find("id").text
        resp = biz.transfer_funds(from_acc_id=from_acc_id, to_acc_id="99999", amount=10)
        assert resp.status_code in [401, 403]

    # ================== 开户 ==================
    @allure.story("账户-开立新账户")
    @allure.title("TC_PB_ACC_003 正常开立新储蓄账户")
    def test_open_new_account(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp_list.text)
        from_acc_id = root.find("account/id").text
        resp = biz.open_new_account(
            customer_id=CUSTOMER_ID_JOHN,
            account_type=1,
            from_account_id=from_acc_id,
        )
        assert resp.status_code == 200

    # ================== 账单支付 ==================
    @allure.story("账单支付-正常支付")
    @allure.title("TC_PB_BILL_001 账单支付-正常金额")
    def test_bill_pay_normal(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp_list.text)
        acc_id = root.find("account/id").text
        resp = biz.pay_bill(account_id=acc_id, amount=10, payee_name="TestPayee")
        assert resp.status_code == 200

    @pytest.mark.xfail(reason="BUG_BILL_001 高危：ParaBank /billpay 未校验余额，超余额仍返回 200")
    @allure.story("账单支付-余额不足")
    @allure.title("TC_PB_BILL_002 账单支付-金额大于余额")
    def test_bill_pay_over_balance(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp_list.text)
        acc_id = root.find("account/id").text
        resp = biz.pay_bill(account_id=acc_id, amount=999999, payee_name="TestPayee")
        assert resp.status_code != 200

    # ================== 贷款 ==================
    @allure.story("贷款-正常申请贷款")
    @allure.title("TC_PB_LOAN_001 贷款申请正常场景")
    def test_loan_apply_normal(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp_list.text)
        from_acc_id = root.find("account/id").text
        resp = biz.apply_loan(
            customer_id=CUSTOMER_ID_JOHN,
            amount=1000,
            down_payment=100,
            from_account_id=from_acc_id,
        )
        assert resp.status_code == 200

    @allure.story("贷款-超过授信额度")
    @allure.title("TC_PB_LOAN_002 贷款申请-金额超出授信")
    def test_loan_apply_over_credit(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp_list.text)
        from_acc_id = root.find("account/id").text
        resp = biz.apply_loan(
            customer_id=CUSTOMER_ID_JOHN,
            amount=1000000,
            down_payment=100,
            from_account_id=from_acc_id,
        )
        body = resp.text.lower()
        assert ("denied" in body) or ("false" in body) or ("regret" in body)

    @allure.story("贷款-负数金额")
    @allure.title("TC_PB_LOAN_003 贷款申请-传入负数金额应被拒绝")
    def test_loan_apply_negative_amount(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp_list.text)
        from_acc_id = root.find("account/id").text
        resp = biz.apply_loan(
            customer_id=CUSTOMER_ID_JOHN,
            amount=-1000,
            down_payment=100,
            from_account_id=from_acc_id,
        )
        assert resp.status_code == 200
        body = resp.text.lower()
        assert "approved>false<" in body or "<approved>false</approved>" in body, \
            f"负数贷款应被拒绝，实际响应： {resp.text[:300]}"

    # ================== 响应结构 / 安全 ==================
    @allure.story("转账-响应报文结构校验")
    @allure.title("TC_PARA_020 校验转账接口返回报文结构")
    def test_transfer_response_schema(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp_list.text)
        acc_list = root.findall("account")
        from_acc_id = acc_list[0].find("id").text
        to_acc_id = acc_list[1].find("id").text
        resp = biz.transfer_funds(from_acc_id, to_acc_id, 10)
        assert resp.status_code == 200
        assert len(resp.text) > 0

    @allure.story("转账-SQL注入安全测试")
    @allure.title("TC_PARA_SEC_004 转账金额传入SQL注入语句")
    def test_transfer_sql_inject(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp_list.text)
        acc_list = root.findall("account")
        from_acc_id = acc_list[0].find("id").text
        to_acc_id = acc_list[1].find("id").text
        resp = biz.transfer_funds(from_acc_id, to_acc_id, "100 or 1=1 --")
        assert resp.status_code != 200

    @pytest.mark.xfail(reason="BUG_006: /transfer 无幂等，重复请求会多次扣款")
    @allure.story("转账-幂等性校验")
    @allure.title("TC_PARA_021 相同转账请求重复提交，不能多次扣钱")
    def test_transfer_idempotent(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp_list.text)
        acc_list = root.findall("account")
        from_acc_id = acc_list[0].find("id").text
        to_acc_id = acc_list[1].find("id").text
        r1 = biz.transfer_funds(from_acc_id, to_acc_id, 200)
        assert r1.status_code == 200
        r2 = biz.transfer_funds(from_acc_id, to_acc_id, 200)
        assert r2.status_code != 200

    @pytest.mark.xfail(reason="BUG_004 高危：存在水平越权，可操作他人账户资金")
    @allure.story("转账-水平越权安全测试")
    @allure.title("TC_PARA_SEC_005 使用A用户token以B用户账户发起转账")
    def test_transfer_horizontal_privilege(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.transfer_funds(from_acc_id="99999", to_acc_id="12345", amount=300)
        assert resp.status_code in [401, 403]


@allure.feature("ParaBank-REST接口测试")
class TestParaBankAPI:
    # ================== 账户查询 ==================
    @pytest.mark.smoke
    @allure.story("账户模块-查询本人账户列表")
    @allure.title("TC_PB_ACC_001 查询本人账户列表")
    def test_get_self_account_list(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        assert resp.status_code == 200
        root = ET.fromstring(resp.text)
        assert len(root.findall("account")) > 0

    @pytest.mark.xfail(reason="BUG_004 高危：水平越权漏洞，可读取其他客户账户")
    @allure.story("安全-水平越权")
    @allure.title("TC_PB_SEC_001 查询其他客户账户-水平越权")
    def test_get_other_customer_account_horizontal(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer_account_list(customer_id="99999")
        assert resp.status_code in [401, 403]

    @pytest.mark.xfail(reason="BUG_005 高危：未授权访问账户列表，无认证即可读取")
    @allure.story("安全-未授权访问")
    @allure.title("TC_PB_SEC_002 查询账户-不带鉴权信息")
    def test_get_account_no_auth(self):
        biz = ParaBankBiz(BASE_URL, auth=None)
        resp = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        assert resp.status_code in [401, 403]

    @allure.story("账户模块-账户详情")
    @allure.title("TC_PB_ACC_002 查询单个账户详情")
    def test_get_single_account_detail(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp_list.text)
        acc_id = root.find("account/id").text
        resp = biz.get_single_account_detail(acc_id)
        assert resp.status_code == 200

    @allure.story("账户-交易记录查询")
    @allure.title("TC_PB_QRY_001 查询账户交易记录")
    def test_get_account_transactions(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp_list.text)
        acc_id = root.find("account/id").text
        resp = biz.get_account_transactions(acc_id)
        assert resp.status_code == 200

    # ================== 转账 ==================
    @pytest.mark.smoke
    @allure.story("转账-正常转账")
    @allure.title("TC_PB_TX_001 本人账户之间正常金额转账")
    def test_transfer_funds_normal(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp.text)
        acc_list = root.findall("account")
        from_acc_id = acc_list[0].find("id").text
        to_acc_id = acc_list[1].find("id").text
        transfer_resp = biz.transfer_funds(from_acc_id, to_acc_id, 10)
        assert transfer_resp.status_code == 200

    @pytest.mark.xfail(reason="BUG_101：/transfer 未校验转账金额，允许 0 元转账")
    @allure.story("转账-边界")
    @allure.title("TC_PB_TX_002 转账金额等于0")
    def test_transfer_amount_zero(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp.text)
        acc_list = root.findall("account")
        from_acc_id = acc_list[0].find("id").text
        to_acc_id = acc_list[1].find("id").text
        transfer_resp = biz.transfer_funds(from_acc_id, to_acc_id, 0)
        assert transfer_resp.status_code != 200

    @pytest.mark.xfail(reason="BUG_102 高危：/transfer 未校验负数金额，会造成反向扣款")
    @allure.story("转账-边界")
    @allure.title("TC_PB_TX_003 转账金额负数")
    def test_transfer_amount_negative(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp.text)
        acc_list = root.findall("account")
        from_acc_id = acc_list[0].find("id").text
        to_acc_id = acc_list[1].find("id").text
        transfer_resp = biz.transfer_funds(from_acc_id, to_acc_id, -50)
        assert transfer_resp.status_code != 200

    @pytest.mark.xfail(reason="BUG_103 高危：/transfer 未校验余额，允许透支")
    @allure.story("转账-异常")
    @allure.title("TC_PB_TX_004 转账金额大于账户余额")
    def test_transfer_over_balance(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp.text)
        acc_list = root.findall("account")
        from_acc_id = acc_list[0].find("id").text
        to_acc_id = acc_list[1].find("id").text
        transfer_resp = biz.transfer_funds(from_acc_id, to_acc_id, 999999)
        assert transfer_resp.status_code != 200

    @pytest.mark.xfail(reason="BUG_104：/transfer 未校验转出转入账户不同，允许自己转自己")
    @allure.story("转账-异常")
    @allure.title("TC_PB_TX_005 转出转入为同一个账户")
    def test_transfer_same_account(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp.text)
        acc_id = root.find("account/id").text
        transfer_resp = biz.transfer_funds(acc_id, acc_id, 10)
        assert "error" in transfer_resp.text.lower() or transfer_resp.status_code != 200

    @pytest.mark.xfail(reason="BUG_105：/transfer 未校验单笔限额，允许任意金额")
    @allure.story("转账-边界")
    @allure.title("TC_PB_TX_006 转账超过单笔限额50001")
    def test_transfer_over_single_limit(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp.text)
        acc_list = root.findall("account")
        from_acc_id = acc_list[0].find("id").text
        to_acc_id = acc_list[1].find("id").text
        transfer_resp = biz.transfer_funds(from_acc_id, to_acc_id, 50001)
        assert transfer_resp.status_code != 200

    @pytest.mark.xfail(reason="BUG_006：/transfer 无幂等，重复请求会多次扣款")
    @allure.story("转账-安全防重")
    @allure.title("TC_PB_TX_007 快速重复提交转账")
    def test_transfer_duplicate_submit(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp.text)
        acc_list = root.findall("account")
        from_acc_id = acc_list[0].find("id").text
        to_acc_id = acc_list[1].find("id").text
        r1 = biz.transfer_funds(from_acc_id, to_acc_id, 100)
        r2 = biz.transfer_funds(from_acc_id, to_acc_id, 100)
        assert r2.status_code != 200

    @pytest.mark.xfail(reason="BUG_004 高危：跨客户转账水平越权")
    @allure.story("转账-安全越权")
    @allure.title("TC_PB_TX_008 转账到其他用户账户")
    def test_transfer_other_user_account(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp.text)
        acc_list = root.findall("account")
        from_acc_id = acc_list[0].find("id").text
        resp = biz.transfer_funds(from_acc_id=from_acc_id, to_acc_id="99999", amount=10)
        assert resp.status_code in [401, 403]

    # ================== 开户 ==================
    @allure.story("账户-开立新账户")
    @allure.title("TC_PB_ACC_003 正常开立新储蓄账户")
    def test_open_new_account(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp_list.text)
        from_acc_id = root.find("account/id").text
        resp = biz.open_new_account(
            customer_id=CUSTOMER_ID_JOHN,
            account_type=1,
            from_account_id=from_acc_id,
        )
        assert resp.status_code == 200

    # ================== 账单支付 ==================
    @allure.story("账单支付-正常支付")
    @allure.title("TC_PB_BILL_001 账单支付-正常金额")
    def test_bill_pay_normal(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp_list.text)
        acc_id = root.find("account/id").text
        resp = biz.pay_bill(account_id=acc_id, amount=10, payee_name="TestPayee")
        assert resp.status_code == 200

    @pytest.mark.xfail(reason="BUG_BILL_001 高危：ParaBank /billpay 未校验余额，超余额仍返回 200")
    @allure.story("账单支付-余额不足")
    @allure.title("TC_PB_BILL_002 账单支付-金额大于余额")
    def test_bill_pay_over_balance(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp_list.text)
        acc_id = root.find("account/id").text
        resp = biz.pay_bill(account_id=acc_id, amount=999999, payee_name="TestPayee")
        assert resp.status_code != 200

    # ================== 贷款 ==================
    @allure.story("贷款-正常申请贷款")
    @allure.title("TC_PB_LOAN_001 贷款申请正常场景")
    def test_loan_apply_normal(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp_list.text)
        from_acc_id = root.find("account/id").text
        resp = biz.apply_loan(
            customer_id=CUSTOMER_ID_JOHN,
            amount=1000,
            down_payment=100,
            from_account_id=from_acc_id,
        )
        assert resp.status_code == 200

    @allure.story("贷款-超过授信额度")
    @allure.title("TC_PB_LOAN_002 贷款申请-金额超出授信")
    def test_loan_apply_over_credit(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp_list.text)
        from_acc_id = root.find("account/id").text
        resp = biz.apply_loan(
            customer_id=CUSTOMER_ID_JOHN,
            amount=1000000,
            down_payment=100,
            from_account_id=from_acc_id,
        )
        body = resp.text.lower()
        assert ("denied" in body) or ("false" in body) or ("regret" in body)

    @allure.story("贷款-负数金额")
    @allure.title("TC_PB_LOAN_003 贷款申请-传入负数金额应被拒绝")
    def test_loan_apply_negative_amount(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp_list.text)
        from_acc_id = root.find("account/id").text
        resp = biz.apply_loan(
            customer_id=CUSTOMER_ID_JOHN,
            amount=-1000,
            down_payment=100,
            from_account_id=from_acc_id,
        )
        assert resp.status_code == 200
        body = resp.text.lower()
        assert "approved>false<" in body or "<approved>false</approved>" in body, \
            f"负数贷款应被拒绝，实际响应： {resp.text[:300]}"

    # ================== 响应结构 / 安全 ==================
    @allure.story("转账-响应报文结构校验")
    @allure.title("TC_PARA_020 校验转账接口返回报文结构")
    def test_transfer_response_schema(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp_list.text)
        acc_list = root.findall("account")
        from_acc_id = acc_list[0].find("id").text
        to_acc_id = acc_list[1].find("id").text
        resp = biz.transfer_funds(from_acc_id, to_acc_id, 10)
        assert resp.status_code == 200
        assert len(resp.text) > 0

    @allure.story("转账-SQL注入安全测试")
    @allure.title("TC_PARA_SEC_004 转账金额传入SQL注入语句")
    def test_transfer_sql_inject(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp_list.text)
        acc_list = root.findall("account")
        from_acc_id = acc_list[0].find("id").text
        to_acc_id = acc_list[1].find("id").text
        resp = biz.transfer_funds(from_acc_id, to_acc_id, "100 or 1=1 --")
        assert resp.status_code != 200

    @pytest.mark.xfail(reason="BUG_006: /transfer 无幂等，重复请求会多次扣款")
    @allure.story("转账-幂等性校验")
    @allure.title("TC_PARA_021 相同转账请求重复提交，不能多次扣钱")
    def test_transfer_idempotent(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp_list = biz.get_customer_account_list(CUSTOMER_ID_JOHN)
        root = ET.fromstring(resp_list.text)
        acc_list = root.findall("account")
        from_acc_id = acc_list[0].find("id").text
        to_acc_id = acc_list[1].find("id").text
        r1 = biz.transfer_funds(from_acc_id, to_acc_id, 200)
        assert r1.status_code == 200
        r2 = biz.transfer_funds(from_acc_id, to_acc_id, 200)
        assert r2.status_code != 200

    @pytest.mark.xfail(reason="BUG_004 高危：存在水平越权，可操作他人账户资金")
    @allure.story("转账-水平越权安全测试")
    @allure.title("TC_PARA_SEC_005 使用A用户token以B用户账户发起转账")
    def test_transfer_horizontal_privilege(self):
        biz = ParaBankBiz(BASE_URL, USER_JOHN)
        resp = biz.transfer_funds(from_acc_id="99999", to_acc_id="12345", amount=300)
        assert resp.status_code in [401, 403]