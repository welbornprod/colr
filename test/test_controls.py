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
from colr.controls import (  # noqa (missing tests for some of these)
    Control,
    cursor,
    cursor_hide,
    cursor_show,
    ensure_tty,
    erase,
    erase_display,
    erase_line,
    move,
    move_back,
    move_column,
    move_down,
    move_forward,
    move_next,
    move_pos,
    move_prev,
    move_return,
    move_up,
    position,
    pos_restore,
    pos_save,
    print_inplace,
    print_flush,
    print_overwrite,
    scroll,
    scroll_down,
    scroll_up,
)

from .testing_tools import (
    ColrTestCase,
    TestFile,
)


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
            except TypeError:
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


class ControlsModuleTests(ColrTestCase):
    """ Tests for module-level functions in colr/controls.py. """
    def test_ensure_tty(self):
        """ ensure_tty() should raise when needed. """
        f = TestFile()
        with self.assertRaises(TypeError):
            ensure_tty(file=f)

        fake = TestFile(tty=True)
        try:
            ensure_tty(fake)
        except TypeError as ex:
            self.fail('Shouldn\'t raise for tty.\n{}'.format(ex))

    def test_cursor_hide(self):
        """ cursor_hide should write to file. """
        f = TestFile()
        cursor_hide(file=f)
        self.assertEqual(
            str(f),
            str(cursor.hide()),
            msg='cursor_hide failed to write to file.',
        )

    def test_cursor_show(self):
        """ cursor_show should write to file. """
        f = TestFile()
        cursor_show(file=f)
        self.assertEqual(
            str(f),
            str(cursor.show()),
            msg='cursor_show failed to write to file.',
        )

    def test_erase_display(self):
        """ erase_display should write to file. """
        f = TestFile()
        erase_display(file=f)
        self.assertEqual(
            str(f),
            str(erase.display()),
            msg='erase_display failed to write to file.',
        )

    def test_erase_line(self):
        """ erase_line should write to file. """
        f = TestFile()
        erase_line(file=f)
        self.assertEqual(
            str(f),
            str(erase.line()),
            msg='erase_line failed to write to file.',
        )

    def test_move_back(self):
        """ move_back should write to file. """
        f = TestFile()
        move_back(file=f)
        self.assertEqual(
            str(f),
            str(move.back()),
            msg='move_back failed to write to file.'
        )

    def test_move_column(self):
        """ move_column should write to file. """
        f = TestFile()
        move_column(file=f)
        self.assertEqual(
            str(f),
            str(move.column()),
            msg='move_column failed to write to file.'
        )

    def test_move_down(self):
        """ move_down should write to file. """
        f = TestFile()
        move_down(file=f)
        self.assertEqual(
            str(f),
            str(move.down()),
            msg='move_down failed to write to file.'
        )

    def test_move_forward(self):
        """ move_forward should write to file. """
        f = TestFile()
        move_forward(file=f)
        self.assertEqual(
            str(f),
            str(move.forward()),
            msg='move_forward failed to write to file.'
        )

    def test_move_next(self):
        """ move_next should write to file. """
        f = TestFile()
        move_next(file=f)
        self.assertEqual(
            str(f),
            str(move.next()),
            msg='move_next failed to write to file.'
        )

    def test_move_pos(self):
        """ move_pos should write to file. """
        f = TestFile()
        move_pos(file=f)
        self.assertEqual(
            str(f),
            str(move.pos()),
            msg='move_pos failed to write to file.'
        )

    def test_move_prev(self):
        """ move_prev should write to file. """
        f = TestFile()
        move_prev(file=f)
        self.assertEqual(
            str(f),
            str(move.prev()),
            msg='move_prev failed to write to file.'
        )

    def test_move_return(self):
        """ move_return should write to file. """
        f = TestFile()
        move_return(file=f)
        self.assertEqual(
            str(f),
            str(move.carriage_return()),
            msg='move_return failed to write to file.'
        )

    def test_move_up(self):
        """ move_up should write to file. """
        f = TestFile()
        move_up(file=f)
        self.assertEqual(
            str(f),
            str(move.up()),
            msg='move_up failed to write to file.'
        )


if __name__ == '__main__':
    print('Testing Colr.Control v. {}'.format(__version__))
    # unittest.main() calls sys.exit(status_code).
    unittest.main(argv=sys.argv, verbosity=2)  # type: ignore
