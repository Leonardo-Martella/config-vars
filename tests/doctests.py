import doctest

from configvars import __main__utils, storage

doctest.testmod(__main__utils)
doctest.testmod(storage)
