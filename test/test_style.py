#!/usr/bin/env python3

""" test_style.py
    Tests for colr.style.Style.
    -Christopher Welborn 05-21-2019
"""

import sys
import unittest
from random import SystemRandom

from colr import (
    __version__,
    Colr,
    Style,
)

from .testing_tools import ColrTestCase

random = SystemRandom()


class StyleTests(ColrTestCase):
    """ Tests for the colr.Style object. """
    def test_eq(self):
        """ __eq__ should work for identical Styles. """
        cases = (
            ('red', 'white', 'bold'),
            ('blue', 'red', 'normal'),
            (1, 2, None),
            ((1, 2, 3), (4, 5, 6), None),
        )
        for fore, back, style in cases:
            self.assertEqual(
                Style(fore, back, style),
                Style(fore, back, style),
                msg='Identical Styles did not compare equal.',
            )
        raiser = self.assertRaises(TypeError, msg='Failed to raise for __eq__.')
        for badtype in (1, 's', {}, None):
            with raiser:
                Style() == badtype

    def test_hash(self):
        """ hash() should not change for identical Styles. """
        self.assertEqual(
            hash(Style('red', 'white', 'bold')),
            hash(Style('red', 'white', 'bold')),
            msg='hash() failed for identical Styles.'
        )

    def test_init(self):
        """ Initializing a Style should work. """
        st = Style('red', 'white', 'bold')
        for text in ('test', 'this', 'out okay?'):
            self.assertCallEqual(
                Colr(text, 'red', 'white', 'bold'),
                func=st,
                args=(text, ),
                msg='Failed to build correct Colr from Style call.',
            )

    def test_lt(self):
        """ __lt__ should work for Styles. """
        styles = [
            Style('black', 'grey', 'highlight'),
            Style('blue', 'red', 'normal'),
            Style('red', 'white', 'bold'),
            Style('white', 'yellow', 'bold'),
            Style('yellow', 'lightblue', 'underline'),
        ]
        randomized = styles[:]
        random.shuffle(randomized)

        self.assertListEqual(
            list(sorted(randomized)),
            styles,
            msg='Failed to sort Styles properly due to __lt__.',
        )

        cases = (
            (
                'fore',
                Style('blue', 'white', 'normal'),
                Style('red', 'blue', 'bold')
            ),
            (
                'back',
                Style('blue', 'blue', 'normal'),
                Style('blue', 'red', 'bold')
            ),
            (
                'style',
                Style('red', 'blue', 'bold'),
                Style('red', 'blue', 'normal')
            ),
        )
        for argtype, a, b in cases:
            self.assertLess(
                a,
                b,
                msg='__lt__ failed on a {} color.'.format(argtype),
            )
            self.assertGreater(
                b,
                a,
                msg='__lt__ failed on a {} color.'.format(argtype),
            )
        raiser = self.assertRaises(TypeError, msg='Failed to raise for __lt__.')
        for badtype in (1, 's', {}, None):
            with raiser:
                Style() < badtype

    def test_merge(self):
        st = Style('red', 'white', 'bold')
        st2 = Style('blue')
        self.assertEqual(
            st.merge(st2),
            Style('blue', 'white', 'bold'),
            msg='Failed to merge Style properly.',
        )
        self.assertEqual(
            st.merge(st2, fore='yellow'),
            Style('yellow', 'white', 'bold'),
            msg='Failed to merge Style properly.',
        )
        self.assertEqual(
            st.merge(st2, back='black'),
            Style('blue', 'black', 'bold'),
            msg='Failed to merge Style properly.',
        )
        self.assertEqual(
            st.merge(st2, style='normal'),
            Style('blue', 'white', 'normal'),
            msg='Failed to merge Style properly.',
        )

    def test_repr(self):
        """ repr() should work for Styles. """
        # Main here for test coverage.
        self.assertEqual(
            repr(Style('red', 'white', 'bold')),
            'Style(fore=\'red\', back=\'white\', style=\'bold\')',
            msg='repr() is wrong.',
        )


if __name__ == '__main__':
    print('Testing Colr v. {}'.format(__version__))
    # unittest.main() calls sys.exit(status_code).
    unittest.main(argv=sys.argv, verbosity=2)  # type: ignore
