import unittest

from mfado.authentication.aws import AWSAuthentication


class TestAWS(unittest.TestCase):
    def test_forwarded_arguments(self):
        args = AWSAuthentication()._forwarded_arguments(['--region', 'us-east-1', '--no-verify-ssl', 's3', 'ls', '--profile=foo'])
        self.assertTrue('--region' in args)
        self.assertEqual(args[args.index('--region')+1], 'us-east-1')
        self.assertTrue('--profile' in args)
        self.assertEqual(args[args.index('--profile')+1], 'foo')
        self.assertTrue('--no-verify-ssl' in args)
        self.assertEqual(len(args), 5)

    def test_token_key(self):
        self.assertEqual('aws', AWSAuthentication().token_key(['aws', 's3', 'ls']))
        self.assertEqual('aws,profile=foo', AWSAuthentication().token_key(['aws', 's3', '--profile', 'foo', 'ls']))
