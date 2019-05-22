#!/usr/bin/env python3

""" test_preset.py
    Tests for colr.preset.Preset.
    -Christopher Welborn 05-21-2019
"""

import sys
import unittest
from random import SystemRandom

from colr import (
    __version__,
    Colr,
    Preset,
)

from .testing_tools import ColrTestCase

random = SystemRandom()


class PresetTests(ColrTestCase):
    """ Tests for the colr.Preset object. """
    def test_eq(self):
        """ __eq__ should work for identical Presets. """
        cases = (
            ('red', 'white', 'bold'),
            ('blue', 'red', 'normal'),
            (1, 2, None),
            ((1, 2, 3), (4, 5, 6), None),
        )
        for fore, back, style in cases:
            self.assertEqual(
                Preset(fore, back, style),
                Preset(fore, back, style),
                msg='Identical Presets did not compare equal.',
            )
        raiser = self.assertRaises(TypeError, msg='Failed to raise for __eq__.')
        for badtype in (1, 's', {}, None):
            with raiser:
                Preset() == badtype

    def test_hash(self):
        """ hash() should not change for identical Presets. """
        self.assertEqual(
            hash(Preset('red', 'white', 'bold')),
            hash(Preset('red', 'white', 'bold')),
            msg='hash() failed for identical Presets.'
        )

    def test_init(self):
        """ Initializing a Preset should work. """
        st = Preset('red', 'white', 'bold')
        for text in ('test', 'this', 'out okay?'):
            self.assertCallEqual(
                Colr(text, 'red', 'white', 'bold'),
                func=st,
                args=(text, ),
                msg='Failed to build correct Colr from Preset call.',
            )

    def test_lt(self):
        """ __lt__ should work for Presets. """
        styles = [
            Preset('black', 'grey', 'highlight'),
            Preset('blue', 'red', 'normal'),
            Preset('red', 'white', 'bold'),
            Preset('white', 'yellow', 'bold'),
            Preset('yellow', 'lightblue', 'underline'),
        ]
        randomized = styles[:]
        random.shuffle(randomized)

        self.assertListEqual(
            list(sorted(randomized)),
            styles,
            msg='Failed to sort Presets properly due to __lt__.',
        )

        cases = (
            (
                'fore',
                Preset('blue', 'white', 'normal'),
                Preset('red', 'blue', 'bold')
            ),
            (
                'back',
                Preset('blue', 'blue', 'normal'),
                Preset('blue', 'red', 'bold')
            ),
            (
                'style',
                Preset('red', 'blue', 'bold'),
                Preset('red', 'blue', 'normal')
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
                Preset() < badtype

    def test_merge(self):
        st = Preset('red', 'white', 'bold')
        st2 = Preset('blue')
        self.assertEqual(
            st.merge(st2),
            Preset('blue', 'white', 'bold'),
            msg='Failed to merge Preset properly.',
        )
        self.assertEqual(
            st.merge(st2, fore='yellow'),
            Preset('yellow', 'white', 'bold'),
            msg='Failed to merge Preset properly.',
        )
        self.assertEqual(
            st.merge(st2, back='black'),
            Preset('blue', 'black', 'bold'),
            msg='Failed to merge Preset properly.',
        )
        self.assertEqual(
            st.merge(st2, style='normal'),
            Preset('blue', 'white', 'normal'),
            msg='Failed to merge Preset properly.',
        )

    def test_repr(self):
        """ repr() should work for Presets. """
        # Main here for test coverage.
        self.assertEqual(
            repr(Preset('red', 'white', 'bold')),
            'Preset(fore=\'red\', back=\'white\', style=\'bold\')',
            msg='repr() is wrong.',
        )


if __name__ == '__main__':
    print('Testing Colr v. {}'.format(__version__))
    # unittest.main() calls sys.exit(status_code).
    unittest.main(argv=sys.argv, verbosity=2)  # type: ignore
