import pytest
from tests.api_test.services.customer_api import CustomerApi
from tests.api_test.services.loan_api import LoanApi
from tests.fixtures.db_fixture import query_loan_by_id

@pytest.mark.api
def test_loan_apply_full_flow(api_client):
    # 1. 创建客户，传入api_client实例
    customer_api = CustomerApi(api_client)
    customer_resp = customer_api.create_customer(name="test_loan_user")
    assert customer_resp.status_code == 201
    customer_info = customer_resp.json()
    customer_id = customer_info["id"]

    # 2. 申请贷款，传入api_client实例
    loan_api = LoanApi(api_client)
    loan_resp = loan_api.create_loan(customer_id=customer_id, amount=50000)
    assert loan_resp.status_code == 201
    loan_id = loan_resp.json()["id"]

    # 3. 接口查询校验
    query_resp = loan_api.get_loan(loan_id)
    assert query_resp.json()["customer_id"] == customer_id

    #4. 数据库一致性校验（先注释掉，因为db_conn fixture还没写）
    # db_result = query_loan_by_id(db_conn, loan_id)
    # assert db_result["amount"] == 50000
