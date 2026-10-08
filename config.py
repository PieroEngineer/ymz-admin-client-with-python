"""Configuration for the Yummizi admin CLI client.

Connection details come from environment variables so the same code can
target dev/staging/prod without any code changes:

    YUMMIZI_USER_POOL_ID      Cognito user pool ID
    YUMMIZI_APP_CLIENT_ID     Cognito app client ID
    YUMMIZI_APP_CLIENT_SECRET Cognito app client secret (optional)
    YUMMIZI_REGION            AWS region of the user pool, e.g. "us-east-1"
    YUMMIZI_API_URL           Base URL of the HTTP API, e.g.
                              "https://abc123.execute-api.us-east-1.amazonaws.com"
"""
from __future__ import annotations

import os
from dataclasses import dataclass


class ConfigError(RuntimeError):
    """Raised when required configuration is missing."""


@dataclass(frozen=True, slots=True)
class CognitoConfig:
    user_pool_id: str
    app_client_id: str
    region: str
    app_client_secret: str | None = None


@dataclass(frozen=True, slots=True)
class ApiConfig:
    base_url: str


@dataclass(frozen=True, slots=True)
class Settings:
    cognito: CognitoConfig
    api: ApiConfig

    @classmethod
    def from_env(cls) -> "Settings":
        try:
            user_pool_id = os.environ["YUMMIZI_USER_POOL_ID"]
            app_client_id = os.environ["YUMMIZI_APP_CLIENT_ID"]
            region = os.environ["YUMMIZI_REGION"]
            api_base_url = os.environ["YUMMIZI_API_URL"]
        except KeyError as missing:
            raise ConfigError(
                f"Missing required environment variable: {missing.args[0]}"
            ) from missing

        app_client_secret = os.environ.get("YUMMIZI_APP_CLIENT_SECRET") or None

        return cls(
            cognito=CognitoConfig(
                user_pool_id=user_pool_id,
                app_client_id=app_client_id,
                region=region,
                app_client_secret=app_client_secret,
            ),
            api=ApiConfig(base_url=api_base_url.rstrip("/")),
        )
