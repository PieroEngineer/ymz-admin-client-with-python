"""Typed models for the API response payloads."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


class ModelParseError(RuntimeError):
    """Raised when an API response is missing required data or has a bad shape."""


def _require(data: Mapping[str, Any], key: str, *, context: str) -> Any:
    if key not in data or data[key] is None:
        raise ModelParseError(f"{context}: missing required field '{key}'")
    return data[key]


def _require_number(data: Mapping[str, Any], key: str, *, context: str) -> int | float:
    value = _require(data, key, context=context)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ModelParseError(f"{context}: '{key}' must be a number")
    return value


@dataclass(frozen=True, slots=True)
class FeedItem:
    id: str
    name: str
    logo_url: str
    section_type: str
    dishes_to_show_urls: list[str]
    latitude: float
    longitude: float
    phone_number_to_contact: str

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> FeedItem:
        context = "FeedItem"
        dishes = _require(data, "dishesToShowUrls", context=context)
        if not isinstance(dishes, list) or not all(
            isinstance(url, str) for url in dishes
        ):
            raise ModelParseError(
                f"{context}: 'dishesToShowUrls' must be a list of strings"
            )

        return cls(
            id=str(_require(data, "id", context=context)),
            name=str(_require(data, "name", context=context)),
            logo_url=str(_require(data, "logoUrl", context=context)),
            section_type=str(_require(data, "sectionType", context=context)),
            dishes_to_show_urls=dishes,
            latitude=float(_require_number(data, "latitude", context=context)),
            longitude=float(_require_number(data, "longitude", context=context)),
            phone_number_to_contact=str(
                _require(data, "phoneNumberToContact", context=context)
            ),
        )


@dataclass(frozen=True, slots=True)
class ActiveRequests:
    request_id: str
    restaurant_id: str
    state: str
    user_id: str
    on_queued_timestamp: int | float
    # Keep the backend's current field name despite its known typing error.
    arrival_time_in_minutes: int | float

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> ActiveRequests:
        context = "ActiveRequests"
        return cls(
            request_id=str(_require(data, "requestId", context=context)),
            restaurant_id=str(_require(data, "restaurantId", context=context)),
            state=str(_require(data, "state", context=context)),
            user_id=str(_require(data, "userId", context=context)),
            on_queued_timestamp=_require_number(
                data, "onQueuedTimestamp", context=context
            ),
            arrival_time_in_minutes=_require_number(
                data, "arrivalTimeInMinutes", context=context
            ),
        )