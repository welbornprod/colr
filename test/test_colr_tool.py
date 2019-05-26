#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" test_colr_tool.py
    Unit tests for colr.py command line tool.

    These tests should be ran with `green -q` to quiet stdout.
    If you are using nose then stdout should be quiet already.
    If you are using unittest to run these, then -b should work to quiet them.
    -Christopher Welborn 12-09-2015
"""

import random
import sys
import unittest

from colr import (
    Colr,
    hex2rgb,
    name_data,
    InvalidArg,
    InvalidColr,
    InvalidStyle,
    rgb2hex,
)
from colr.__main__ import (
    __version__,
    InvalidNumber,
    InvalidRgb,
    get_colr,
)

from .testing_tools import (
    ColrToolTestCase,
    StdOutCatcher,
)

r = random.SystemRandom()

# Save names in list format, for random.choice().
name_data_names = list(name_data)


class ColrToolTests(ColrToolTestCase):
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
            '--names': False,
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

    def test_auto_disable(self):
        """ colr tool should auto disable when asked. """
        argd = {'TEXT': 'Hello', 'FORE': 'red', '--auto-disable': True}
        self.assertMain(
            argd,
            stdout='\x1b[31mHello\x1b[0m\n',
            msg='main() with --auto-disable failed.'
        )

    def test_basic_colors(self):
        """ colr tool should recognize basic colors. """
        argd = {'TEXT': 'Hello World', 'FORE': 'green', 'BACK': 'blue'}
        for _ in range(10):
            argd['FORE'] = r.choice(self.valid_basic_vals)
            argd['BACK'] = r.choice(self.valid_basic_vals)
            self.assertMain(argd, msg='main() failed with valid args.')
        # Invalid color names should raise a InvalidColr.
        badargsets = (
            {'FORE': 'XXX', 'BACK': r.choice(self.valid_basic_vals)},
            {'BACK': 'XXX', 'FORE': r.choice(self.valid_basic_vals)},
        )
        for argset in badargsets:
            argd.update(argset)
            with self.assertRaises(InvalidColr):
                self.run_main_test(argd, should_fail=True)

    def test_debug_deps(self):
        """ colr tool should load debug dependencies. """
        argd = {'TEXT': 'Hello', '--debug': True}
        self.assertMain(argd, msg='main() with --debug failed.')

    def test_entry_point(self):
        """ entry_point() should run and handle the exit status code. """
        argd = {'TEXT': 'test'}
        self.assertEntry(argd, stdout='test')
        argd = {'TEXT': 'test', 'FORE': 'blah'}
        self.assertEntry(argd, should_fail=True)

    def test_extended_colors(self):
        """ colr tool should recognize extended colors. """
        argd = {'TEXT': 'Hello World', 'FORE': '235'}
        for _ in range(10):
            argd['FORE'] = r.choice(self.valid_ext_vals)
            argd['BACK'] = r.choice(self.valid_ext_vals)
            self.assertMain(argd, msg='main() failed on extended colors.')
        # Invalid color values should raise a InvalidColr.
        badargsets = (
            {'FORE': '1000', 'BACK': r.choice(self.valid_ext_vals)},
            {'BACK': '-1', 'FORE': r.choice(self.valid_ext_vals)},
        )
        for argset in badargsets:
            argd.update(argset)
            with self.assertRaises(InvalidColr):
                self.run_main_test(argd, should_fail=True)

    def test_gradient(self):
        """ colr tool should do basic gradients. """
        for name in self.valid_basic_vals:
            for spread in range(3):
                argd = {
                    'TEXT': 'test',
                    '--gradient': name,
                    '--spread': str(spread),
                }
                self.assertMain(
                    argd,
                    msg='main() failed on valid --gradient name.',
                )

        for badspread in ('s', 'x', 'bad'):
            argd['--spread'] = badspread
            with self.assertRaises(InvalidNumber):
                self.run_main_test(argd)

    def test_gradient_rgb(self):
        """ colr tool should do basic rgb gradients. """
        for i in range(256):
            i1 = str(i)
            i2 = str((i + 255) % 255)
            rgbs = [
                ','.join((i1, i1, i1)),
                ','.join((i2, i2, i2)),
            ]
            argd = {'TEXT': 'test', '--gradientrgb': rgbs}
            self.assertMain(
                argd,
                msg='main() failed on valid --gradientrgb args.',
            )
        argd = {'TEXT': 'test', '--gradientrgb': ['0,0,0', '1,1,1', '2,2,2']}
        raiser = self.assertRaises(
            InvalidArg,
            msg='main() should have failed with more than 2 --gradientrgb args.'
        )
        with raiser:
            self.run_main_test(argd, should_fail=True)

        # Invalid rgb values should raise a InvalidColr.
        badargsets = (
            {'--gradientrgb': ['-1,25,25', r.choice(self.valid_rgb_vals)]},
            {'--gradientrgb': ['257,25,25', r.choice(self.valid_rgb_vals)]},
            {'--gradientrgb': ['a,255,255', r.choice(self.valid_rgb_vals)]},
            {'--gradientrgb': ['xxx', r.choice(self.valid_rgb_vals)]},
        )
        for argset in badargsets:
            argd.update(argset)
            with self.assertRaises(InvalidRgb):
                self.run_main_test(argd, should_fail=True)

    def test_hex_colors(self):
        """ colr tool should recognize hex colors. """
        argd = {'TEXT': 'Hello World', 'FORE': 'd7d7d7'}
        for _ in range(10):
            argd['FORE'] = r.choice(self.valid_hex_vals)
            argd['BACK'] = r.choice(self.valid_hex_vals)
            self.assertMain(argd, msg='main() failed on hex colors.')

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
        argd = {'TEXT': 'Hello World', '--truecolor': False}
        badargsets = (
            {'FORE': 'ffooll', 'BACK': r.choice(self.valid_hex_vals)},
            {'BACK': 'oopsie', 'FORE': r.choice(self.valid_hex_vals)},
        )
        for argset in badargsets:
            argd.update(argset)
            with self.assertRaises(InvalidColr):
                self.run_main_test(argd, should_fail=True)

    def test_just(self):
        """ colr tool should justify text with --center, --ljust, and --rjust.
        """
        s = 'test'
        cases = {
            ('--ljust', 10): '\x1b[31mtest\x1b[0m      \n',
            ('--rjust', 10): '      \x1b[31mtest\x1b[0m\n',
            ('--center', 10): '   \x1b[31mtest\x1b[0m   \n',
        }
        for argset, expected in cases.items():
            argd = {'TEXT': s, 'FORE': 'red', argset[0]: str(argset[1])}
            self.assertMain(
                argd,
                stdout=expected,
                msg='Justification failed for {}={}.'.format(
                    argset[0],
                    argset[1],
                ),
            )

    def test_list_codes(self):
        """ colr tool should list escape codes with --listcodes. """
        cases = {
            s: str(Colr('test', s))
            for s in ('red', 'blue', 'green', 'white')
        }
        for name, s in cases.items():
            argd = {'TEXT': s, '--listcodes': True}
            self.assertMainIn(
                argd,
                stdout=name,
                msg='main() with --listcodes did not recognize an escape code.',
            )

    def test_list_names(self):
        """ colr tool should list names with --names. """
        argd = {'--names': True}
        self.assertMain(argd, msg='main() failed with --names')

    def test_rainbow(self):
        """ colr tool should work for basic rainbows. """
        argsets = []
        for offset in range(0, 256):
            for freq in range(0, 11):
                freq = freq * 0.1
                for width in range(1, 4):
                    argd = {
                        'TEXT': 'test',
                        '--rainbow': True,
                        '--offset': str(offset),
                        '--frequency': str(freq),
                        '--width': str(width),
                    }
                    argsets.append(argd)
        for argd in argsets:
            self.assertMain(
                argd,
                msg='main() with --rainbow failed for valid args.',
            )

        for badfreq in ('s', 'bad', 'x2'):
            argd['--frequency'] = badfreq
            with self.assertRaises(InvalidNumber):
                self.run_main_test(argd)

    def test_rgb_colors(self):
        """ colr tool should recognize rgb colors. """
        argd = {'TEXT': 'Hello World', 'FORE': '25, 25, 25'}
        with StdOutCatcher():
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

    def test_strip_codes(self):
        """ colr tool should strip escape codes with --stripcodes. """
        cases = [
            str(Colr(' ').join(Colr('test', s), Colr('this', 'blue')))
            for s in ('red', 'blue', 'green', 'white')
        ]
        # Purposely starting at 1, and ending at 254 because of i + 1, i - 1.
        cases.extend(
            str(Colr(' ').join(
                Colr('test', i, back=i + 1),
                Colr('this', i - 1)
            ))
            for i in range(1, 255)
        )
        for s in cases:
            argd = {'TEXT': s, '--stripcodes': True}
            self.assertMain(
                argd,
                stdout='test this',
                msg='main() with --stripcodes did not strip codes properly.',
            )

    def test_styles(self):
        """ colr tool should recognize styles. """
        argd = {'TEXT': 'Hello World', 'FORE': '235', 'STYLE': 'normal'}
        for _ in range(10):
            argd['STYLE'] = r.choice(self.valid_style_vals)
            self.assertMain(argd, msg='main() failed with valid style arg.')
        # Invalid style values should raise a InvalidStyle.
        badargsets = (
            {'STYLE': 'dimmer'},
            {'STYLE': 'x'},
        )
        for argset in badargsets:
            argd.update(argset)
            with self.assertRaises(InvalidStyle):
                self.run_main_test(argd, should_fail=True)

    def test_translate(self):
        """ colr tool should translate color names/codes with --translate. """
        for name in self.valid_basic_vals:
            argd = {'CODE': [name], '--translate': True}
            self.assertMainIn(
                argd,
                stdout=name,
                msg='stdout was missing the color name.',
            )

        for name in range(9, 256):
            s = str(name)
            argd = {'CODE': [s], '--translate': True}
            self.assertMainIn(
                argd,
                stdout='Name: {}'.format(s),
                msg='stdout was missing the extended color name.',
            )
            rgb = ','.join((s, s, s))
            argd = {'CODE': [rgb], '--translate': True}
            self.assertMain(
                argd,
                msg='main() with --translate failed for valid rgb code.',
            )

        for badname in ('blah', '256', 'not-a-color', 'x,y,z'):
            argd = {'CODE': [badname], '--translate': True}
            self.assertMain(
                argd,
                should_fail=True,
            )


if __name__ == '__main__':
    print('Testing Colr Tool v. {}'.format(__version__))
    # unittest.main() calls sys.exit(status_code).
    unittest.main(argv=sys.argv, verbosity=2)
