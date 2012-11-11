# -*- coding: utf-8 -*-

import io
import socket
import threading
import unittest

from sexpdata import Symbol, loads

from ..server import ThreadingEPCServer, encode_string, encode_object
from ..py3compat import PY3, utf8, Queue


class TestEPCServer(unittest.TestCase):

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

    def get_client_handler(self):
        return next(iter(self.server.clients))

    def test_echo(self):
        self.client.send(encode_string('(call 1 echo (55))'))
        result = self.client.recv(1024)
        self.assertEqual(encode_string('(return 1 (55))'), result)

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

    def test_call_client_method(self):
        called_with = Queue.Queue()
        callback = called_with.put
        self.test_echo()  # to start connection, client must send something
        handler = self.get_client_handler()
        handler.call('dummy', [55], callback)
        (call, uid, meth, args) = self.receive_message()
        self.assertEqual(call.value(), 'call')
        assert isinstance(uid, int)
        self.assertEqual(args, [55])
        self.client.send(encode_string('(return {0} 123)'.format(uid)))
        reply = called_with.get(True, 1)
        self.assertEqual(reply, 123)

    def test_call_client_methods_info(self):
        called_with = Queue.Queue()
        callback = called_with.put
        self.test_echo()  # to start connection, client must send something
        handler = self.get_client_handler()
        handler.methods(callback)
        (methods, uid) = self.receive_message()
        self.assertEqual(methods.value(), 'methods')
        self.client.send(encode_string(
            '(return {0} ((dummy () "")))'.format(uid)))
        reply = called_with.get(True, 1)
        self.assertEqual(len(reply), 1)
        self.assertEqual(len(reply[0]), 3)
        self.assertEqual(reply[0][0].value(), 'dummy')
        self.assertEqual(reply[0][1], [])
        self.assertEqual(reply[0][2], "")

    def test_print_port(self):
        if PY3:
            stream = io.StringIO()
        else:
            stream = io.BytesIO()
        self.server.print_port(stream)
        self.assertEqual(stream.getvalue(),
                         '{0}\n'.format(self.server.server_address[1]))

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
