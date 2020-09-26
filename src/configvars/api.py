"""API functions for loading variables in modules/scripts."""
from .storage import _load_vars, VarNotFound, SETTINGS


def load(name, vars_=None, settings=SETTINGS):
    """Load the variables associated with 'name'.

    Parameters
    ----------
    name: str
        the name associated with the file storing the variables
    vars_ (default None)
        setting this parameter to a value other than None (the default)
        will make this function return a class decorator
        if vars_ is:
            - None: return the variables as an _AttrFrozenDict object
            - True or "all": return a decorator which will set all the available
                variables as attributes of the decorated class
            - a list of variable names as strings: return a decorator which will set
                all the variables in the list as class attributes of the decorated class
    settings: mapping (default .storage.SETTINGS)
        a mapping containing the necessary settings (see .storage._SETTINGS),
        usually doesn't need to be set to a value other than the default

    Returns
    -------
    if vars_ is None
        the loaded variables as an _AttrFrozenDict object
    else
        the load decorator, which will set the appropriate variables as class
        attributes on the decorated class

    Raises
    ------
    .storage.VarNotFound
        if vars_ is a list of variable names and one of its items is not
        an available variable for the given 'name'
    """
    if vars_ is None:
        return _load_vars(name, settings=settings)

    def load_decorator(cls):
        loaded_vars_ = _load_vars(name, settings=settings)
        if vars_ in ("all", True):
            # cls.__dict__.update(loaded_vars_) ?
            for var in loaded_vars_:
                setattr(cls, var, loaded_vars_[var])
        else:
            for var in vars_:
                try:
                    setattr(cls, var, loaded_vars_[var])
                except KeyError:
                    raise VarNotFound(f"variable '{var}' was not "
                                      f"found in '{name}'") from None
        return cls

    return load_decorator


_held_vars = []  # NOTE: mutable type to prevent import-related problems


def hold(name, reset=False, settings=SETTINGS):
    """Store the variables for 'name' in _held_vars.

    _held_vars' items can be accessed via configvars.ITEM_NAME directly (see __init__.py's __getattr__).

    Parameters
    ----------
    name: str
        the name associated with the file storing the variables
    reset: bool (default False)
        wether or not to reset the list of variables held
    settings: mapping (default .storage.SETTINGS)
        a mapping containing the necessary settings (see .storage._SETTINGS),
        usually doesn't need to be set to a value other than the default
    """
    vars_ = _load_vars(name, settings=settings)
    if reset:
        _held_vars[:] = [vars_]
    else:
        _held_vars.insert(0, vars_)
