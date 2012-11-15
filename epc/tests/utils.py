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


class BaseTestCase(unittest.TestCase):

    if not hasattr(unittest.TestCase, 'assertIsInstance'):
        def assertIsInstance(self, obj, cls, msg=None):
            self.assertTrue(isinstance(obj, cls), msg),


def skip(func):
    import functools
    from nose import SkipTest

    @functools.wraps(func)
    def wrapper(*args, **kwds):
        raise SkipTest
    return wrapper
