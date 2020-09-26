"""File run when running the package as a script with 'python3 -m configvars'."""
from .storage import _store_vars, SETTINGS
from .__main__utils import get_vars_dict


def main():
    name = input("storage name: ")
    vars_dict = get_vars_dict()
    _store_vars(name, vars_dict, settings=SETTINGS)


if __name__ == "__main__":
    main()
