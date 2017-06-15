from __future__ import print_function
import os
import sys


def main(args=sys.argv):
    print('''
    *** ADDITIONAL SETUP REQUIRED ***

    To manipulate the terminal environment, mfado must be invoked through an alias.

    If you're using ZSH, you can install this alias by adding the following to your .zshrc file:

        mfado () { eval $(mfado-exec "$@") }

    If you're using another shell, you need to add an alias with the same effect as the ones above.

    Once you've created the alias, you'll need to start a new shell session.

    See mfado-exec --help for more options.
    ''', file=sys.stderr)
    sys.exit(1)

if __name__ == '__main__':
    main()
