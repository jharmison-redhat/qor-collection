from typing import Any
from typing import Optional

import requests

from ansible_collections.jharmison.crypto_qor.plugins.module_utils.logging import make_logger
from ansible_collections.jharmison.crypto_qor.plugins.module_utils.models import IPvAnySocketPair
from ansible_collections.jharmison.crypto_qor.plugins.module_utils.models import QorEndpoint
from ansible_collections.jharmison.crypto_qor.plugins.module_utils.models import Scheme


class QorApiClient(object):
    def __init__(self, endpoint: IPvAnySocketPair, scheme: Scheme = "http") -> None:
        self.endpoint: IPvAnySocketPair = endpoint
        self.scheme = scheme
        self._session: Optional[requests.Session] = None
        self.logger = make_logger()

    def __enter__(self) -> "QorApiClient":
        return self

    def __exit__(self, *_) -> None:
        self.close_session()

    @property
    def session(self) -> requests.Session:
        if self._session is None:
            self.logger.debug("Creating a new session")
            self._session = requests.Session()
        return self._session

    def close_session(self) -> None:
        if self._session is not None:
            self.logger.debug("Closing the session")
            self._session.close()
            self._session = None

    def _http_method(self, endpoint: str = "", http_method: str = "get") -> dict:
        endpoint = endpoint.lstrip("/")
        url = f"{self.scheme}://{self.endpoint}/{endpoint}"
        method = getattr(self.session, http_method)
        try:
            resp = method(url).json()
            self.logger.debug(f"{http_method.upper()}: [{url}]: {resp}")
        except Exception:
            self.logger.debug(f"{http_method.upper()}: [{url}]: <FAIL>")
            raise
        return resp

    def get(self, endpoint: str = "") -> dict:
        return self._http_method(endpoint)

    def is_healthy(self) -> bool:
        try:
            _ = self.get("")
            self.logger.debug("Healthy client")
            return True
        except Exception:  # noqa: E722
            self.logger.debug("Unhealthy client")
            return False

    def status(self) -> Any:
        return self.get("/status")
