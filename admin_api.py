"""High-level admin operations with typed parsing of raw API responses."""
from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import TypeVar

from http_client import ApiClient
from models import ActiveRequests, FeedItem, ModelParseError, Order

T = TypeVar("T")


def _parse_list_response(
    data: object,
    *,
    key: str,
    context: str,
    parse_item: Callable[[Mapping[str, object]], T],
) -> list[T]:
    if not isinstance(data, Mapping):
        raise ModelParseError(f"{context}: response must be an object")
    items = data.get(key)
    if not isinstance(items, list):
        raise ModelParseError(f"{context}: '{key}' must be a list")
    if not all(isinstance(item, Mapping) for item in items):
        raise ModelParseError(f"{context}: each item must be an object")
    return [parse_item(item) for item in items]


class AdminService:
    def __init__(self, api_client: ApiClient) -> None:
        self._api = api_client

    def retrieve_all_restaurants(self) -> list[FeedItem]: # TODO: Add pagination here if the feed grows beyond a single response.
        response = self._api.get("restaurants/feed", query={"userId": 'someUserId'})

        ##Save restaurants in Records
        
        if not isinstance(response.data, list):
            raise ModelParseError("Restaurant feed: response must be a list")
        if not all(isinstance(item, Mapping) for item in response.data):
            raise ModelParseError("Restaurant feed: each item must be an object")
        return [FeedItem.from_dict(item) for item in response.data]
        
    def retrieve_restaurant_requests_for_a_period(
        self,
        *,
        restaurant_id: str,
        date_from: str,
        date_to: str,
    ) -> list[ActiveRequests]:



        # Look for this restaurant in searching records

        # 
        
        path = f"tracking/{restaurant_id}/{date_from}/{date_to}/requests"
        response = self._api.get(path)
        return _parse_list_response(
            response.data,
            key="restaurantRequests",
            context="Tracking requests",
            parse_item=ActiveRequests.from_dict,
        )

    def retrieve_requests_for_a_period(
        self, *, date_from: str, date_to: str
    ) -> list[ActiveRequests]:
        path = f"tracking/{date_from}/{date_to}/requests"
        response = self._api.get(path)
        return _parse_list_response(
            response.data,
            key="restaurantRequests",
            context="Tracking requests",
            parse_item=ActiveRequests.from_dict,
        )

    def retrieve_orders_for_a_period(self, *, date_from: str, date_to: str) -> list[Order]:
        path = f"tracking/{date_from}/{date_to}/orders"
        response = self._api.get(path)
        return _parse_list_response(
            response.data,
            key="restaurantOrders",
            context="Orders",
            parse_item=Order.from_dict,
        )

    def retrieve_restaurant_orders_for_a_period(
        self, *, restaurant_id: str, date_from: str, date_to: str
    ) -> list[Order]:
        path = f"tracking/{restaurant_id}/{date_from}/{date_to}/orders"
        response = self._api.get(path)
        return _parse_list_response(
            response.data,
            key="restaurantOrders",
            context="Restaurant orders",
            parse_item=Order.from_dict,
        )
