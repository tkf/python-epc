from ..client import EPCClient
from ..server import ThreadingEPCServer
from ..server import ReturnError
from ..utils import newthread
from ..py3compat import Queue
from .utils import BaseTestCase


class TestEPCPy2Py(BaseTestCase):

    def setUp(self):
        ThreadingEPCServer.allow_reuse_address = True
        self.server = ThreadingEPCServer(('localhost', 0))
        self.server.daemon_threads = True
        self.server_thread = newthread(self, target=self.server.serve_forever)
        self.server_thread.start()

        self.client_queue = q = Queue.Queue()
        self.server.handle_client_connect = q.put

        self.client = EPCClient(self.server.server_address)

        @self.client.register_function
        @self.server.register_function
        def echo(*a):
            """Return argument unchanged."""
            return a

        @self.client.register_function
        @self.server.register_function
        def bad_method(*_):
            """This is a bad method.  Don't call!"""
            raise ValueError("This is a bad method!")

        @self.server.register_function
        def ping_server(x):
            return self.server.clients[0].call_sync('pong_client', [x])

        @self.client.register_function
        def pong_client(x):
            return self.client.call_sync('echo', [x])

        @self.client.register_function
        def ping_client(x):
            return self.client.call_sync('pong_server', [x])

        @self.server.register_function
        def pong_server(x):
            return self.server.clients[0].call_sync('echo', [x])

        @self.server.register_function
        def fib_server(x):
            if x < 2:
                return x
            i = self.server.clients[0].call_sync('fib_client', [x - 1])
            j = self.server.clients[0].call_sync('fib_client', [x - 2])
            return i + j

        @self.client.register_function
        def fib_client(x):
            if x < 2:
                return x
            i = self.client.call_sync('fib_server', [x - 1])
            j = self.client.call_sync('fib_server', [x - 2])
            return i + j

    def tearDown(self):
        self.client.close()
        self.server.shutdown()
        self.server.server_close()

    def wait_until_client_is_connected(self):
        if not self.client_ready:
            self.client_queue.get(timeout=1)
            self.client_ready = True

    client_ready = False

    def assert_call_return(self, call, method, args, reply):
        self.assertEqual(call(method, args, timeout=1), reply)

    def assert_client_return(self, method, args, reply):
        self.assert_call_return(self.client.call_sync, method, args, reply)

    def assert_server_return(self, method, args, reply):
        self.wait_until_client_is_connected()
        self.assert_call_return(self.server.clients[0].call_sync,
                                method, args, reply)

    def test_client_calls_server_echo(self):
        self.assert_client_return('echo', [55], [55])

    def test_client_calls_server_bad_method(self):
        self.assertRaises(
            ReturnError, self.client.call_sync, 'bad_method', [55])

    def test_server_calls_client_echo(self):
        self.assert_server_return('echo', [55], [55])

    def test_server_calls_client_bad_method(self):
        self.wait_until_client_is_connected()
        self.assertRaises(
            ReturnError, self.server.clients[0].call_sync, 'bad_method', [55])

    def test_client_ping_pong(self):
        self.assert_client_return('ping_server', [55], [55])

    def test_server_ping_pong(self):
        self.assert_server_return('ping_client', [55], [55])

    def test_client_close_should_not_fail_even_if_not_used(self):
        pass

    fibonacci = [0, 1, 1, 2, 3, 5, 8]

    def test_client_fib(self):
        for (i, f) in enumerate(self.fibonacci):
            self.assert_client_return('fib_server', [i], f)

    def test_server_fib(self):
        for (i, f) in enumerate(self.fibonacci):
            self.assert_server_return('fib_client', [i], f)
