#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" test_colr_tool.py
    Unit tests for colr.py command line tool.

    These tests should be ran with `green -q` to quiet stdout.
    If you are using nose then stdout should be quiet already.
    If you are using unittest to run these, then -b should work to quiet them.
    -Christopher Welborn 12-09-2015
"""

import json
import random
import sys
import unittest

from colr import (
    Colr,
    hex2rgb,
    name_data,
    InvalidColr,
    InvalidStyle,
    rgb2hex,
)
from colr.__main__ import (
    __version__,
    get_colr,
    main
)

from .testing_tools import ColrTestCase

r = random.SystemRandom()

print('Testing Colr Tool v. {}'.format(__version__))

# Save names in list format, for random.choice().
name_data_names = list(name_data)


class ColrToolTests(ColrTestCase):
    def setUp(self):
        # Default argd, when no flags are given.
        self.argd = {
            '--auto-disable': False,
            '--back': None,
            '--center': None,
            '--debug': False,
            '--err': False,
            '--fore': None,
            '--frequency': None,
            '--gradient': None,
            '--gradientrgb': [],
            '--help': False,
            '--listcodes': False,
            '--ljust': None,
            '--newline': False,
            '--offset': None,
            '--rainbow': False,
            '--rjust': None,
            '--spread': None,
            '--stripcodes': False,
            '--style': None,
            '--translate': False,
            '--truecolor': False,
            '--unique': False,
            '--version': False,
            'BACK': None,
            'CODE': [],
            'FORE': None,
            'STYLE': None,
            'TEXT': None,
        }
        # Number of random values to generate for tests to choose from.
        max_vals = 50

        # Valid basic color name args for the colr tool.
        self.valid_basic_vals = (
            'white',
            'black',
            'red',
            'cyan',
            'green',
            'blue',
        )
        # Valid extended color names/values.
        self.valid_ext_vals = [
            'lightblue',
            'lightcyan',
        ]
        self.valid_ext_vals.extend(
            set((
                str(r.randint(0, 255))
                for _ in range(max_vals)
            ))
        )

        # Valid rgb color values.
        self.valid_rgb_vals = []
        self.valid_rgb_vals.extend(
            set((
                ','.join(str(r.randint(0, 255)) for rgb in range(3))
                for _ in range(max_vals)
            ))
        )

        # Valid hex values.
        self.valid_hex_vals = ['000', 'fff', 'f0f', 'aba']
        for rgb in self.valid_rgb_vals:
            rgbtup = tuple(int(x) for x in rgb.split(','))
            self.valid_hex_vals.append(rgb2hex(*rgbtup))

        # Valid style names/values.
        self.valid_style_vals = (
            '0',
            '1',
            '2',
            '3',
            '4',
            '5',
            '7',
            '22',
            'b',
            'bold',
            'bright',
            'd',
            'dim',
            'f',
            'flash',
            'h',
            'highlight',
            'hilight',
            'hilite',
            'i',
            'italic',
            'n',
            'none',
            'normal',
            'reset_all',
            'reverse',
            'u',
            'underline',
            'underlined',
        )

    def make_argd(self, argd):
        """ Make a copy of self.argd and update it with values from argd.
            Returns the updated copy.
        """
        d = self.argd.copy()
        d.update(argd)
        return d

    def run_main_test(self, argd, should_fail=False):
        """ Run main() with the given argd, and fail on any errors. """
        argd = self.make_argd(argd)
        try:
            ret = main(argd)
        except (InvalidColr, InvalidStyle) as ex:
            if should_fail:
                raise
            # This should not have happened. Show detailed arg/exc info.
            self.fail(
                'Colr tool failed to run:\n{}\n    argd: {}'.format(
                    ex,
                    json.dumps(argd, sort_keys=True, indent=4)
                )
            )
        return ret

    def test_basic_colors(self):
        """ colr tool should recognize basic colors. """
        argd = {'TEXT': 'Hello World', 'FORE': 'green', 'BACK': 'blue'}
        for _ in range(10):
            argd['FORE'] = r.choice(self.valid_basic_vals)
            argd['BACK'] = r.choice(self.valid_basic_vals)
            self.assertEqual(
                0,
                self.run_main_test(argd, should_fail=False)
            )
        # Invalid color names should raise a InvalidColr.
        badargsets = (
            {'FORE': 'XXX', 'BACK': r.choice(self.valid_basic_vals)},
            {'BACK': 'XXX', 'FORE': r.choice(self.valid_basic_vals)},
        )
        for argset in badargsets:
            argd.update(argset)
            with self.assertRaises(InvalidColr):
                self.run_main_test(argd, should_fail=True)

    def test_extended_colors(self):
        """ colr tool should recognize extended colors. """
        argd = {'TEXT': 'Hello World', 'FORE': '235'}
        for _ in range(10):
            argd['FORE'] = r.choice(self.valid_ext_vals)
            argd['BACK'] = r.choice(self.valid_ext_vals)
            self.assertEqual(
                0,
                self.run_main_test(argd, should_fail=False)
            )
        # Invalid color values should raise a InvalidColr.
        badargsets = (
            {'FORE': '1000', 'BACK': r.choice(self.valid_ext_vals)},
            {'BACK': '-1', 'FORE': r.choice(self.valid_ext_vals)},
        )
        for argset in badargsets:
            argd.update(argset)
            with self.assertRaises(InvalidColr):
                self.run_main_test(argd, should_fail=True)

    def test_hex_colors(self):
        """ colr tool should recognize hex colors. """
        argd = {'TEXT': 'Hello World', 'FORE': 'd7d7d7'}
        for _ in range(10):
            argd['FORE'] = r.choice(self.valid_hex_vals)
            argd['BACK'] = r.choice(self.valid_hex_vals)
            self.assertEqual(
                0,
                self.run_main_test(argd, should_fail=False)
            )

        # Without -T, close matches should be used.
        argd = {'TEXT': 'Hello World', '--truecolor': False}
        hexvals = {
            '010203': '000000',
            '040506': '000000',
        }
        for hexval, closematch in hexvals.items():
            argd['FORE'] = hexval
            self.assertEqual(
                get_colr(argd['TEXT'], self.make_argd(argd)),
                Colr(argd['TEXT'], closematch),
                msg='Hex value close match failed without --truecolor.',
            )
        # With -T, rgb mode should be used.
        argd = {'TEXT': 'Hello World', '--truecolor': True}
        hexvals = (
            '010203',
            '040506',
        )
        for hexval in hexvals:
            argd['FORE'] = hexval
            self.assertEqual(
                get_colr(argd['TEXT'], self.make_argd(argd)),
                Colr(argd['TEXT'], hex2rgb(argd['FORE'])),
                msg='Hex value failed with --truecolor.',
            )
        # Invalid color values should raise a InvalidColr.
        argd['--truecolor'] = False

        argd = {'TEXT': 'Hello World'}
        badargsets = (
            {'FORE': 'ffooll', 'BACK': r.choice(self.valid_hex_vals)},
            {'BACK': 'oopsie', 'FORE': r.choice(self.valid_hex_vals)},
        )
        for argset in badargsets:
            argd.update(argset)
            with self.assertRaises(InvalidColr):
                self.run_main_test(argd, should_fail=True)

    def test_rgb_colors(self):
        """ colr tool should recognize rgb colors. """
        argd = {'TEXT': 'Hello World', 'FORE': '25, 25, 25'}
        for _ in range(10):
            argd['FORE'] = r.choice(self.valid_rgb_vals)
            argd['BACK'] = r.choice(self.valid_rgb_vals)
            self.assertEqual(
                0,
                self.run_main_test(argd)
            )
        # Invalid rgb values should raise a InvalidColr.
        badargsets = (
            {'FORE': '-1,25,25', 'BACK': r.choice(self.valid_rgb_vals)},
            {'BACK': '257,25,25', 'FORE': r.choice(self.valid_rgb_vals)},
            {'FORE': 'a,255,255', 'BACK': r.choice(self.valid_rgb_vals)},
            {'BACK': 'xxx', 'FORE': r.choice(self.valid_rgb_vals)},
        )
        for argset in badargsets:
            argd.update(argset)
            with self.assertRaises(InvalidColr):
                self.run_main_test(argd, should_fail=True)

    def test_styles(self):
        """ colr tool should recognize styles. """
        argd = {'TEXT': 'Hello World', 'FORE': '235', 'STYLE': 'normal'}
        for _ in range(10):
            argd['STYLE'] = r.choice(self.valid_style_vals)
            self.assertEqual(
                0,
                self.run_main_test(argd, should_fail=False)
            )
        # Invalid style values should raise a InvalidStyle.
        badargsets = (
            {'STYLE': 'dimmer'},
            {'STYLE': 'x'},
        )
        for argset in badargsets:
            argd.update(argset)
            with self.assertRaises(InvalidStyle):
                self.run_main_test(argd, should_fail=True)


if __name__ == '__main__':
    # unittest.main() calls sys.exit(status_code).
    unittest.main(argv=sys.argv, verbosity=2)
