from __future__ import print_function
import argparse
import json
import subprocess
import sys
import time


class AWSAuthentication:
    def name(self):
        return 'aws'

    def _forwarded_arguments(self, args):
        string_args = ['endpoint-url', 'profile', 'region', 'ca-bundle', 'cli-read-timeout', 'cli-connect-timeout']
        boolean_args = ['no-verify-ssl', 'no-sign-request']

        parser = argparse.ArgumentParser()
        for arg in string_args:
            parser.add_argument('--' + arg, dest=arg)
        for arg in boolean_args:
            parser.add_argument('--' + arg, action='store_true', dest=arg)
        forwarded = vars(parser.parse_known_args(args)[0])

        ret = []
        for arg in string_args:
            if forwarded[arg] is not None:
                ret += ['--' + arg, forwarded[arg]]
        ret += ['--' + arg for arg in boolean_args if forwarded[arg]]
        return ret

    def _aws_command(self, command):
        return json.loads(subprocess.check_output(command + ['--output', 'json']).decode())

    def token_key(self, cmd):
        parser = argparse.ArgumentParser()
        parser.add_argument('--profile')
        args = parser.parse_known_args(cmd[1:])[0]
        return ','.join(['aws'] + (['profile='+args.profile] if args.profile else []))

    def token_expiration_time(self, token):
        return token['Expiration']

    def request_token(self, cmd, new_token_lifespan):
        forwarded_args = self._forwarded_arguments(cmd[1:])
        mfa_devices = self._aws_command(['aws'] + forwarded_args + ['iam', 'list-mfa-devices'])['MFADevices']
        if not mfa_devices:
            raise RuntimeError('no mfa devices are configured for your iam user')

        print('MFA Code: ', file=sys.stderr, end='')
        try:
            raw_input
        except NameError:
            raw_input = input
        token_code = str(raw_input()).strip()

        credentials = self._aws_command(['aws'] + forwarded_args + [
            'sts', 'get-session-token',
            '--duration-seconds', str(new_token_lifespan),
            '--serial-number', mfa_devices[0]['SerialNumber'],
            '--token-code', token_code,
        ])['Credentials']
        return credentials

    def token_environment_variables(self, token):
        return {
            'AWS_ACCESS_KEY_ID': token['AccessKeyId'],
            'AWS_SECRET_ACCESS_KEY': token['SecretAccessKey'],
            'AWS_SESSION_TOKEN': token['SessionToken'],
        }

    def command_to_execute(self, cmd):
        if '--profile' in cmd:
            return cmd[:cmd.index('--profile')] + cmd[cmd.index('--profile')+2:]
        return cmd
