"""Configuration variables made easy!"""
import itertools as _itertools

from .api import load, hold, _held_vars


__all__ = ["load", "hold"]


def __getattr__(name):
    """Module level __getattr__ dunder method.

    Works only for python 3.7 and above (see PEP 562 https://www.python.org/dev/peps/pep-0562/).
    Try to return the value for the key 'name' in _held_vars' AttrFrozenDict.

    Raises
    ------
    AttributeError
        if the end of the function is hit
    """
    for v in _held_vars:
        try:
            return v[name]
        except KeyError:
            pass
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__():
    """Module level __dir__ dunder method.

    Works only for python 3.7 and above (see PEP 562 https://www.python.org/dev/peps/pep-0562/).
    """
    return __all__ + list(_itertools.chain.from_iterable(_held_vars))
