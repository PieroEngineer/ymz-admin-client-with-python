"""Minimal authenticated HTTP client for the Yummizi HTTP API (API Gateway v2).

Uses only the standard library, so boto3 stays the only third-party
dependency in this project.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping

from config import ApiConfig


class ApiError(RuntimeError):
    """Raised when the API returns a non-2xx response or an unreadable body."""

    def __init__(self, status: int, body: str, *, url: str) -> None:
        super().__init__(f"HTTP {status} calling {url}: {body}")
        self.status = status
        self.body = body
        self.url = url


@dataclass(frozen=True, slots=True)
class ApiResponse:
    status: int
    data: Any  # already json.loads()-ed body (dict, list, or None)


class ApiClient:
    """Calls the Yummizi admin API, attaching a bearer token to every request."""

    def __init__(self, config: ApiConfig, *, bearer_token: str) -> None:
        self._base_url = config.base_url
        self._bearer_token = bearer_token

    def with_token(self, bearer_token: str) -> "ApiClient":
        """Return a new client using a refreshed token, same base URL."""
        return ApiClient(ApiConfig(base_url=self._base_url), bearer_token=bearer_token)

    def get(self, path: str, *, query: Mapping[str, str] | None = None) -> ApiResponse:
        url = f"{self._base_url}/{path.lstrip('/')}"
        if query:
            # Drop keys with None values instead of sending "nextToken=None".
            clean_query = {k: v for k, v in query.items() if v is not None}
            if clean_query:
                url = f"{url}?{urllib.parse.urlencode(clean_query)}"

        request = urllib.request.Request(
            url,
            method="GET",
            headers={
                "Authorization": f"Bearer {self._bearer_token}",
                "Accept": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(request) as response:
                raw_body = response.read().decode("utf-8")
                status = response.status
        except urllib.error.HTTPError as err:
            raw_body = err.read().decode("utf-8")
            raise ApiError(err.code, raw_body, url=url) from err
        except urllib.error.URLError as err:
            raise ApiError(0, str(err.reason), url=url) from err

        try:
            data = json.loads(raw_body) if raw_body else None
        except json.JSONDecodeError as err:
            raise ApiError(status, f"Non-JSON body: {raw_body[:200]}", url=url) from err

        return ApiResponse(status=status, data=data)
