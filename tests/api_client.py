"""Общий HTTP-клиент: base URL, заголовки, логирование запросов и ответов."""

import json
import logging
import time

import requests

logger = logging.getLogger("api")

MAX_LOGGED_BODY = 2000


class ApiClient:
    """Обёртка над requests.Session для одного стенда."""

    def __init__(self, base_url: str, identity: str | None = None, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        if identity:
            self.session.headers["X-Playground-Identity"] = identity

    def request(self, method: str, path: str = "", **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        if "json" in kwargs:
            logger.debug(
                "%s %s | request body: %s",
                method, url, json.dumps(kwargs["json"], ensure_ascii=False),
            )
        started = time.perf_counter()
        response = self.session.request(method, url, timeout=self.timeout, **kwargs)
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.info("%s %s -> %d (%.0f ms)", method, url, response.status_code, elapsed_ms)
        logger.debug("%s %s | response body: %s", method, url, response.text[:MAX_LOGGED_BODY])
        return response

    def get(self, path: str = "", **kwargs) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str = "", json=None, **kwargs) -> requests.Response:
        return self.request("POST", path, json=json, **kwargs)

    def patch(self, path: str = "", json=None, **kwargs) -> requests.Response:
        return self.request("PATCH", path, json=json, **kwargs)

    def set_bearer_token(self, token: str) -> None:
        self.session.headers["Authorization"] = f"Bearer {token}"

    def drop_bearer_token(self) -> None:
        self.session.headers.pop("Authorization", None)

    def graphql(self, query: str, variables: dict | None = None) -> requests.Response:
        payload = {"query": query}
        if variables is not None:
            payload["variables"] = variables
        return self.post(json=payload)
