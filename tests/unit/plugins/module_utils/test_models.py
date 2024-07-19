import pytest
from pydantic_core import ValidationError

from ansible_collections.jharmison.crypto_qor.plugins.module_utils.models import IPvAnySocketPair
from ansible_collections.jharmison.crypto_qor.plugins.module_utils.models import QorEndpoint

socket_pair_test_cases = [
    "10.1.1.1:8000",
    "[::]:8000",
    "[::ff]:8000",
    "[2001:0db8:0000:0000:0000:7a6e:0680:9668]:8000",
    "[2001:0db8::7a6e:0680:9668]:8000",
    "127.0.0.1:65535",
    "196.168.1.1:1",
]
socket_pair_test_failure_cases = [
    "a",
    "10.1.1.1",
    "10.1.1.1:0",
    "10.1.1.1.2:8000",
    "10.1.1.1:65536",
    ":::8000",
    "2001:0db8:0000:0000:0000:7a6e:0680:9668",
    "[2001:0db8::7a6e:0680:9668]:",
    "",
]
qor_endpoint_test_cases = [
    {
        "remote_user_name": "core",
        "remote_user_password": "password",
        "local_endpoint": "qor1",
        "remote_endpoint": "qor2",
        "remote_ip": "10.1.1.22",
        "local_wg_ipport": "10.1.1.21:5280",
        "remote_wg_ipport": "10.1.1.22:5280",
        "pqc": "kyb1024",
    },
    {
        "remote_user_name": "core",
        "remote_user_password": "password",
        "local_endpoint": "qor1",
        "remote_endpoint": "qor2",
        "remote_ip": "10.1.1.22",
        "local_wg_ipport": "10.1.1.21:5280",
        "remote_wg_ipport": "10.1.1.22:5280",
        "pqc": "kyb768",
    },
    {
        "remote_user_name": "core",
        "remote_user_password": "password",
        "local_endpoint": "qor1",
        "remote_endpoint": "qor2",
        "remote_ip": "2001:db8:3333:4444:5555:6666:7777:8888",
        "local_wg_ipport": "[2001:db8:3333:4444:CCCC:DDDD:EEEE:FFFF]:5280",
        "remote_wg_ipport": "[2001:db8:3333:4444:5555:6666:7777:8888]:5280",
        "pqc": "mce8",
    },
]
qor_endpoint_test_failure_cases = [
    {
        "remote_user_name": "core",
        "remote_user_password": "password",
        "local_endpoint": "qor1",
        "remote_endpoint": "qor2",
        "remote_ip": "10.1.1.22",
        "local_wg_ipport": "10.1.1.21",
        "remote_wg_ipport": "10.1.1.22:5280",
        "pqc": "kyb768",
    },
    {
        "remote_user_name": "core",
        "remote_user_password": "password",
        "local_endpoint": "qor1",
        "remote_endpoint": "qor2",
        "remote_ip": "google.com",
        "local_wg_ipport": "10.1.1.21:5280",
        "remote_wg_ipport": "10.1.1.22:5280",
        "pqc": "kyb768",
    },
    {
        "remote_user_name": "core",
        "remote_user_password": "password",
        "local_endpoint": "qor1",
        "remote_endpoint": "qor2",
        "remote_ip": "10.1.1.22",
        "pqc": "kyb768",
    },
    {
        "remote_user_name": "core",
        "local_endpoint": "qor1",
        "remote_endpoint": "qor2",
        "remote_ip": "2001:db8:3333:4444:5555:6666:7777:8888",
        "local_wg_ipport": "[2001:db8:3333:4444:CCCC:DDDD:EEEE:FFFF]:5280",
        "remote_wg_ipport": "[2001:db8:3333:4444:5555:6666:7777:8888]:5280",
        "pqc": "mce8",
    },
    {
        "remote_user_name": "core",
        "remote_user_password": "password",
        "local_endpoint": "qor1",
        "remote_endpoint": "qor2",
        "remote_ip": "2001:db8:3333:4444:5555:6666:7777:8888",
        "local_wg_ipport": "2001:db8:3333:4444:CCCC:DDDD:EEEE:FFFF:5280",
        "remote_wg_ipport": "2001:db8:3333:4444:5555:6666:7777:8888:5280",
        "pqc": "mce8",
    },
    {
        "remote_user_name": "core",
        "remote_user_password": "password",
        "local_endpoint": "qor1",
        "remote_endpoint": "qor2",
        "remote_ip": "2001:db8:3333:4444:5555:6666:7777:8888",
        "local_wg_ipport": "[2001:db8:3333:4444:CCCC:DDDD:EEEE:FFFF]:5280",
        "remote_wg_ipport": "[2001:db8:3333:4444:5555:6666:7777:8888]:5280",
        "pqc": "kyb512",
    },
]


def test_valid_socket_pair():
    for test_case in socket_pair_test_cases:
        print(f"Testing expected success: {test_case}")
        _ = IPvAnySocketPair.validate(test_case)
    for test_case in socket_pair_test_failure_cases:
        print(f"Testing expected failure: {test_case}")
        with pytest.raises(ValueError):
            _ = IPvAnySocketPair.validate(test_case)


def test_socket_pair_serialization():
    for test_case in socket_pair_test_cases:
        assert str(test_case) == IPvAnySocketPair(test_case)
        assert test_case == str(IPvAnySocketPair(test_case))


def test_qor_endpoint_instantiation():
    for test_case in qor_endpoint_test_cases:
        _ = QorEndpoint(**test_case)
    for test_case in qor_endpoint_test_failure_cases:
        print(f"Testing expected failure: {test_case}")
        with pytest.raises(ValidationError):
            _ = QorEndpoint(**test_case)
