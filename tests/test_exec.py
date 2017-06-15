import unittest

utc_timestamp = __import__('mfado.exec', globals(), locals(), ['utc_timestamp']).utc_timestamp


class TestExec(unittest.TestCase):
    def test_utc_timestamp(self):
        self.assertEqual(utc_timestamp('2017-06-15T05:47:44Z'), 1497505664)
        self.assertEqual(utc_timestamp(1497505664), 1497505664)
