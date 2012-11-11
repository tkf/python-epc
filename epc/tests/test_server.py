# -*- coding: utf-8 -*-

import io
import socket
import threading
import unittest

from sexpdata import Symbol, loads

from ..server import ThreadingEPCServer, encode_string, encode_object, \
    ReturnError, EPCError
from ..py3compat import PY3, utf8, Queue


class BaseEPCServerTestCase(unittest.TestCase):

    def setUp(self):
        # See: http://stackoverflow.com/questions/7720953
        self.server = ThreadingEPCServer(('localhost', 0))
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.allow_reuse_address = True
        self.client = socket.create_connection(self.server.server_address)
        self.server_thread.start()

        def echo(*a):
            """Return argument unchanged."""
            return a

        def bad_method(*_):
            """This is a bad method.  Don't call!"""
            raise self.error_to_throw
        self.error_to_throw = ValueError("This is a bad method!")

        self.server.register_function(echo)
        self.server.register_function(bad_method)

    def tearDown(self):
        self.client.close()
        self.server.shutdown()
        self.server.server_close()

    def receive_message(self):
        result = self.client.recv(1024)
        self.assertEqual(int(result[:6], 16), len(result[6:]))
        return loads(result[6:].decode())  # skip the length part

    def check_echo(self):
        self.client.send(encode_string('(call 1 echo (55))'))
        result = self.client.recv(1024)
        self.assertEqual(encode_string('(return 1 (55))'), result)


class TestEPCServerRequestHandling(BaseEPCServerTestCase):

    """
    Test that EPCServer handles request from client properly.
    """

    def test_echo(self):
        self.check_echo()

    def test_error_in_method(self):
        self.client.send(encode_string('(call 2 bad_method nil)'))
        result = self.client.recv(1024)
        expected = encode_object([
            Symbol('return-error'), 2, repr(self.error_to_throw)])
        self.assertEqual(result, expected)

    def test_no_such_method(self):
        self.client.send(encode_string('(call 3 no_such_method nil)'))
        reply = self.receive_message()
        self.assertEqual(reply[0], Symbol('epc-error'))
        self.assertEqual(reply[1], 3)
        assert 'No such method' in reply[2]

    def test_methods(self):
        self.client.send(encode_string('(methods 4)'))
        reply = self.receive_message()
        self.assertEqual(reply[0], Symbol('return'))
        self.assertEqual(reply[1], 4)
        method = dict((m[0].value(), m[1:]) for m in reply[2])
        self.assertEqual(set(method), set(['echo', 'bad_method']))

        actual_docs = dict(
            (n, doc) for (n, (_, doc)) in method.items())
        desired_docs = dict(
            (n, f.__doc__) for (n, f) in self.server.funcs.items())
        self.assertEqual(actual_docs, desired_docs)

    def test_unicode_message(self):
        s = "日本語能力!!ソﾊﾝｶｸ"
        encode = lambda x: encode_string(utf8(x))
        self.client.send(encode('(call 1 echo ("{0}"))'.format(s)))
        result = self.client.recv(1024)
        self.assertEqual(encode('(return 1 ("{0}"))'.format(s)), result)

    def test_invalid_sexp(self):
        self.client.send(encode_string('(((invalid sexp!'))
        reply = self.receive_message()
        self.assertEqual(reply[0].value(), Symbol('epc-error').value())
        self.assertEqual(reply[1], [])  # uid
        assert 'Not enough closing brackets.' in reply[2]

    def test_print_port(self):
        if PY3:
            stream = io.StringIO()
        else:
            stream = io.BytesIO()
        self.server.print_port(stream)
        self.assertEqual(stream.getvalue(),
                         '{0}\n'.format(self.server.server_address[1]))


class TestEPCServerCallClient(BaseEPCServerTestCase):

    def setUp(self):
        super(TestEPCServerCallClient, self).setUp()
        self.check_echo()  # to start connection, client must send something
        self.handler = next(iter(self.server.clients))

        self.callback_called_with = Queue.Queue()
        self.callback = self.callback_called_with.put

        self.errback_called_with = Queue.Queue()
        self.errback = self.errback_called_with.put

    def check_call_client_dummy_method(self):
        self.handler.call('dummy', [55], self.callback, self.errback)
        (call, uid, meth, args) = self.receive_message()
        assert isinstance(uid, int)
        self.assertEqual([call, uid, meth, args],
                         [Symbol('call'), uid, Symbol('dummy'), [55]])
        return uid

    def test_call_client_dummy_method(self):
        uid = self.check_call_client_dummy_method()
        self.client.send(encode_string('(return {0} 123)'.format(uid)))
        reply = self.callback_called_with.get(True, 1)
        self.assertEqual(reply, 123)

    def test_call_client_methods_info(self):
        self.handler.methods(self.callback)
        (methods, uid) = self.receive_message()
        self.assertEqual(methods.value(), 'methods')
        self.client.send(encode_string(
            '(return {0} ((dummy () "")))'.format(uid)))
        reply = self.callback_called_with.get(True, 1)
        self.assertEqual(reply, [[Symbol('dummy'), [], ""]])

    def check_call_client_error(self, ename, eclass, message=utf8("message")):
        uid = self.check_call_client_dummy_method()
        self.client.send(
            encode_string('({0} {1} "{2}")'.format(ename, uid, message)))
        reply = self.errback_called_with.get(True, 1)
        assert isinstance(reply, eclass)
        self.assertEqual(reply.args, (message,))

    def test_call_client_return_error(self):
        self.check_call_client_error('return-error', ReturnError)

    def test_call_client_epc_error(self):
        self.check_call_client_error('epc-error', EPCError)
