"""
FIXME: replace with key_getter and key_setter
"""

from typing import Any


class dictproxy(dict):
    __obj: Any
    __prefix: str
    __keys: tuple

    def __fieldname(self, key):
        assert key in self.__keys
        return f"{self.__prefix}{str(key).lower()}"

    def __setitem__(self, key, val):
        super().__setitem__(key, val)
        setattr(self.__obj, self.__fieldname(key), val)

    def __new__(cls, obj, prefix, keys):
        inst = super().__new__(cls)
        inst.__obj = obj
        inst.__prefix = prefix
        inst.__keys = keys
        return inst

    def __init__(self, *args):
        super().__init__({k: getattr(self.__obj, self.__fieldname(k)) for k in self.__keys})


class dictprop:
    def __init__(self, prefix, keys):
        self.prefix = prefix
        self.keys = keys

    def __get__(self, obj, cls):
        return dictproxy(obj, self.prefix, self.keys)
