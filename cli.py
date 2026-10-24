"""Terminal-only interactive client for the Yummizi admin API."""
from __future__ import annotations

import os
from pprint import pp
# import getpass

from admin_api import AdminService

from auth import AuthError, AuthTokens, CognitoAuthenticator
from config import ConfigError, Settings
from http_client import ApiClient, ApiError
from models import ModelParseError


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

def _track_all_restaurants(service: AdminService) -> None:
    try:
        feed_items = service.retrieve_all_restaurants()
    except (ApiError, ModelParseError) as err:
        print(f"Could not load restaurant feed: {err}")
        return
    # _print_restaurants(feed_items)
    pp(feed_items)


# def _track_restaurant_requests(service: AdminService) -> None:
#     restaurant_id = input("Restaurant ID: ").strip()
#     date_from = input("From (YYYY-MM-DD): ").strip()
#     date_to = input("To (YYYY-MM-DD): ").strip()   # TODO: Ask again if the date is earlier than the from
#     try:
#         requests = service.retrieve_restaurant_requests_for_a_period(
#             restaurant_id=restaurant_id, date_from=date_from, date_to=date_to
#         )
#     except (ApiError, ModelParseError) as err:
#         print(f"Could not load tracking data: {err}")
#         return
#     # _print_tracking(requests)
#     pp(requests)


def _track_requests(service: AdminService, restaurant_scoped: bool) -> None:
    restaurant_id = input("Restaurant ID: ").strip() if restaurant_scoped else None
    date_from = input("From (YYYY-MM-DD): ").strip()    # TODO: Edit it because the backend is in UTC
    date_to = input("To (YYYY-MM-DD): ").strip()
    try:
        if restaurant_id is None:
            requests = service.retrieve_requests_for_a_period(
                date_from=date_from, date_to=date_to
            )
        else:
            requests = service.retrieve_restaurant_requests_for_a_period(
                restaurant_id=restaurant_id, date_from=date_from, date_to=date_to
            )
    except (ApiError, ModelParseError) as err:
        print(f"Could not load tracking data: {err}")
        return
    pp(requests)


def _track_orders(service: AdminService, *, restaurant_scoped: bool) -> None:
    restaurant_id = input("Restaurant ID: ").strip() if restaurant_scoped else None
    date_from = input("From (YYYY-MM-DD): ").strip()    # TODO: Edit it because the backend is in UTC
    date_to = input("To (YYYY-MM-DD): ").strip()
    try:
        if restaurant_id is None:
            orders = service.retrieve_orders_for_a_period(date_from=date_from, date_to=date_to)
        else:
            orders = service.retrieve_restaurant_orders_for_a_period(
                restaurant_id=restaurant_id,
                date_from=date_from,
                date_to=date_to,
            )
    except (ApiError, ModelParseError) as err:
        print(f"Could not load orders: {err}")
        return
    pp(orders)


def run() -> None:
    try:
        settings = Settings.from_env()
    except ConfigError as err:
        print(f"Configuration error: {err}")
        return

    authenticator = CognitoAuthenticator(settings.cognito)
    tokens: AuthTokens | None = None

    tokens = _sign_in_flow(authenticator)
    # while tokens is None:
    #     choice = input("[1] Sign in  |  [2] Sign up  |  [3] Quit\n> ").strip()
    #     if choice == "1":
    #         tokens = _sign_in_flow(authenticator)
    #     elif choice == "2":
    #         _sign_up_flow(authenticator)
    #     elif choice == "3":
    #         return
    #     else:
    #         print("Invalid option.")

    # access_token is used here; see README.md for when to use id_token instead.
    api_client = ApiClient(settings.api, bearer_token=tokens.access_token)
    service = AdminService(api_client)

    while True:
        choice = input(
            "\n[1] Restaurant feed  [2] Restaurant tracking requests  "
            "[3] Tracking requests by date  [4] Orders by date  "
            "[5] Restaurant orders  [6] Quit\n> "
        ).strip()
        if choice == "1":
            _track_all_restaurants(service, restaurant_scoped=False)
        elif choice == "2":
            _track_all_restaurants(service, restaurant_scoped=True)
        elif choice == "3":
            _track_requests(service)
        elif choice == "4":
            _track_orders(service, restaurant_scoped=False)
        elif choice == "5":
            _track_orders(service, restaurant_scoped=True)
        elif choice == "6":
            return
        else:
            print("Invalid option.")
