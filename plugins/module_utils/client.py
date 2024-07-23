from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import requests

from ansible_collections.jharmison.crypto_qor.plugins.module_utils.logging import make_logger
from ansible_collections.jharmison.crypto_qor.plugins.module_utils.models import IPvAnySocketPair
from ansible_collections.jharmison.crypto_qor.plugins.module_utils.models import QorEndpoint
from ansible_collections.jharmison.crypto_qor.plugins.module_utils.models import Scheme


class QorApiError(Exception):
    pass


class QorApiClient(object):
    def __init__(self, endpoint: IPvAnySocketPair, scheme: Scheme = "http") -> None:
        if isinstance(endpoint, IPvAnySocketPair):
            self.endpoint = endpoint
        else:
            self.endpoint = IPvAnySocketPair.validate(endpoint)
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

    def _http_method(
        self, endpoint: str = "", http_method: str = "get", data: Optional[dict] = None
    ) -> Tuple[requests.Response, Union[Dict, List]]:
        endpoint = endpoint.lstrip("/")
        url = f"{self.scheme}://{self.endpoint}/{endpoint}"
        method = getattr(self.session, http_method)
        try:
            if data is not None:
                if http_method == "post":
                    resp = method(url, json=data)
                else:
                    resp = method(url, data=data)
            else:
                resp = method(url)
        except Exception:
            self.logger.debug(f"{http_method.upper()}: [{url}]: <FAIL>")
            raise
        try:
            _json = resp.json()
        except requests.exceptions.JSONDecodeError:
            _json = {}
        self.logger.debug(
            f"{http_method.upper()}: [{url}]" + f" (data={data})" if data is not None else "" + f": {_json}"
        )
        return (resp, _json)

    def _get(self, endpoint: str = "", data: Optional[dict] = None) -> Tuple[requests.Response, Union[Dict, List]]:
        return self._http_method(endpoint)

    def _post(self, endpoint: str = "", data: Optional[dict] = None) -> Tuple[requests.Response, Union[Dict, List]]:
        return self._http_method(endpoint, http_method="post", data=data)

    def is_healthy(self) -> bool:
        try:
            _ = self._get("")
            self.logger.debug("Healthy client")
            return True
        except Exception:  # noqa: E722
            self.logger.debug("Unhealthy client")
            return False

    def status(self) -> Any:
        return self._get("/status")[1]

    def progress(self) -> Any:
        try:
            return self._get("/progress")[1]
        except requests.exceptions.JSONDecodeError:
            self.logger.debug("Returning empty response")
            return {}

    def progress_step(self) -> Any:
        return self._get("/progress-step")[1]

    def create_endpoint(self, endpoint: Union[QorEndpoint, Dict[Any, Any]]) -> Any:
        if isinstance(endpoint, QorEndpoint):
            data = endpoint.json  # type: ignore
        else:
            data = QorEndpoint(**endpoint).json
        resp, json = self._post("/endpoints", data=data)
        if resp.status_code == 201:
            return json
        raise QorApiError(resp.text)

    def reset(self) -> Any:
        _ = self._get("/progress-step", data={"reset": "true"})
        _ = self._get("/progress", data={"clear": "true"})
