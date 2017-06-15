#!/usr/bin/env python
import os

from setuptools import setup


def read_file(path):
    with open(os.path.join(os.path.dirname(__file__), path)) as fp:
        return fp.read()

setup(
    name='mfado',
    version='0.0',
    description='Like sudo, but for MFA.',
    url='https://github.com/ccbrown/mfado',
    long_description=read_file('README.md'),
    author='Christopher Brown',
    author_email='ccbrown112@gmail.com',
    packages=[
        'mfado',
        'mfado.authentication',
    ],
    entry_points={
        'console_scripts': [
            'mfado = mfado.setup:main',
            'mfado-exec = mfado.exec:main',
        ]
    },
    install_requires=[
        'python-dateutil'
    ],
    license='MIT'
)
