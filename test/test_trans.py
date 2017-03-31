#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" test_trans.py
    Unit tests for colr/trans.py

    -Christopher Welborn 03-29-2017
"""

import sys
import unittest

from colr import (
    __version__,
)
from colr.trans import (
    ColorCode,
    fix_hex,
    hex2rgb,
    hex2term,
    hex2termhex,
    is_code,
    is_ext_code,
    is_rgb_code,
    rgb2hex,
    rgb2term,
    rgb2termhex,
    term2hex,
    term2rgb,
)
from .testing_tools import ColrTestCase


class TransTests(ColrTestCase):
    """ Tests for colr/trans.py """

    def setUp(self):
        # hex2termhex known values. (input, output)
        self.termhex_close = (
            ('faefba', 'ffffaf'),
            ('babada', 'afafd7'),
            ('dadada', 'd7d7d7')
        )

        # known conversions
        self.conversions = (
            {'code': '229', 'hexval': 'ffffaf', 'rgb': (255, 255, 175)},
            {'code': '146', 'hexval': 'afafd7', 'rgb': (175, 175, 215)},
            {'code': '188', 'hexval': 'd7d7d7', 'rgb': (215, 215, 215)},
        )

        # known conversion conflicts
        self.conv_conflicts = (
            (
                {'code': '15', 'hexval': 'ffffff', 'rgb': (255, 255, 255)},
                {'code': '231', 'hexval': 'ffffff', 'rgb': (255, 255, 255)}
            ),
        )

    def test_colorcode(self):
        """ ColorCode should properly translate codes. """

        for v in self.conversions:
            for code in v.values():
                argset = (code,)
                self.assertCallEqual(
                    v,
                    ColorCode(*argset).to_dict(),
                    func=ColorCode,
                    args=argset,
                    msg='Failed to translate.',
                )

        for hexval, termhex in self.termhex_close:
            argset = (hexval,)
            self.assertCallEqual(
                termhex,
                ColorCode(*argset).hexval,
                func=ColorCode,
                args=argset,
                msg='Failed to find known close match.'
            )

    def test_fix_hex(self):
        """ fix_hex should translate short-form hex strings. """
        for argset in (('#f',), ('#ffffffXX',), ('',)):
            with self.assertCallRaises(
                    ValueError,
                    func=fix_hex,
                    args=argset,
                    msg='Failed to raise.'):
                fix_hex(*argset)

        for argset, expected in (
            (('#fff',), 'ffffff'),
            (('fff',), 'ffffff'),
            (('000',), '000000'),
            (('##000',), '000000'),
            (('aaaaaa',), 'aaaaaa')
        ):
            self.assertCallEqual(
                expected,
                fix_hex(*argset),
                func=fix_hex,
                args=argset,
                msg='Failed to fix hex string.',
            )

    def test_hex2rgb(self):
        """ hex2rgb should translate well-formed codes, and raise on errors.
        """
        testargs = (('',), ('00 0000',))
        for argset in testargs:
            with self.assertCallRaises(
                    ValueError,
                    func=hex2rgb,
                    args=argset,
                    msg='Failed to raise.'):
                hex2rgb(*argset)

        argset = ('#f00',)
        kwset = {'allow_short': False}
        with self.assertCallRaises(
                ValueError,
                func=hex2rgb,
                args=argset,
                kwargs=kwset,
                msg='Failed to raise without.'):
            hex2rgb(*argset, **kwset)

        argset = (' #FF0000',)
        self.assertCallTupleEqual(
            hex2rgb(*argset),
            (255, 0, 0),
            func=hex2rgb,
            args=argset,
            msg='Failed to convert padded hex string.',
        )

        argset = ('#f00',)
        kwset = {'allow_short': True}
        self.assertCallTupleEqual(
            hex2rgb(*argset, **kwset),
            (255, 0, 0),
            func=hex2rgb,
            args=argset,
            kwargs=kwset,
            msg='Failed to convert short form hex string.',
        )

    def test_is_code(self):
        """ colr.trans.is_code should recognize a color code. """
        validcodes = ('\033[31m', '\033[41m')
        invalidcode = '\033[38;5;27m'
        for validcode in validcodes:
            self.assertTrue(is_code(validcode))
        self.assertFalse(is_code(invalidcode))

    def test_is_ext_code(self):
        """ colr.trans.is_ext_code should recognize a color code. """
        validcodes = ('\033[38;5;42m', '\033[48;5;42m')
        invalidcode = '\033[10m'
        for validcode in validcodes:
            self.assertTrue(is_ext_code(validcode))
        self.assertFalse(is_ext_code(invalidcode))

    def test_is_rgb_code(self):
        """ colr.trans.is_rgb_code should recognize a color code. """
        validcodes = ('\033[38;2;0;0;255m', '\033[48;2;0;0;255m')
        invalidcode = '\033[10m'
        for validcode in validcodes:
            self.assertTrue(is_rgb_code(validcode))
        self.assertFalse(is_rgb_code(invalidcode))

    def test_trans(self):
        """ Translation functions should translate codes properly. """
        for v in self.conversions:
            # hex2*
            argset = (v['hexval'],)
            self.assertCallTupleEqual(
                v['rgb'],
                hex2rgb(*argset),
                func=hex2rgb,
                args=argset,
                msg='Failed to translate.',
            )

            argset = (v['hexval'],)
            self.assertCallEqual(
                v['code'],
                hex2term(*argset),
                func=hex2term,
                args=argset,
                msg='Failed to translate.',
            )

            argset = (v['hexval'],)
            self.assertCallEqual(
                v['hexval'],
                hex2termhex(*argset),
                func=hex2termhex,
                args=argset,
                msg='Failed to translate.',
            )

            # rgb2*
            argset = v['rgb']
            self.assertCallEqual(
                v['hexval'],
                rgb2hex(*argset),
                func=rgb2hex,
                args=argset,
                msg='Failed to translate.',
            )

            argset = v['rgb']
            self.assertCallEqual(
                v['code'],
                rgb2term(*argset),
                func=rgb2term,
                args=argset,
                msg='Failed to translate.',
            )

            argset = v['rgb']
            self.assertCallEqual(
                v['hexval'],
                rgb2termhex(*argset),
                func=rgb2termhex,
                args=argset,
                msg='Failed to translate.',
            )

            # term2*
            argset = (v['code'],)
            self.assertCallEqual(
                v['hexval'],
                term2hex(*argset),
                func=term2hex,
                args=argset,
                msg='Failed to translate.',
            )

            argset = (v['code'],)
            self.assertCallTupleEqual(
                v['rgb'],
                term2rgb(*argset),
                func=term2rgb,
                args=argset,
                msg='Failed to translate.',
            )

            for hexval, termhex in self.termhex_close:
                argset = (hexval,)
                self.assertCallEqual(
                    termhex,
                    hex2termhex(*argset),
                    func=hex2termhex,
                    args=argset,
                    msg='Failed on close match.',
                )


if __name__ == '__main__':
    print('Testing Colr.trans v. {}'.format(__version__))
    # unittest.main() calls sys.exit(status_code).
    unittest.main(argv=sys.argv, verbosity=2)  # type: ignore
