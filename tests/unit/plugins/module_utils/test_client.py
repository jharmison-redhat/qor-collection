import logging
import os

import pytest

from ansible_collections.jharmison.crypto_qor.plugins.module_utils.client import QorApiClient
from ansible_collections.jharmison.crypto_qor.plugins.module_utils.models import QorEndpoint

try:  # for Python 3
    from http.client import HTTPConnection
except ImportError:
    from httplib import HTTPConnection
HTTPConnection.debuglevel = 1

logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

creation_test_cases = [
    {
        "remote_user_name": "core",
        "remote_user_password": "password",
        "local_endpoint": "qor1",
        "remote_endpoint": "qor2",
        "remote_ip": "10.1.5.22",
        "local_wg_ipport": "10.1.5.21:51820",
        "remote_wg_ipport": "10.1.5.22:51820",
        "pqc": "kyb1024",
    },
]


@pytest.fixture(scope="session")
def api_client():
    c = QorApiClient(os.getenv("QOR_TEST_ENDPOINT", "10.1.5.21:8000"))
    if c.is_healthy():
        if c.progress_step().get("status") != "ok":
            c.reset()
        yield c
        c.close_session()
    else:
        yield None


@pytest.fixture(autouse=True)
def skip_if_unavailable(api_client):
    if api_client is None:
        pytest.skip("no access to QOR endpoint for test")


def test_status_exists(api_client):
    _ = api_client.status()


def test_progress_exists(api_client):
    _ = api_client.progress()


def test_progress_step(api_client):
    resp = api_client.progress_step()
    assert resp.get("status") == "ok"


def test_create_endpoint(api_client):
    local_wg_ipport = f"{api_client.endpoint.ip}:51820"
    for test_case in creation_test_cases:
        test_case["local_wg_ipport"] = local_wg_ipport
        _ = api_client.create_endpoint(endpoint=QorEndpoint(**test_case))
