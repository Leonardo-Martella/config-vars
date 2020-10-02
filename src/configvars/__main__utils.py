"""Functions used by __main__.py (can't run doctests on __main__.py)."""
import collections
import operator
import re
import sys


ReTypeMatch = collections.namedtuple("ReTypeMatch", "re_match type constructor", defaults=(None,))


def parse_key_value(s):
    """Parse an expression, returning a key (variable name), value pair.

    Examples
    --------
    >>> parse_key_value("PIN = 9858")
    ('PIN', 9858)
    >>> parse_key_value("NEGATIVE_INT = -9858")
    ('NEGATIVE_INT', -9858)
    >>> parse_key_value("SECRET='opiuasf'")
    ('SECRET', 'opiuasf')
    >>> parse_key_value("F = .98")
    ('F', 0.98)
    >>> parse_key_value("F = 0.98")
    ('F', 0.98)
    >>> parse_key_value("F2 = 5.")
    ('F2', 5.0)
    >>> parse_key_value("FLOAT = 40e8")
    ('FLOAT', 4000000000.0)
    >>> parse_key_value("FLOAT = 2E-5")
    ('FLOAT', 2e-05)
    >>> parse_key_value("FLOAT = -2E-5")
    ('FLOAT', -2e-05)
    """
    if not bool(re.fullmatch(r"[a-zA-Z_]\w* ?= ?.+", s)):
        raise SyntaxError("invalid syntax")

    # not None since the regex above matched
    key_match = re.match(r"[a-zA-Z_]\w*", s)
    value_match = re.search(r"= ?.+", s)

    value = value_match.group().lstrip("= ")
    re_type_matches = [
        ReTypeMatch(bool(re.fullmatch(r"[-+]?\d+", value)), int),
        ReTypeMatch(bool(re.fullmatch(r"""([-+]?\d+\.\d*)         # floats in 'x.y' or 'x.' notation
                                          |([-+]?\d*\.\d+)        # '.x'
                                          |([-+]?\d+[Ee][-+]?\d+) # 'xEy' or 'xey'""",
                                      value, flags=re.VERBOSE)), float),
        ReTypeMatch(bool(re.fullmatch("[\"'].*[\"']", value, flags=re.DOTALL)),
                    str, operator.itemgetter(slice(1, -1, None)))  # constructor to get rid of extra quotes
    ]

    matches = list(filter(operator.attrgetter("re_match"), re_type_matches))  # should only be one item

    if len(matches) == 0:
        raise TypeError("invalid type used. allowed types: "
                        + ', '.join(list(map(lambda x: x.type.__name__, re_type_matches))))
    elif len(matches) > 1:
        raise Exception("regexes match more than one type")

    match = matches[0]
    if match.constructor is not None:
        return key_match.group(), match.constructor(value)
    return key_match.group(), match.type(value)


def get_vars_dict():
    """Ask the user for the variables to store."""
    vars_dict = {}
    msg = "Enter the variables you want to store. An empty string will save the variables and exit."
    sys.stdout.write(msg + "\n")
    while True:
        src = input(">>> ")
        if src == "":
            break
        try:
            key, value = parse_key_value(src)
        except Exception as e:
            sys.stdout.write(e + "\n")
        else:
            vars_dict[key] = value
            msg = f"key: {key} ({type(key).__name__}), value: {value} ({type(value).__name__})"
            sys.stdout.write(msg + "\n")
    return vars_dict
