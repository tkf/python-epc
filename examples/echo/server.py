import logging

from epc.server import EPCServer


def echo_server(address='localhost', port=0, logfilename='python-epc.log'):
    server = EPCServer((address, port), log_traceback=True)
    server.logger.setLevel(logging.DEBUG)

    ch = logging.FileHandler(filename=logfilename, mode='w')
    ch.setLevel(logging.DEBUG)
    server.logger.addHandler(ch)

    def echo(*a):
        """Return argument unchanged."""
        return a
    server.register_function(echo)
    return server


if __name__ == '__main__':
    server = echo_server()
    server.print_port()  # needed for Emacs client

    server.serve_forever()
    server.logger.info('exit')
