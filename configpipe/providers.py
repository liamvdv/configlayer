import os
import json
from abc import abstractmethod, ABC

from typing import List, Hashable
import logging

# https://docs.python.org/3/library/collections.html#collections.ChainMap 
# kinda what we want...
# for readonly: https://code.activestate.com/recipes/305268/


# implemented dict() wrong: uses __iter__ not __dict__ (that's used for introspection)
""" E. g.
def __iter__(self):
    for key in self.__dict__:
        yield key, getattr(self, key)
"""


__logger = logging.getLogger("configpipe.providers")

def _perform_cast(key: Hashable, value: str, cast=None):
    if cast is None:
        return value
    try:
        return cast(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"Config '{key}' has value '{value}'. Not a valid {cast.__name__}."
        )

class LayeredProvider(object):
    """PipeProvider keeps the chained objects on the same level and interates through."""

    def __init__(self, *providers):
        self.providers: List['BaseProvider'] = providers or []
    
    def __call__(self, key: Hashable, *args, **kwargs):
        cast = kwargs.pop("cast", None)
        default_given = "default" in kwargs
        default = kwargs.pop("default", None)
        for provider in self.providers:
            try:
                value = provider(key, *args, **kwargs)
                return _perform_cast(key, value, cast)
            except KeyError:
                pass
        if default_given:
            return _perform_cast(key, default, cast)
        raise KeyError(f"unknown key '{key}'")
    
    def __or__(self, other):
        if isinstance(other, BaseProvider):
            return LayeredProvider(*self.providers, other)
        if isinstance(other, LayeredProvider):
            return LayeredProvider(*self.providers, *other.providers)
        raise ValueError(f"unsupported type {type(other)}")

    def __dict__(self):
        merged = dict()
        for data in reversed(self.providers):
            merged.update(data)
        return merged

    def __repr__(self):
        inner_layers = f"({'->'.join(list(map(repr, self.providers)))})" 
        if self.__class__ is BaseProvider:
            return "Union" + inner_layers
        return self.__class__.__name__ + inner_layers
    

class BaseProvider(ABC):
    def __call__(self, key: str, *args, **kwargs):
        cast = kwargs.pop("cast", None)
        default_given = "default" in kwargs
        default = kwargs.pop("default", None)
        try:
            value = self.get(key, *args, **kwargs)
            return _perform_cast(key, value, cast)
        except KeyError as e:
            if default_given:
                return _perform_cast(key, default, cast)
            raise e

    def __or__(self, other):
        if isinstance(other, BaseProvider):
            return LayeredProvider(self, other)
        if isinstance(other, LayeredProvider):
            return LayeredProvider(self, *other.providers)
        raise ValueError(f"unsupported type {type(other)}")
    
    def __repr__(self):
        return self.__class__.__name__
    
    @abstractmethod
    def get(self, key: Hashable, *args, **kwargs):
        ...

    @abstractmethod
    def __dict__(self) -> dict:
        ...
    

class Dict(BaseProvider):
    def __init__(self, data: dict):
        super().__init__()
        self._data = data 

    def get(self, key: Hashable, *args, **kwargs):
        return self._data[key]
    
class Env(BaseProvider):
    def __init__(self):
        super().__init__()

    def get(self, key: str, *args, **kwargs):
        return os.environ[key]
    
class JsonFile(BaseProvider):
    def __init__(self, path: str|os.PathLike):
        super().__init__()
        if isinstance(path, os.PathLike):
            path = os.__fspath__()
        if not isinstance(path, str):
            raise ValueError("path must be str or pathlike")
        with open(path, "rb") as f:
            self._data = json.load(f)
        if not isinstance(self._data, dict):
            raise ValueError(f"{self.__class__.__name__} data must result in a top level json object, not {type(self._data).__name__}")
        
    def get(self, key: str, *args, **kwargs):
        return self._data[key]
    
    def __dict__(self):
        return self._data
    
class YamlFile(BaseProvider):
    def __init__(self, path: str|os.PathLike):
        super().__init__()
        try: 
            import yaml
        except ImportError:
            raise TypeError(f"cannot instantiate {self.__class__.__name__} without pyyaml installed.\nSuggested-Fix: pip install configpipe[yaml]")
        if isinstance(path, os.PathLike):
            path = os.__fspath__()
        if not isinstance(path, str):
            raise ValueError("path must be str or pathlike")
        with open(path, "rb") as f:
            self._data = yaml.load(f)
    
    def get(self, key: str, *args, **kwargs):
        return self._data[key]
    
    def __dict__(self):
        return self._data

class EnvFile(BaseProvider):
    def __init__(self, path: str|os.PathLike):
        super().__init__()
        self._data = self._parse_file(path)
    
    def _parse_file(self, path: str|os.PathLike): 
        data = dict()
        with open(path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith('#') or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                if key in data:
                    __logger.warning(f"{self.__class__.__name__}: key '{key}' exists multiple times in {path}")
                data[key] = value.strip()
        return data

    def get(self, key: str, *args, **kwargs):
        return self._data[key]
    
    def __dict__(self):
        return self._data