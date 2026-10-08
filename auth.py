"""Cognito authentication: sign-up and sign-in for the admin CLI.

Uses the USER_PASSWORD_AUTH flow, which must be enabled on the app
client (ExplicitAuthFlows must include "ALLOW_USER_PASSWORD_AUTH" and,
for token refresh, "ALLOW_REFRESH_TOKEN_AUTH").

If the app client has a secret, every call must include a SECRET_HASH
(HMAC-SHA256 of username + client id, keyed with the client secret);
that is computed automatically below whenever a secret is configured.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
from dataclasses import dataclass
import time

import boto3
from pycognito import Cognito
# from botocore.config import Config
from botocore.exceptions import ClientError

from config import CognitoConfig


class AuthError(RuntimeError):
    """Raised for any Cognito sign-up/sign-in failure, with a readable message."""


@dataclass(frozen=True, slots=True)
class AuthTokens:
    id_token: str
    access_token: str
    refresh_token: str | None
    expires_in: int
    token_type: str

class CognitoAuthenticator:
    """Thin wrapper around the boto3 cognito-idp client for one app client."""

    def __init__(self, config: CognitoConfig) -> None:
        self._config = config
        self._client = boto3.client("cognito-idp", region_name=config.region)

    def _secret_hash(self, username: str) -> str | None:
        secret = self._config.app_client_secret
        if secret is None:
            return None
        message = (username + self._config.app_client_id).encode("utf-8")
        digest = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).digest()
        return base64.b64encode(digest).decode("utf-8")

    def sign_up(self, email: str, password: str, *, name: str | None = None) -> None:
        attributes = [{"Name": "email", "Value": email}]
        if name:
            attributes.append({"Name": "name", "Value": name})

        kwargs: dict[str, object] = {
            "ClientId": self._config.app_client_id,
            "Username": email,
            "Password": password,
            "UserAttributes": attributes,
        }
        secret_hash = self._secret_hash(email)
        if secret_hash:
            kwargs["SecretHash"] = secret_hash

        try:
            self._client.sign_up(**kwargs)
        except ClientError as err:
            raise AuthError(_readable(err)) from err

    def confirm_sign_up(self, email: str, confirmation_code: str) -> None:
        kwargs: dict[str, object] = {
            "ClientId": self._config.app_client_id,
            "Username": email,
            "ConfirmationCode": confirmation_code,
        }
        secret_hash = self._secret_hash(email)
        if secret_hash:
            kwargs["SecretHash"] = secret_hash

        try:
            self._client.confirm_sign_up(**kwargs)
        except ClientError as err:
            raise AuthError(_readable(err)) from err

    def sign_in(self, email: str, password: str) -> AuthTokens:
        try:
            print("🔑  Starting signing in...")
            
            # Initialize the pycognito object
            cog = Cognito(
                user_pool_id=self._config.user_pool_id,
                client_id=self._config.app_client_id,
                # client_secret=self._config.app_client_secret, # Pass if you have a client secret
                username=email,
                # botocore_config=Config(
                #     connect_timeout=5,
                #     read_timeout=15,
                #     retries={"total_max_attempts": 1},
                # ),
            )
            
            print("🔑  Signing in...")

            
            start_time = time.perf_counter()
            # This handles the ALLOW_USER_SRP_AUTH flow and SRP_A math automatically
            cog.authenticate(password=password)
            end_time = time.perf_counter()

            print(f"✅  Sign-in successful. Time taken: {end_time - start_time:.2f} seconds.")
            
            return AuthTokens(
                id_token=cog.id_token,
                access_token=cog.access_token,
                refresh_token=cog.refresh_token,
                expires_in=3600, # Cognito standard tokens expire in 1 hour (3600s)
                token_type="Bearer",
            )
        except Exception as err:
            raise AuthError(str(err)) from err

    def refresh(
        self, refresh_token: str, *, username_for_secret_hash: str | None = None
    ) -> AuthTokens:
        auth_parameters = {"REFRESH_TOKEN": refresh_token}
        if username_for_secret_hash:
            secret_hash = self._secret_hash(username_for_secret_hash)
            if secret_hash:
                auth_parameters["SECRET_HASH"] = secret_hash

        try:
            response = self._client.initiate_auth(
                ClientId=self._config.app_client_id,
                AuthFlow="REFRESH_TOKEN_AUTH",
                AuthParameters=auth_parameters,
            )
        except ClientError as err:
            raise AuthError(_readable(err)) from err

        result = response["AuthenticationResult"]
        return AuthTokens(
            id_token=result["IdToken"],
            access_token=result["AccessToken"],
            refresh_token=result.get("RefreshToken", refresh_token),
            expires_in=result["ExpiresIn"],
            token_type=result["TokenType"],
        )


def _readable(err: ClientError) -> str:
    error = err.response.get("Error", {})
    code = error.get("Code", "UnknownError")
    message = error.get("Message", str(err))
    return f"{code}: {message}"



    # def sign_in(self, email: str, password: str) -> AuthTokens:
    #     auth_parameters = {"USERNAME": email, "PASSWORD": password}
    #     secret_hash = self._secret_hash(email)
    #     if secret_hash:
    #         auth_parameters["SECRET_HASH"] = secret_hash

    #     try:
    #         response = self._client.initiate_auth(
    #             ClientId=self._config.app_client_id,
    #             AuthFlow="USER_SRP_AUTH",
    #             AuthParameters=auth_parameters,
    #         )
    #     except ClientError as err:
    #         raise AuthError(_readable(err)) from err

    #     if "ChallengeName" in response:
    #         raise AuthError(
    #             f"Sign-in requires an unhandled challenge: {response['ChallengeName']} "
    #             "(e.g. a first-login NEW_PASSWORD_REQUIRED reset). Handle this challenge "
    #             "before this CLI can sign the user in."
    #         )

    #     result = response["AuthenticationResult"]
    #     return AuthTokens(
    #         id_token=result["IdToken"],
    #         access_token=result["AccessToken"],
    #         refresh_token=result.get("RefreshToken"),
    #         expires_in=result["ExpiresIn"],
    #         token_type=result["TokenType"],
    #     )