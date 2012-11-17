import os
import sys

import unittest
from contextlib import contextmanager


@contextmanager
def mockedattr(object, name, replace):
    """
    Mock `object.name` attribute using `replace`.
    """
    original = getattr(object, name)
    try:
        setattr(object, name, replace)
        yield
    finally:
        setattr(object, name, original)


def logging_to_stdout(logger):
    # it assumes that 0-th hander is the only one stream handler...
    return mockedattr(logger.handlers[0], 'stream', sys.stdout)


class BaseTestCase(unittest.TestCase):

    TRAVIS = os.getenv('TRAVIS')

    if TRAVIS:
        timeout = 10
    else:
        timeout = 1

    if not hasattr(unittest.TestCase, 'assertIsInstance'):
        def assertIsInstance(self, obj, cls, msg=None):
            self.assertTrue(isinstance(obj, cls), msg),


def skip(reason):
    import functools
    from nose import SkipTest

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwds):
            raise SkipTest("Skipping {0} because: {1}"
                           .format(func.__name__, reason))
        return wrapper
    return decorator
