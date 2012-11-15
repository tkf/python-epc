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

    def tearDown(self):
        self.client.close()
        self.server.shutdown()
        self.server.server_close()

    def wait_until_client_is_connected(self):
        self.client_queue.get(timeout=1)

    def test_client_calls_server_echo(self):
        self.assertEqual(self.client.call_sync('echo', [55]), [55])

    def test_client_calls_server_bad_method(self):
        self.assertRaises(
            ReturnError, self.client.call_sync, 'bad_method', [55])

    def test_server_calls_client_echo(self):
        self.wait_until_client_is_connected()
        self.assertEqual(self.server.clients[0].call_sync('echo', [55]), [55])

    def test_server_calls_client_bad_method(self):
        self.wait_until_client_is_connected()
        self.assertRaises(
            ReturnError, self.server.clients[0].call_sync, 'bad_method', [55])
