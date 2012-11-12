import logging
import itertools
import functools
import threading

from .py3compat import Queue


def func_call_as_str(name, *args, **kwds):
    """
    Return arguments and keyword arguments as formatted string

    >>> func_call_as_str('f', 1, 2, a=1)
    'f(1, 2, a=1)'

    """
    return '{0}({1})'.format(
        name,
        ', '.join(itertools.chain(
            map('{0!r}'.format, args),
            map('{0[0]!s}={0[1]!r}'.format, sorted(kwds.items())))))


def autolog(level):
    if isinstance(level, str):
        level = getattr(logging, level.upper())

    def wrapper(method):
        @functools.wraps(method)
        def new_method(self, *args, **kwds):
            funcname = ".".join([self.__class__.__name__, method.__name__])
            self.logger.log(level, "(AutoLog) Called: %s",
                            func_call_as_str(funcname, *args, **kwds))
            ret = method(self, *args, **kwds)
            self.logger.log(level, "(AutoLog) Returns: %s(...) = %r",
                            funcname, ret)
            return ret
        return new_method
    return wrapper


class ThreadedIterator(object):

    def __init__(self, iterable):
        self._original_iterable = iterable
        self.queue = Queue.Queue()
        self.thread = threading.Thread(target=self._target)
        self.thread.daemon = True
        self.thread.start()

    def _target(self):
        for result in self._original_iterable:
            self.queue.put(result)

    def __next__(self):
        return self.queue.get()
    next = __next__  # for PY2
