class CreditApiBiz:
    def __init__(self, api_client, use_token: bool = True):
        self.client = api_client
        self.use_token = use_token
        self.base_path = "/api/v1"

    def register_customer(self, payload: dict):
        """用户注册"""
        return self.client.post(f"{self.base_path}/register/", json=payload)

    def check_eligibility(self, payload: dict):
        """贷款资格检查"""
        return self.client.post(f"{self.base_path}/check-eligibility/", json=payload)

    def create_loan(self, payload: dict):
        """创建贷款申请"""
        return self.client.post(f"{self.base_path}/create-loan/", json=payload)

    def query_loan(self, loan_id: int):
        """查询单条贷款"""
        return self.client.get(f"{self.base_path}/view-loan/{loan_id}/")

    def loan_repay(self, payload: dict):
        """贷款还款"""
        return self.client.post(f"{self.base_path}/loan-repay/", json=payload)

    def get_test_customer_id(self):
        """
        获取一个可用测试客户ID
        实际项目：可以在这里自动注册一个测试用户，返回customer_id
        """
        # 后续可改成自动注册；现在先写死，待Django服务启动后可替换
        return 1
