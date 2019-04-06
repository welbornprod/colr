#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" test_colr_docopt.py
    Unit tests for colr.docopt.

    -Christopher Welborn 4-6-2019
"""
import sys
import unittest

from colr import (
    docopt,
    docopt_file,
    docopt_version,
)
from colr.__main__ import (
    __version__,
)

from .testing_tools import ColrTestCase


class ColrDocoptTests(ColrTestCase):
    def setUp(self):
        self.usage = """
Usage:
    colrtest -h | -v

Options:
    -h,--help     : Show this message.
    -v,--version  : Show version and exit.
"""
        self.script = 'colrtest'
        self.version = '0.0.0'

    def call_testinfo(self, testinfo):
        return testinfo['func'](*testinfo['args'], **testinfo['kwargs'])

    def test_basic_call(self):
        """ colr.docopt should at least be callable. """
        testinfo = {
            'func': docopt,
            'args': (self.usage, ),
            'kwargs': {
                'argv': ['-v'],
                'version': self.version,
                'script': self.script,
            }
        }
        testflags = {
            '-h': 'help only',
            '--help': 'help only (long form)',
            '-v': 'version only',
            '--version': 'version only (long form)',
        }
        for flag, desc in testflags.items():
            testinfo['kwargs']['argv'] = [flag]
            testinfo['msg'] = 'Docopt failed with {}, {}.'.format(flag, desc)
            with self.assertCallRaises(SystemExit, **testinfo):
                self.call_testinfo(testinfo)


if __name__ == '__main__':
    print('Testing Colr v. {}'.format(__version__))
    print('against docopt v. {} from: {}'.format(docopt_version, docopt_file))
    # unittest.main() calls sys.exit(status_code).
    unittest.main(argv=sys.argv, verbosity=2)
