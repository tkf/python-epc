# Copyright (C) 2012-  Takafumi Arakaki

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import sys
import functools

import unittest
from contextlib import contextmanager

from ..py3compat import Queue
from ..utils import newthread


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

    if not hasattr(unittest.TestCase, 'assertIs'):
        def assertIs(self, expr1, expr2, msg=None):
            self.assertTrue(expr1 is expr2, msg)

    if not hasattr(unittest.TestCase, 'assertIsInstance'):
        def assertIsInstance(self, obj, cls, msg=None):
            self.assertTrue(isinstance(obj, cls), msg),


def skip(reason):
    from nose import SkipTest

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwds):
            raise SkipTest("Skipping {0} because: {1}"
                           .format(func.__name__, reason))
        return wrapper
    return decorator


def post_mortem_in_thread(traceback):
    """
    `pdb.post_mortem` that can be used in a daemon thread.

    Put the following in the `except`-block::

        import sys
        from epc.tests.utils import post_mortem_in_thread
        exc_info = sys.exc_info()
        post_mortem_in_thread(exc_info[2])

    """
    import pdb
    blocker = Queue.Queue()
    thread = newthread(target=blocker.get)
    thread.daemon = False
    thread.start()
    pdb.post_mortem(traceback)
    blocker.put(None)
