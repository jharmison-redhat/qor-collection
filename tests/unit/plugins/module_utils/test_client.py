import os

import pytest

from ansible_collections.jharmison.crypto_qor.plugins.module_utils.client import QorApiClient


@pytest.fixture(scope="session")
def api_client():
    c = QorApiClient(os.getenv("QOR_TEST_ENDPOINT", "10.1.5.21:8000"))
    if c.is_healthy():
        yield c
        c.close_session()
    else:
        yield None


def test_status_exists(api_client):
    if api_client is None:
        pytest.skip("no access to QOR endpoint for test")
    _ = api_client.status()
