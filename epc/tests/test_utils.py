from ..utils import ThreadedIterator

from .utils import BaseTestCase


class TestThreadedIterator(BaseTestCase):

    def check_identity(self, iterable):
        lst = list(iterable)
        self.assertEqual(list(ThreadedIterator(lst)), lst)

    def test_empty(self):
        self.check_identity([])

    def test_range_1(self):
        self.check_identity(range(1))

    def test_range_7(self):
        self.check_identity(range(7))
