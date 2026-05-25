from typing import Any


def _fieldname(prefix: str, key: Any):
    return prefix + str(key).lower()


def key_getter(prefix: str):
    """Makes function like get_someting(key)"""

    def getter(obj, key: Any) -> Any:
        return getattr(obj, _fieldname(prefix, key))

    return getter


def key_setter(prefix: str):
    """Makes function like set_someting(key, value)"""

    def setter(obj, key: Any, val: Any):
        setattr(obj, _fieldname(prefix, key), val)

    return setter


def dict_getter(prefix: str, keys: tuple[Any, ...] | list[Any]):

    def getter(obj) -> dict:
        return {key: getattr(obj, _fieldname(prefix, key)) for key in keys}

    return getter
