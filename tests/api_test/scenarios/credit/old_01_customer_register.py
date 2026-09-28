import pytest
from tests.api_test.business.loan_biz import CustomerBiz

@pytest.mark.api
def test_customer_register(api_client):
    customer_biz = CustomerBiz(api_client)
    res = customer_biz.register(name="张三", age=22, income=8000, credit_score=700)
    assert res.status_code == 201
    data = res.json()
    assert "customer_id" in data
    assert isinstance(data["customer_id"], int)
