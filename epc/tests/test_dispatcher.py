from ..core import EPCDispatcher
from .utils import BaseTestCase


class Dummy(object):
    pass


class TestEPCDispatcher(BaseTestCase):

    def setUp(self):
        self.dispatcher = EPCDispatcher()

    def test_register_module(self):
        import os
        self.dispatcher.register_instance(os)
        self.assertIs(self.dispatcher.get_method('chmod'), os.chmod)

    def test_register_module_with_dotted_names(self):
        import os
        self.dispatcher.register_instance(os, allow_dotted_names=True)
        self.assertIs(self.dispatcher.get_method('path.join'), os.path.join)

    def test_error_on_private_method_access(self):
        obj = Dummy()
        obj._private_method = lambda: None
        obj.sub = Dummy()
        obj.sub._private_attribute = Dummy()
        obj.sub._private_attribute.some_method = lambda: None
        self.dispatcher.register_instance(obj, allow_dotted_names=True)
        self.assertRaises(AttributeError, self.dispatcher.get_method,
                          '_private_method')
        self.assertRaises(AttributeError, self.dispatcher.get_method,
                          'obj.sub._private_attribute.some_method')

    def test_instance_get_method(self):
        always_me = lambda: None
        obj = Dummy()
        obj._get_method = lambda _: always_me
        self.dispatcher.register_instance(obj)
        self.assertIs(self.dispatcher.get_method('x'), always_me)
        self.assertIs(self.dispatcher.get_method('y'), always_me)
