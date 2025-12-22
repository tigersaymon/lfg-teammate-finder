from typing import Any

from django import template

register = template.Library()


@register.filter
def get_item(dictionary: dict, key: Any) -> Any:
    return dictionary.get(key)
