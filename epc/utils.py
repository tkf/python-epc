import logging
import functools


def func_call_as_str(name, *args, **kwds):
    """
    Return arguments and keyword arguments as formatted string

    >>> func_call_as_str('f', 1, 2, a=1)
    'f(1, 2, a=1)'

    """
    return '{0}({1})'.format(
        name,
        ', '.join(map('{0!r}'.format, args) +
                  map('{0[0]!s}={0[1]!r}'.format, sorted(kwds.iteritems()))))


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
