from __future__ import print_function
import argparse
import base64
import calendar
import dateutil.parser
import datetime
import json
import os
import pipes
import shlex
import subprocess
import sys
import time

from .authentication import available_authentication_types


def fatal(msg):
    print('error: ' + msg, file=sys.stderr)
    sys.exit(1)


def utc_timestamp(ts):
    try:
        if isinstance(ts, str) or isinstance(ts, unicode):
            ts = dateutil.parser.parse(ts)
    except NameError:
        pass
    if isinstance(ts, datetime.datetime):
        ts = calendar.timegm(ts.utctimetuple())
    return ts


def shell_quote(s):
    try:
        return shlex.quote(s)
    except AttributeError:
        return pipes.quote(s)


def main(args=sys.argv):
    try:
        parser = argparse.ArgumentParser(
            description='Ensures that a valid session token is present, refreshing it if needed, then outputs a script that will persist the token and invoke the given command.'
        )
        parser.add_argument('--min-remaining-token-lifespan', default=180, help='if the token has a shorter lifespan remaining, it is refreshed (default: 180)')
        parser.add_argument('--new-token-lifespan', default=900, help='the lifespan of newly refreshed tokens (default: 900)')
        parser.add_argument('--type', default='auto', choices=['auto']+available_authentication_types().keys(), help='the type of authentication to perform (default: auto)')
        parser.add_argument('command', nargs=argparse.REMAINDER)
        parsed = parser.parse_args(args[1:])

        if not parsed.command:
            fatal('a command is required')

        auth = available_authentication_types().get(parsed.command[0] if parsed.type == 'auto' else parsed.type)
        if not auth:
            fatal('unable to determine authentication type for \'{}\' command. recognized commands: {}'.format(parsed.command[0], ', '.join(available_authentication_types().keys())))

        if 'MFADO_SESSIONS' not in os.environ:
            print('eval $(MFADO_SESSIONS=$MFADO_SESSIONS ' + ' '.join([shell_quote(x) for x in sys.argv]) + ')')
            sys.exit(0)

        sessions = {}
        if os.environ['MFADO_SESSIONS']:
            sessions = json.loads(base64.b64decode(os.environ['MFADO_SESSIONS']))

        if 'tokens' not in sessions:
            sessions['tokens'] = {}

        token = sessions['tokens'].get(auth.token_key(parsed.command))
        if token is None or utc_timestamp(auth.token_expiration_time(token)) + parsed.min_remaining_token_lifespan < time.time():
            token = auth.request_token(
                parsed.command,
                new_token_lifespan=parsed.new_token_lifespan
            )
            sessions['tokens'][auth.token_key(parsed.command)] = token

        print('MFADO_SESSIONS=' + base64.b64encode(json.dumps(sessions).encode()).decode() + ';')
        env = auth.token_environment_variables(token)
        print(' '.join([k + '=' + v for k, v in env.items()] + [shell_quote(x) for x in auth.command_to_execute(parsed.command)]) + ';')
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        fatal(str(e))

if __name__ == '__main__':
    main()
