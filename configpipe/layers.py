import configparser
import json
import logging
import os
from collections import ChainMap
from typing import Hashable

# Goal: Enable simple and declarative Configuration loaded and overwritten from different sources.
# - configpipe.Layer() is a dict compatible class
# - using / you can layer these classes
# - they implement a __call__(key, cast=None, default=undefined)


__logger = logging.getLogger("configpipe.providers")


def _perform_cast(key: Hashable, value: str, cast=None):
    if cast is None:
        return value
    try:
        return cast(value)
    except (TypeError, ValueError):
        raise ValueError(f"Config '{key}' has value '{value}'. Not a valid {cast.__name__}.")


def _parse_yaml_file(raw: str | bytes | bytearray) -> dict:
    import yaml

    return yaml.safe_load(raw)


def _parse_toml_file(raw: str | bytes | bytearray) -> dict:
    import toml

    return toml.loads(raw)


def _parse_ini_file(path: str) -> dict[str, dict[str, str]]:
    parser = configparser.ConfigParser()
    parser.read(path)
    data = dict(parser._sections)
    for section in data:
        data[section] = dict(parser._defaults, **data[section])
        data[section].pop("__name__", None)
    return data


def _parse_env_file(path: str | os.PathLike) -> dict[str, str]:
    data = dict()
    with open(path, "r") as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            if key in data:
                __logger.warning(f"key '{key}' exists multiple times in {path}")
            data[key] = value.strip()
    return data


class Layer(ChainMap):
    """
    https://docs.python.org/3/library/collections.html#collections.ChainMap
    https://github.com/python/cpython/blob/4664a7cf689946f0c9854cadee7c6aa9c276a8cf/Lib/collections/__init__.py#L974
    """

    def __call__(self, key, *args, **kwargs):
        cast = kwargs.pop("cast", None)
        default_given = "default" in kwargs
        default = kwargs.pop("default", None)
        try:
            value = self[key]
            return _perform_cast(key, value, cast)
        except KeyError:
            pass
        if default_given:
            return _perform_cast(key, default, cast)
        raise KeyError(f"unknown key '{key}'")

    def __truediv__(self, other):
        if isinstance(other, Layer):
            return self.__class__(*self.maps, *other.maps)
        raise TypeError(f"unsupported operated for Layer / <other> of type '{other.__class__.__name__}'")

    @classmethod
    def from_env(cls):
        return cls(os.environ.copy())

    @classmethod
    def from_env_file(cls, path: str | os.PathLike = ".env"):
        return cls(_parse_env_file(path))

    @classmethod
    def from_ini_file(cls, path: str | os.PathLike):
        return cls(_parse_ini_file(path))

    @classmethod
    def from_yaml_file(cls, path: str | os.PathLike):
        with open(path, "r") as file:
            return cls.from_yaml(file.read())

    @classmethod
    def from_yaml(cls, raw: str | bytes | bytearray):
        try:
            return cls(_parse_yaml_file(raw))
        except ImportError:
            raise ImportError(
                f"cannot instantiate {cls.__name__} without pyyaml installed.\nSuggested-Fix: pip install configpipe[yaml]"
            )

    @classmethod
    def from_json_file(cls, path: str | os.PathLike):
        with open(path, "r") as file:
            return cls.from_json(file.read())

    @classmethod
    def from_json(cls, raw: str | bytes | bytearray):
        return cls(json.loads(raw))

    @classmethod
    def from_toml_file(cls, path: str | os.PathLike):
        with open(path, "r") as file:
            return cls.from_toml(file.read())

    @classmethod
    def from_toml(cls, raw: str | bytes | bytearray):
        try:
            return cls(_parse_toml_file(raw))
        except ImportError:
            raise ImportError(
                f"cannot instantiate {cls.__name__} without toml installed.\nSuggested-Fix: Upgrade to Python 3.11 or pip install configpipe[toml]"
            )

    @classmethod
    def from_aws_ssm(root_path="/", client=None):
        raise NotImplementedError("todo")
