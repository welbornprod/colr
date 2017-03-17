#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" test_controls.py
    Unit tests for colr/controls.py.

    -Christopher Welborn 3-7-2017
"""

import sys
import unittest

from colr import (
    __version__,
    Colr,
)
from colr.controls import (
    Control,
    move,
)

from .testing_tools import ColrTestCase

print('Testing Colr.Control v. {}'.format(__version__))


class ControlTests(ColrTestCase):

    def test_add(self):
        """ Controls should be added to each other, Colrs, or strs. """
        types = {
            'Control': Control().move_down(1),
            'Colr': Colr('Test', 'red'),
            'str': 'testing',
        }
        for othername, other in types.items():
            ctl = Control().move_column(3)
            try:
                newctl = ctl + other
            except TypeError as ex:
                self.fail(
                    'Control + {} should not raise a TypeError.'.format(
                        othername
                    ))
            else:

                self.assertIsInstance(
                    newctl,
                    Control,
                    msg=(
                        'Adding {} to a Control did not return a Control.'
                    ).format(othername)
                )
                ctl_str_result = ''.join((str(ctl), str(other)))
                s = str(newctl)
                self.assertEqual(
                    ctl_str_result,
                    s,
                    msg='str(Control()) did not match.'
                )

    def test_bytes(self):
        """ bytes(Control()) should encode self.data. """
        s = 'test'
        a = s.encode()
        b = bytes(Control(s))
        self.assertEqual(a, b, msg='Encoded Control is not the same.')

    def test_hash(self):
        """ hash(Control()) should return a unique hash for self.data. """
        a, b = hash(Control().move_down()), hash(Control().move_down())
        self.assertCallEqual(
            a,
            b,
            func=hash,
            args=[a],
            otherargs=[b],
            msg='Mismatched hash values.',
        )
        b = hash(Control().move_up())
        self.assertCallNotEqual(
            a,
            b,
            func=hash,
            args=[a],
            otherargs=[b],
            msg='Hash values should not match.',
        )

    @unittest.skipUnless(False, 'No way to test the actual escape codes.')
    def test_move_column(self):
        """ move_column should move the cursor to the specified column. """
        # There is no way to test these right now.
        # Unless there is some file object that can parse escape sequences
        # and perform the actions? I need to do some research.
        pass

    def test_repeat(self):
        """ Control.repeat() should repeat the last code. """
        s = ''.join((
            str(move.up()),
            str(move.down()),
            str(move.down()),
            str(move.down()),
        ))
        ctl = Control().move_up().move_down().repeat(3)
        self.assertEqual(
            s,
            str(ctl),
            msg='Control.repeat produced an unexpected result.',
        )

    def test_repeat_all(self):
        """ Control.repeat() should be like str(Control()) * count. """
        count = 3
        s = ''.join((
            str(move.up()),
            str(move.down()),
            str(move.down()),
            str(move.down()),
        )) * count
        ctl = Control().move_up().move_down().repeat(3)
        self.assertEqual(
            s,
            str(ctl.repeat_all(count)),
            msg='Control.repeat_all produced an unexpected result.',
        )


if __name__ == '__main__':
    # unittest.main() calls sys.exit(status_code).
    unittest.main(argv=sys.argv, verbosity=2)  # type: ignore
