#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" test_colrtestcase.py
    Unit tests for colr's test.testing_tools.ColrTestCase

    -Christopher Welborn 03-29-2017
"""

import os
import sys
import unittest

from .testing_tools import ColrTestCase


# These are failing tests, to check the format for ColrTestCase messages.
# They can be ran from the command line by prepending:
#   COLR_TEST_MSGS=1
# ..to the test command.
# Example:
#   COLR_TEST_MSGS=1 green -q -vv
run_test_val = os.environ.get('COLR_TEST_MSGS', 0) or 0
try:
    RUN_TESTS = bool(int(run_test_val))
except (TypeError, ValueError):
    # Invalid environment var setting, 'y[..]' and 't[...]' are okay I guess.
    RUN_TESTS = str(run_test_val).lower().startswith(('t', 'y'))

skipmsg = ' '.join((
    'Not testing ColrTestCase messages.',
    'Set `COLR_TEST_MSGS=1` to test.',
))


@unittest.skipUnless(RUN_TESTS, skipmsg)
class FailingTests(ColrTestCase):
    def test_eq(self):
        """ Equal failures should print a pretty message. """
        self.assertEqual(1, 2, msg='Nope, not equal.')

    def test_neq(self):
        """ Non-equal failures should print a pretty message. """
        self.assertNotEqual(1, 1, msg='Oops, they are equal')

    def test_call_eq(self):
        """ Equal func return should print a pretty message. """
        self.assertCallEqual(
            1,
            2,
            func=str,
            args=[1],
            otherargs=[2],
            kwargs={'testing': True},
            otherkwargs={'testing': True},
            msg='Nope, not equal.',
        )

    def test_call_neq(self):
        """ Non-equal func return should print a pretty message. """
        self.assertCallNotEqual(
            1,
            1,
            func=str,
            args=[1],
            kwargs={'testing': True},
            otherargs=[1],
            otherkwargs={'testing': True},
            msg='Oops, they are equal.',
        )

    def test_call_tuple_eq(self):
        """ Equal tuple func return should print a pretty message. """
        self.assertCallTupleEqual(
            (1,),
            (2,),
            func=str,
            args=[1],
            kwargs={'testing': True},
            otherargs=[2],
            otherkwargs={'testing': True},
            msg='Nope, not equal.',
        )

    def test_call_true(self):
        """ True func return should print a pretty message. """
        self.assertCallTrue(
            False,
            func=str,
            args=[1],
            kwargs={'testing': True},
            msg='Nope not true.',
        )

    def test_call_false(self):
        """ False func return should print a pretty message. """
        self.assertCallFalse(
            True,
            func=str,
            args=[1],
            kwargs={'testing': True},
            msg='Nope not false.',
        )

    def test_call_raises(self):
        """ Func raises should print a pretty message. """
        with self.assertCallRaises(
                ValueError,
                func=None,
                args=[1],
                kwargs={'testing': True},
                msg='Nope, did not raise.'):
            pass


if __name__ == '__main__':
    unittest.main(argv=sys.argv, verbosity=2)
