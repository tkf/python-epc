from ..client import EPCClient
from ..server import ThreadingEPCServer
from ..server import ReturnError
from ..utils import newthread
from .utils import BaseTestCase


class TestEPCPy2Py(BaseTestCase):

    def setUp(self):
        self.server = ThreadingEPCServer(('localhost', 0))
        self.server.daemon_threads = True
        self.server_thread = newthread(self, target=self.server.serve_forever)
        self.server_thread.start()

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

    def test_client_calls_server_echo(self):
        self.assertEqual(self.client.call_sync('echo', [55]), [55])

    def test_client_calls_server_bad_method(self):
        self.assertRaises(
            ReturnError, self.client.call_sync, 'bad_method', [55])
