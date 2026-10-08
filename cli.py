"""Terminal-only interactive client for the Yummizi admin API."""
from __future__ import annotations

import os
from pprint import pp
# import getpass

from admin_api import AdminService

from auth import AuthError, AuthTokens, CognitoAuthenticator
from config import ConfigError, Settings
from http_client import ApiClient, ApiError
from models import ActiveRequests, FeedItem, ModelParseError


def _prompt_credentials() -> tuple[str, str]:
    # email = input("Email: ").strip()
    # password = getpass.getpass("Password: ")
    email = os.environ.get("ADMIN_EMAIL")
    password = os.environ.get("ADMIN_PWD")

    return email, password


def _sign_up_flow(authenticator: CognitoAuthenticator) -> None:
    email, password = _prompt_credentials()
    # name = input("Name (optional): ").strip() or None
    try:
        authenticator.sign_up(email, password)#, name=name)
    except AuthError as err:
        print(f"Sign-up failed: {err}")
        return

    print("✅  Sign-up successful. Auto signing in starting...")

    authenticator.sign_in(email, password)
    # print("Sign-up submitted. Check your email for a confirmation code.")
    # code = input("Confirmation code: ").strip()
    # try:
    #     authenticator.confirm_sign_up(email, code)
    #     print("Account confirmed. You can sign in now.")
    # except AuthError as err:
    #     print(f"Confirmation failed: {err}")


def _sign_in_flow(authenticator: CognitoAuthenticator) -> AuthTokens | None:
    email, password = _prompt_credentials()
    try:
        return authenticator.sign_in(email, password)
    except AuthError as err:
        print(f"Sign-in failed: {err}")
        return None


def _print_restaurants(feed_items: list[FeedItem]) -> None:
    if not feed_items:
        print("No restaurants found.")
        return
    print(f"{'ID':<24} {'Name':<30} {'Section':<18} Phone")
    print("-" * 95)
    for item in feed_items:
        print(
            f"{item.id:<24} {item.name:<30} "
            f"{item.section_type:<18} {item.phone_number_to_contact}"
        )


def _print_tracking(requests: list[ActiveRequests]) -> None:
    if not requests:
        print("No requests in that range.")
        return
    print(f"{'Request ID':<30} {'State':<12} {'User ID':<30} Queued   Arrival (min)")
    print("-" * 105)
    for item in requests:
        print(
            f"{item.request_id:<30} {item.state:<12} {item.user_id:<30} "
            f"{item.on_queued_timestamp} {item.arrival_time_in_minutes}"
        )
    print(f"\n{len(requests)} request(s) shown.")


def _feed_menu(service: AdminService) -> None:
    try:
        feed_items = service.get_all_restaurants()
    except (ApiError, ModelParseError) as err:
        print(f"Could not load restaurant feed: {err}")
        return
    # _print_restaurants(feed_items)
    pp(feed_items)


def _tracking_menu(service: AdminService) -> None:
    restaurant_id = input("Restaurant ID: ").strip()
    date_from = input("From (YYYY-MM-DD): ").strip()
    date_to = input("To (YYYY-MM-DD): ").strip()   # TODO: Ask again if the date is earlier than the from
    try:
        requests = service.get_tracking_requests(
            restaurant_id=restaurant_id, date_from=date_from, date_to=date_to
        )
    except (ApiError, ModelParseError) as err:
        print(f"Could not load tracking data: {err}")
        return
    # _print_tracking(requests)
    pp(requests)


def run() -> None:
    try:
        settings = Settings.from_env()
    except ConfigError as err:
        print(f"Configuration error: {err}")
        return

    authenticator = CognitoAuthenticator(settings.cognito)
    tokens: AuthTokens | None = None

    while tokens is None:
        choice = input("[1] Sign in  |  [2] Sign up  |  [3] Quit\n> ").strip()
        if choice == "1":
            tokens = _sign_in_flow(authenticator)
        elif choice == "2":
            _sign_up_flow(authenticator)
        elif choice == "3":
            return
        else:
            print("Invalid option.")

    # access_token is used here; see README.md for when to use id_token instead.
    api_client = ApiClient(settings.api, bearer_token=tokens.access_token)
    service = AdminService(api_client)

    while True:
        choice = input(
            "\n[1] Restaurant feed  [2] Tracking requests  [3] Quit\n> "
        ).strip()
        if choice == "1":
            _feed_menu(service)
        elif choice == "2":
            _tracking_menu(service)
        elif choice == "3":
            return
        else:
            print("Invalid option.")
