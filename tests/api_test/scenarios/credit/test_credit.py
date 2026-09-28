import pytest
import allure
from tests.api_test.business.credit_biz import CreditApiBiz

# 占位模拟类，仅用于pytest收集，后续实现credit_biz后删除
class CreditApiBiz:
    def __init__(self, use_token=True):
        pass
    def register_customer(self,payload):raise NotImplementedError("待实现biz层")
    def check_eligibility(self,req_data):raise NotImplementedError("待实现biz层")
    def get_test_customer_id(self):raise NotImplementedError("待实现biz层")
    def create_loan(self,payload):raise NotImplementedError("待实现biz层")
    def query_loan(self,loan_id):raise NotImplementedError("待实现biz层")
    def loan_repay(self,payload):raise NotImplementedError("待实现biz层")


@allure.feature("信贷审批API测试")
class TestCreditApi:
    @allure.story("用户注册")
    @allure.title("TC_CRED_001 正常注册客户")
    def test_customer_register_normal(self, api_client):
        biz = CreditApiBiz(api_client, use_token=True)
        payload = {"name": "张三", "age": 22, "income": 8000, "credit_score": 700}
        res = biz.register_customer(payload)
        assert res.status_code == 201
        data = res.json()
        assert "customer_id" in data
        assert isinstance(data["customer_id"], int)


    @allure.story("资格校验-边界场景")
    @allure.title("TC_CRED_002 年龄刚好18岁，满足资格")
    @pytest.mark.parametrize("req_data, expect_pass", [
        ({"age": 18, "income":5000, "credit_score":650}, True),
        ({"age": 17, "income":5000, "credit_score":650}, False),
        ({"age": 60, "income":5000, "credit_score":650}, True),
        ({"age": 61, "income":5000, "credit_score":650}, False),
    ])
    def test_eligibility_age_boundary(self, req_data, expect_pass):
        biz = CreditApiBiz()
        res = biz.check_eligibility(req_data)
        data = res.json()
        if expect_pass:
            assert data["eligible"] is True
        else:
            assert data["eligible"] is False

    @allure.story("资格校验-信用分边界")
    @allure.title("TC_CRED_003 信用分数边界校验")
    @pytest.mark.parametrize("req_data, expect_pass", [
        ({"age": 30, "income":5000, "credit_score":600}, True),
        ({"age": 30, "income":5000, "credit_score":599}, False),
    ])
    def test_eligibility_credit_score_boundary(self, req_data, expect_pass):
        biz = CreditApiBiz()
        res = biz.check_eligibility(req_data)
        data = res.json()
        if expect_pass:
            assert data["eligible"] is True
        else:
            assert data["eligible"] is False

    @allure.story("创建贷款-金额边界校验")
    @allure.title("TC_CRED_004 贷款金额=0，非法输入")
    @pytest.mark.xfail(reason="Bug:后端未校验，允许贷款金额为0")
    def test_create_loan_amount_zero(self):
        biz = CreditApiBiz()
        customer_id = biz.get_test_customer_id()
        payload = {"customer_id": customer_id, "amount": 0, "term":12}
        res = biz.create_loan(payload)
        assert res.status_code != 201

    @allure.story("创建贷款-金额边界校验")
    @allure.title("TC_CRED_005 贷款金额负数")
    @pytest.mark.xfail(reason="Bug:后端未拦截负数贷款金额")
    def test_create_loan_amount_negative(self):
        biz = CreditApiBiz()
        customer_id = biz.get_test_customer_id()
        payload = {"customer_id": customer_id, "amount": -1000, "term":12}
        res = biz.create_loan(payload)
        assert res.status_code != 201

    @allure.story("贷款查询-安全测试：水平越权")
    @allure.title("TC_CRED_SEC_001 查看其他用户贷款记录，水平越权")
    @pytest.mark.xfail(reason="高危Bug：存在水平越权，可查看别人贷款")
    def test_loan_query_horizontal_privilege(self):
        biz = CreditApiBiz()
        res = biz.query_loan(loan_id=99999)
        assert res.status_code in [401,403]

    @allure.story("贷款查询-安全测试：未授权访问")
    @allure.title("TC_CRED_SEC_002 查询贷款不带token")
    @pytest.mark.xfail(reason="高危Bug：无token也能查到贷款信息")
    def test_loan_query_no_token(self):
        biz = CreditApiBiz(use_token=False)
        res = biz.query_loan(loan_id=10001)
        assert res.status_code in [401,403]

    @allure.story("贷款期限边界校验")
    @allure.title("TC_CRED_006 贷款期限=0")
    @pytest.mark.xfail(reason="Bug:期限为0没有拦截")
    def test_create_loan_term_zero(self):
        biz = CreditApiBiz()
        customer_id = biz.get_test_customer_id()
        payload = {"customer_id": customer_id, "amount": 10000, "term":0}
        res = biz.create_loan(payload)
        assert res.status_code != 201

    @allure.story("正常创建贷款")
    @allure.title("TC_CRED_007 合法参数创建贷款成功")
    def test_create_loan_normal(self):
        biz = CreditApiBiz()
        customer_id = biz.get_test_customer_id()
        payload = {"customer_id": customer_id, "amount": 50000, "term":12}
        res = biz.create_loan(payload)
        assert res.status_code == 201
        data = res.json()
        assert "loan_id" in data

    @allure.story("查询本人贷款")
    @allure.title("TC_CRED_008 查询当前用户自己的贷款记录")
    def test_query_self_loan(self):
        biz = CreditApiBiz()
        customer_id = biz.get_test_customer_id()
        loan_resp = biz.create_loan({"customer_id": customer_id, "amount":20000, "term":24})
        loan_id = loan_resp.json()["loan_id"]
        res = biz.query_loan(loan_id)
        assert res.status_code == 200
        assert res.json()["customer_id"] == customer_id

    @allure.story("还款-正常还款")
    @allure.title("TC_CRED_009 正常还款")
    def test_loan_repay_normal(self):
        biz = CreditApiBiz()
        customer_id = biz.get_test_customer_id()
        loan_resp = biz.create_loan({"customer_id": customer_id, "amount":20000, "term":24})
        loan_id = loan_resp.json()["loan_id"]
        res = biz.loan_repay({"loan_id":loan_id, "pay_amount":1000})
        assert res.status_code == 200

    @allure.story("还款-超额还款")
    @allure.title("TC_CRED_010 还款金额大于贷款总额")
    @pytest.mark.xfail(reason="Bug：超额还款没有做限制")
    def test_loan_repay_over_amount(self):
        biz = CreditApiBiz()
        customer_id = biz.get_test_customer_id()
        loan_resp = biz.create_loan({"customer_id": customer_id, "amount":20000, "term":24})
        loan_id = loan_resp.json()["loan_id"]
        res = biz.loan_repay({"loan_id":loan_id, "pay_amount":999999})
        assert res.status_code !=200

    @allure.story("贷款查询-响应Schema校验")
    @allure.title("TC_CRED_011 校验贷款查询返回报文结构")
    def test_loan_query_response_schema(self, api_client):
        import jsonschema
        biz = CreditApiBiz(api_client, use_token=True)
        customer_id = biz.get_test_customer_id()
        loan_resp = biz.create_loan({"customer_id": customer_id, "amount":20000, "term":24})
        loan_id = loan_resp.json()["loan_id"]
        res = biz.query_loan(loan_id)
        assert res.status_code == 200
        resp_data = res.json()
        # 定义响应json schema
        loan_schema = {
            "type": "object",
            "properties": {
                "loan_id": {"type": "integer"},
                "customer_id": {"type": "integer"},
                "amount": {"type": "number"},
                "term": {"type": "integer"},
                "status": {"type": "string"}
            },
            "required": ["loan_id", "customer_id", "amount", "term", "status"]
        }
        # 校验报文结构
        jsonschema.validate(instance=resp_data, schema=loan_schema)


    @allure.story("创建贷款-SQL注入测试")
    @allure.title("TC_CRED_SEC_003 贷款金额参数传入SQL注入语句")
    @pytest.mark.xfail(reason="高危Bug：接口未过滤特殊字符，存在SQL注入风险")
    def test_create_loan_sql_inject(self, api_client):
        biz = CreditApiBiz(api_client, use_token=True)
        customer_id = biz.get_test_customer_id()
        # SQL注入payload
        payload = {"customer_id": customer_id, "amount": "100 or 1=1 --", "term":12}
        res = biz.create_loan(payload)
        # 预期：后端识别非法参数，拒绝创建，返回400
        assert res.status_code != 201


    @allure.story("创建贷款-幂等性校验")
    @allure.title("TC_CRED_012 同一笔贷款请求重复提交，不可重复生成贷款")
    @pytest.mark.xfail(reason="Bug：接口无幂等控制，重复请求会新增多条贷款记录")
    def test_create_loan_idempotent(self, api_client):
        biz = CreditApiBiz(api_client, use_token=True)
        customer_id = biz.get_test_customer_id()
        payload = {"customer_id": customer_id, "amount": 10000, "term":12}
        # 第一次请求
        res1 = biz.create_loan(payload)
        assert res1.status_code == 201
        loan_id_1 = res1.json()["loan_id"]
        # 完全相同请求，重复提交
        res2 = biz.create_loan(payload)
        # 预期：返回400/409，不新建贷款
        loan_id_2 = res2.json().get("loan_id")
        assert loan_id_2 == loan_id_1

