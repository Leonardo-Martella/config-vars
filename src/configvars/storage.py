"""A collection of storage-related classes, functions and variables."""
from collections import abc
import json
import os
import types
from importlib import import_module  # to get the absolute path to the package


_SETTINGS = {
    # TODO: better way to get 'store' directory path ?
    "storage_dir": os.path.join(import_module(__package__).__spec__.origin.rstrip("__init__.py"), "store"),
    "file_name": "{name}.json",  # no forward slash here
}

SETTINGS = types.MappingProxyType(_SETTINGS)


class NameNotFound(Exception):
    """The given name did not match an existing file."""
    pass


class VarNotFound(Exception):
    """The requested variable was not found in the current name's variables."""
    pass


class FrozenError(Exception):
    """The attempted operation is not allowed on a frozen instance."""
    pass


def _frozen(msg=None):
    """Freeze a method.

    Assign to methods which are not allowed because the class is frozen.

    Parameters
    ----------
    msg: str or None (default None)
        a message to pass to the FrozenError exception constructor on raise

    Raises
    ------
    .storage.FrozenError
    """
    def frozen_method(*_, **__):
        raise FrozenError(msg) if msg is not None else FrozenError()
    return frozen_method


# TODO: enforce str type keys (case-sensitivity?) and json-saveable objects
# TODO: implement __contains__ ?
class _AttrFrozenDict:
    """A read-only dict.

    NOTES
    -----
    Supports obj.name and obj["name"] access (delete or assignment
    operations will raise a storage.FrozenError).
    Implements __iter__ and __eq__.
    The internal dict (self._data) is modifiable, but should
    not be modified externaly (obviously).

    Examples
    --------
    >>> d = {"PIN": 9574, "MAIL_PASSWORD": "password1234"}
    >>> fd = _AttrFrozenDict(d)
    >>> fd
    _AttrFrozenDict({'PIN': 9574, 'MAIL_PASSWORD': 'password1234'})
    >>> fd.PIN
    9574
    >>> fd.MAIL_PASSWORD, fd["MAIL_PASSWORD"]
    ('password1234', 'password1234')
    >>> fd == d
    True
    >>> d["PIN"] = 1234
    >>> fd  # no change since a new dictionary was built during initialization
    _AttrFrozenDict({'PIN': 9574, 'MAIL_PASSWORD': 'password1234'})
    >>> fd == d
    False
    >>> fd.MAIL_PASSWORD
    'password1234'
    >>> del fd["MAIL_PASSWORD"]
    Traceback (most recent call last):
        ...
    storage.FrozenError: cannot delete item
    >>> fd.MAIL_PASSWORD = "mypass"
    Traceback (most recent call last):
        ...
    storage.FrozenError: cannot set attribute
    """
    __setattr__ = _frozen("cannot set attribute")
    __setitem__ = _frozen("cannot set item")
    __delattr__ = _frozen("cannot delete attribute")
    __delitem__ = _frozen("cannot delete item")

    def __init__(self, *args, **kwargs):
        """Initialize self. Same signature as dict (see help(dict) for more info)."""
        # modify self.__dict__ directly to avoid calling __setattr__ (which is frozen)
        self.__dict__["_data"] = dict(*args, **kwargs)

    def __getitem__(self, name):
        """Get self._data item via subscript.

        Raises
        ------
        KeyError
            if 'name' is not a key of self._data
        """
        return self._data[name]

    def __getattr__(self, name):
        """Get self._data item via attribute access.

        Raises
        ------
        KeyError
            if 'name' is not a key of self._data
        """
        return self._data[name]

    def __eq__(self, other):
        """Return wether 'self' and 'other' can be considered equal.

        Parameters
        ----------
        other: dict or .storage._AttrFrozenDict
            the object to compare 'self' with

        Raises
        ------
        TypeError
            if 'other._data' raises an AttributeError, we raise a TypeError
            indicating that an object of type 'type(self)' cannot be
            compared to an object of type 'type(other)'
        """
        if isinstance(other, abc.MutableMapping):
            return self._data == other
        try:
            return self._data == other._data
        except AttributeError as e:
            raise TypeError(f"{type(self).__name__} object cannot be compared "
                            f"to object of type {type(other).__name__}") from e

    def __iter__(self):
        """Return a dict key iterator object."""
        return iter(self._data)

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self._data)})"


def _get_storage_location(name, settings):
    """Return the path to the file associated with 'name' as a string.

    Parameters
    ----------
    name: str
        the name associated with the file storing the variables
    settings: mapping
        a mapping containing the necessary settings
    """
    return os.path.join(settings["storage_dir"], settings["file_name"]).format(name=name)


def _store_vars(name, vars_, settings):
    """Store 'vars_' in the file for 'name'.

    Parameters
    ----------
    name: str
        the name associated with the file storing the variables
    vars_: dict
        a dictionary of json-encodable key/value pairs to store
    settings: mapping
        a mapping containing the necessary settings
    """
    store_loc = _get_storage_location(name, settings=settings)
    os.makedirs(settings["storage_dir"], exist_ok=True)
    with open(store_loc, "w") as f:  # NOTE: overwrites file
        json.dump(vars_, f)


def _load_vars(name, settings):
    """Return the variables for 'name'.

    Parameters
    ----------
    name: str
        the name associated with the file storing the variables
    settings: mapping
        a mapping containing the necessary settings

    Raises
    ------
    .storage.NameNotFound
        if the file associated wih 'name' was not found

    Returns
    -------
    vars_: .storage._AttrFrozenDict
        the retrieved variables as an _AttrFrozenDict instance
    """
    store_loc = _get_storage_location(name, settings=settings)
    try:
        with open(store_loc, "r") as f:
            return _AttrFrozenDict(json.load(f))
    except FileNotFoundError:
        raise NameNotFound(f"name '{name}' not found") from None
