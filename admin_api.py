"""High-level admin operations with typed parsing of raw API responses."""
from __future__ import annotations

from typing import Mapping

from http_client import ApiClient
from models import ActiveRequests, FeedItem, ModelParseError


class AdminService:
    def __init__(self, api_client: ApiClient) -> None:
        self._api = api_client

    def get_restaurant_feed(self, user_id: str) -> list[FeedItem]:
        response = self._api.get("restaurants/feed", query={"userId": user_id})

        if not isinstance(response.data, list):
            raise ModelParseError("Restaurant feed: response must be a list")
        if not all(isinstance(item, Mapping) for item in response.data):
            raise ModelParseError("Restaurant feed: each item must be an object")
        return [FeedItem.from_dict(item) for item in response.data]

    def get_all_restaurants(self) -> list[FeedItem]:
        # Add pagination here if the feed grows beyond a single response.
        return self.get_restaurant_feed('someUserId')

    def get_tracking_requests(
        self,
        *,
        restaurant_id: str,
        date_from: str,
        date_to: str,
    ) -> list[ActiveRequests]:
        path = f"tracking/{restaurant_id}/{date_from}/{date_to}/requests"
        response = self._api.get(path)

        if not isinstance(response.data, Mapping):
            raise ModelParseError("Tracking requests: response must be an object")
        requests = response.data.get("restaurantRequests")
        if not isinstance(requests, list):
            raise ModelParseError(
                "Tracking requests: 'restaurantRequests' must be a list"
            )
        if not all(isinstance(item, Mapping) for item in requests):
            raise ModelParseError("Tracking requests: each item must be an object")
        
        return [ActiveRequests.from_dict(item) for item in requests]
