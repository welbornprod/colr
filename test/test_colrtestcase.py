#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" test_colrtestcase.py
    Unit tests for colrtestcase.py v. 0.0.1

    -Christopher Welborn 03-29-2017
"""

import sys
import unittest

from .testing_tools import ColrTestCase


# These are failing tests, to check the format for ColrTestCase messages.
RUN_TESTS = False


@unittest.skipUnless(RUN_TESTS, 'Not testing ColrTestCase messages.')
class FailingTests(ColrTestCase):
    def test_fail_eq(self):
        """ Non-equal failures should print a pretty message. """
        self.assertEqual(1, 2, msg='Nope, not equal.')
        self.assertNotEqual(1, 1, msg='Oops, they are equal')
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
        self.assertCallTrue(
            False,
            func=str,
            args=[1],
            kwargs={'testing': True},
            msg='Nope not true.',
        )
        self.assertCallFalse(
            True,
            func=str,
            args=[1],
            kwargs={'testing': True},
            msg='Nope not false.',
        )
        with self.assertCallRaises(
                ValueError,
                func=None,
                args=[1],
                kwargs={'testing': True},
                msg='Nope, did not raise.'):
            pass


if __name__ == '__main__':
    unittest.main(argv=sys.argv, verbosity=2)
