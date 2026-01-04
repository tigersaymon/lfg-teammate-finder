from typing import Any

from django import template

register = template.Library()


@register.filter
def get_item(dictionary: dict, key: Any) -> Any:
    """
    Template filter to retrieve a dictionary value by key.

    Usage in template: {{ my_dict|get_item:my_key }}
    Necessary because standard Django templates (dict.key)
    doesn't work well with dynamic keys.
    """
    return dictionary.get(key)
