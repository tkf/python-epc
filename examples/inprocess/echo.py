"""
Run in-process server/client.

This script is mainly for profiling.  To profile this script, run
it using the following command.::

    python -m cProfile -o echo.prof examples/inprocess/echo.py

To see the profiling resut, use::

    python -m pstats

However, what you can see in the profile is the profile of
the main thread.

To see the profile of all threads, use yappi_.
To use yappi, run the following snippet::

    import yappi
    yappi.start()
    echo_long_string(int(1e5), 1)
    yappi.stop()
    yappi.print_stats(limit=10, sort_type=yappi.SORTTYPE_TSUB)
    yappi.print_stats(limit=10, sort_type=yappi.SORTTYPE_TTOT)

.. _yappi: http://code.google.com/p/yappi/

"""


from epc.tests.test_py2py import ThreadingPy2Py


def echo_long_string(length, repeat):
    p2p = ThreadingPy2Py()
    p2p.setup_connection(log_traceback=True)

    @p2p.server.register_function
    def echo(x):
        return x

    try:
        for _ in range(repeat):
            p2p.client.call_sync('echo', ['a' * length])
    finally:
        p2p.teardown_connection()


def main(args=None):
    from argparse import ArgumentParser
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--length', default=int(1e5))
    parser.add_argument('--repeat', default=10)
    ns = parser.parse_args(args)
    echo_long_string(**vars(ns))


if __name__ == '__main__':
    main()
