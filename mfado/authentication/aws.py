from __future__ import print_function
import argparse
import json
import os
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

    def _aws_command(self, command, env_overrides={}):
        env = os.environ.copy()
        env.update(env_overrides)
        return json.loads(subprocess.check_output(['aws'] + command + ['--output', 'json'], env=env).decode())

    def token_key(self, cmd):
        parser = argparse.ArgumentParser()
        parser.add_argument('--profile')
        args = parser.parse_known_args(cmd[1:])[0]
        return ','.join(['aws'] + (['profile='+args.profile] if args.profile else []))

    def token_expiration_time(self, token):
        return token['Expiration']

    def request_token(self, cmd, new_token_lifespan):
        roles_to_assume = []
        profile = cmd[cmd.index('--profile')+1] if '--profile' in cmd else os.environ.get('AWS_DEFAULT_PROFILE')
        while True:
            try:
                source_profile = subprocess.check_output(['aws', 'configure', 'get', 'source_profile'] + (['--profile', profile] if profile else [])).decode().strip()
            except subprocess.CalledProcessError:
                break
            role_arn = subprocess.check_output(['aws', 'configure', 'get', 'role_arn'] + (['--profile', profile] if profile else [])).decode().strip()
            roles_to_assume.insert(0, role_arn)
            profile = source_profile

        forwarded_args = self._strip_profile_args(self._forwarded_arguments(cmd[1:])) if cmd[0] == 'aws' else []

        mfa_args = forwarded_args
        if profile:
            mfa_args.extend(['--profile', profile])

        mfa_devices = self._aws_command(mfa_args + ['iam', 'list-mfa-devices'])['MFADevices']
        if not mfa_devices:
            raise RuntimeError('no mfa devices are configured for your iam user')

        print('MFA Code: ', file=sys.stderr, end='')
        try:
            token_code = str(raw_input()).strip()
        except NameError:
            token_code = str(input()).strip()

        credentials = self._aws_command(mfa_args + [
            'sts', 'get-session-token',
            '--duration-seconds', str(new_token_lifespan),
            '--serial-number', mfa_devices[0]['SerialNumber'],
            '--token-code', token_code,
        ])['Credentials']

        for role in roles_to_assume:
            credentials = self._aws_command(forwarded_args + [
                'sts', 'assume-role',
                '--role-arn', role,
                '--role-session-name', 'AWS-CLI-session-{}'.format(int(time.time())),
                '--duration-seconds', str(new_token_lifespan),
            ], env_overrides=self.token_environment_variables(credentials))['Credentials']

        return credentials

    def token_environment_variables(self, token):
        return {
            'AWS_ACCESS_KEY_ID': token['AccessKeyId'],
            'AWS_SECRET_ACCESS_KEY': token['SecretAccessKey'],
            'AWS_SESSION_TOKEN': token['SessionToken'],
        }

    def _strip_profile_args(self, args):
        if '--profile' in args:
            return args[:args.index('--profile')] + args[args.index('--profile')+2:]
        return args

    def command_to_execute(self, cmd):
        return self._strip_profile_args(cmd) if cmd[0] == 'aws' else cmd
