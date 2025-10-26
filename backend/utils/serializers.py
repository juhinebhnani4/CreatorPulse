"""
Response serialization utilities.

P2 #4: Standardize null vs undefined handling across API responses.
This module provides utilities to clean API responses by omitting None values,
reducing payload size and matching frontend expectations.
"""

from typing import Any, Dict, List, Union


def omit_none_values(obj: Any) -> Any:
    """
    Recursively remove None values from dictionaries and lists.

    This reduces payload size and matches frontend expectations where
    undefined (missing field) is preferred over null (explicit null).

    Args:
        obj: Object to clean (dict, list, or primitive)

    Returns:
        Cleaned object with None values removed

    Examples:
        >>> omit_none_values({'a': 1, 'b': None, 'c': 'test'})
        {'a': 1, 'c': 'test'}

        >>> omit_none_values([1, None, 3, None, 5])
        [1, 3, 5]

        >>> omit_none_values({'user': {'name': 'John', 'email': None}})
        {'user': {'name': 'John'}}
    """
    if isinstance(obj, dict):
        return {
            key: omit_none_values(value)
            for key, value in obj.items()
            if value is not None
        }
    elif isinstance(obj, list):
        return [
            omit_none_values(item)
            for item in obj
            if item is not None
        ]
    else:
        return obj


def serialize_api_response(data: Any, omit_nulls: bool = True) -> Any:
    """
    Serialize data for API response with optional null omission.

    P2 #4: Main serializer for all API endpoints.

    Args:
        data: Data to serialize (typically dict from Pydantic model)
        omit_nulls: Whether to omit None values (default: True)

    Returns:
        Serialized data ready for JSON response

    Usage:
        # In API endpoint:
        from backend.utils.serializers import serialize_api_response

        @router.get("/items")
        async def get_items():
            items = fetch_items()
            return serialize_api_response({
                'items': items,
                'count': len(items)
            })
    """
    if omit_nulls:
        return omit_none_values(data)
    return data


def serialize_content_item(item_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Specialized serializer for ContentItem responses.

    Handles ContentItem-specific serialization:
    - Omits None values
    - Ensures ISO format for datetimes
    - Preserves important fields even if None (e.g., score can be 0 or None)

    Args:
        item_dict: ContentItem as dictionary

    Returns:
        Serialized ContentItem dict
    """
    # Fields that should be preserved even if None (semantic meaning)
    preserve_none_fields = {'score', 'comments_count', 'shares_count', 'views_count'}

    result = {}
    for key, value in item_dict.items():
        # Skip None values unless they're semantically important
        if value is None and key not in preserve_none_fields:
            continue

        # Include all non-None values and semantically important None values
        result[key] = value

    return result


def serialize_content_list(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Serialize a list of ContentItems.

    Args:
        items: List of ContentItem dicts

    Returns:
        List of serialized ContentItems
    """
    return [serialize_content_item(item) for item in items]


# Convenience function for Pydantic model serialization
def serialize_pydantic_model(model: Any, omit_nulls: bool = True) -> Dict[str, Any]:
    """
    Serialize a Pydantic model to dict with optional null omission.

    Args:
        model: Pydantic model instance
        omit_nulls: Whether to omit None values

    Returns:
        Serialized dict

    Usage:
        from pydantic import BaseModel

        class User(BaseModel):
            name: str
            email: Optional[str] = None

        user = User(name="John")
        result = serialize_pydantic_model(user)
        # Returns: {'name': 'John'} (email omitted)
    """
    data = model.dict() if hasattr(model, 'dict') else model.model_dump()
    return serialize_api_response(data, omit_nulls=omit_nulls)
