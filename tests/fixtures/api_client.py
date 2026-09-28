import pytest
from tests.api_test.services.base_api import BaseApi

@pytest.fixture(scope="function")
def api_client():
    client = BaseApi()
    yield client
    client.session.close()
