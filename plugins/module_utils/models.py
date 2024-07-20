import re
from enum import Enum
from typing import Optional
from typing import Tuple

from pydantic import BaseModel
from pydantic import IPvAnyAddress
from pydantic_core import CoreSchema
from pydantic_core import core_schema

ipv4_regex = re.compile(
    r"^(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])"
)
bounded_ipv6_regex = re.compile(
    r"^\[(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))\]"
)
socket_port = re.compile(r"^(\[?[^]]*\]?):([0-9]+)$")


class StrEnum(str, Enum):
    """Represent a choice between a fixed set of strings.

    A mix-in of string and enum, representing itself as the string value.
    """

    @classmethod
    def list(cls) -> list:
        """Return a list of the available options in the Enum."""
        return [e.value for e in cls]

    def __str__(self) -> str:
        """Return only the value of the enum when cast to String."""
        return self.value


class PQCAlgo(StrEnum):
    KYB1024 = "kyb1024"
    KYB768 = "kyb768"
    MCE4 = "mce4"
    MCE6 = "mce6"
    MCE8 = "mce8"


class Scheme(StrEnum):
    HTTP = "http"
    HTTPS = "https"


class IPvAnySocketPair(str):
    ip: str
    port: int

    @classmethod
    def __get_pydantic_core_schema__(cls, *_) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls.validate, core_schema.str_schema())

    def __repr__(self):
        return f"IPvAnySocketPair({super().__repr__()})"

    @staticmethod
    def validate(v: str) -> "IPvAnySocketPair":
        if not isinstance(v, str):
            raise TypeError("IPvAnySocketPairs should be of type str")

        match = socket_port.fullmatch(v)
        if match is None:
            raise ValueError("Invalid IP/Socket Pair Format")

        ip, port = match.groups()
        if not ip or not port:
            raise ValueError("Invalid IP/Socket Pair format")

        if not ipv4_regex.fullmatch(ip) and not bounded_ipv6_regex.fullmatch(ip):
            raise ValueError("Invalid IPv4 IPv6 format")
        try:
            port = int(port)
        except ValueError:
            raise ValueError("Invalid Port Type")

        if port <= 0 or port > 65535:
            raise ValueError("Invalid Port Number")

        socket_pair = IPvAnySocketPair(f"{ip}:{port}")
        socket_pair.ip = ip
        socket_pair.port = port
        return socket_pair


class QorEndpoint(BaseModel):
    remote_user_name: str
    remote_user_password: str
    remote_root_password: Optional[str] = None
    local_endpoint: str
    remote_endpoint: str
    remote_ip: IPvAnyAddress
    local_wg_ipport: IPvAnySocketPair
    remote_wg_ipport: IPvAnySocketPair
    pqc: PQCAlgo = PQCAlgo.KYB1024
