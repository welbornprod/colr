#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" test_colr.py
    Unit tests for colr.py.

    -Christopher Welborn 12-09-2015
"""

import inspect
import sys
import unittest

from typing import Any, Callable, Mapping, Optional, no_type_check

from colr import (
    __version__,
    color,
    Colr,
    ColorCode,
    fix_hex,
    hex2rgb,
    hex2term,
    hex2termhex,
    rgb2hex,
    rgb2term,
    rgb2termhex,
    term2hex,
    term2rgb,
    strip_codes,
)


def func_name(level: Optional[int]=1, parent: Optional[Callable]=None) -> str:
    """ Return the name of the function that is calling this function. """
    frame = inspect.currentframe()
    # Go back a number of frames (usually 1).
    backlevel = level or 1
    while backlevel > 0:
        frame = frame.f_back
        backlevel -= 1
    if parent:
        func = '{}.{}'.format(parent.__class__.__name__, frame.f_code.co_name)
        return func

    return frame.f_code.co_name


def test_msg(s: str, *args: Any, **kwargs: Mapping[Any, Any]):
    """ Return a message suitable for the `msg` arg in asserts,
        including the calling function name.
    """
    argstr = ', '.join(repr(a) for a in args)
    kwargstr = ', '.join('{}={!r}'.format(k, v) for k, v in kwargs.items())
    argrepr = ', '.join(s for s in (argstr, kwargstr) if s)
    return '{}({}): {}'.format(
        func_name(level=2),
        argrepr,
        s)


@no_type_check
class ColrTest(unittest.TestCase):

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
                self.assertEqual(
                    v,
                    ColorCode(*argset).to_dict(),
                    msg=test_msg('Failed to translate.', *argset))

        for hexval, termhex in self.termhex_close:
            argset = (hexval,)
            self.assertEqual(
                termhex,
                ColorCode(*argset).hexval,
                msg=test_msg('Failed to find known close match.', *argset))

    def test_fix_hex(self):
        """ fix_hex should translate short-form hex strings. """
        for argset in (('#f',), ('#ffffffXX',), ('',)):
            with self.assertRaises(
                    ValueError,
                    msg=test_msg('Failed to raise.', *argset)):
                _ = fix_hex(*argset)  # noqa

        for argset, expected in (
            (('#fff',), 'ffffff'),
            (('##000',), '000000'),
            (('aaaaaa',), 'aaaaaa')
        ):
            self.assertEqual(
                expected,
                fix_hex(*argset),
                msg=test_msg('Failed to fix hex string.', *argset))

    def test_hex2rgb(self):
        """ hex2rgb should translate well-formed codes, and raise on errors.
        """
        testargs = (('',), ('00 0000',))
        for argset in testargs:
            with self.assertRaises(
                    ValueError,
                    msg=test_msg('Failed to raise.', *argset)):
                _ = hex2rgb(*argset)

        argset = ('#f00',)
        kwset = {'allow_short': False}
        with self.assertRaises(
                ValueError,
                msg=test_msg('Failed to raise without.', *argset, **kwset)):
            _ = hex2rgb(*argset, **kwset)  # noqa

        argset = (' #FF0000',)
        self.assertTupleEqual(
            hex2rgb(*argset),
            (255, 0, 0),
            msg=test_msg('Failed to convert padded hex string.', *argset))

        argset = ('#f00',)
        kwset = {'allow_short': True}
        self.assertTupleEqual(
            hex2rgb(*argset, **kwset),
            (255, 0, 0),
            msg=test_msg(
                'Failed to convert short form hex string.', *argset, **kwset))

    def test_strip_codes(self):
        """ strip_codes() should strip all color and reset codes. """
        self.assertEqual(
            'hello world',
            strip_codes(
                Colr('hello world', fore='green', back='blue', style='bright')
            ),
            msg=test_msg('Failed to strip codes from Colr string.'))

        self.assertEqual(
            'hello world',
            strip_codes(
                color('hello world', fore='red', back='blue', style='bright')
            ),
            msg=test_msg('Failed to strip codes from color string.'))

        self.assertEqual(
            'hello world',
            strip_codes(
                Colr().red().bggreen().bright('hello world')
            ),
            msg=test_msg('Failed to strip codes from chained Colr string.'))

        self.assertEqual(
            'hello world',
            strip_codes(
                Colr('hello world').rainbow()
            ),
            msg=test_msg('Failed to strip codes from Colr.rainbow string.'))

    def test_trans(self):
        """ Translation functions should translate codes properly. """
        for v in self.conversions:
            # hex2*
            argset = (v['hexval'],)
            self.assertTupleEqual(
                v['rgb'],
                hex2rgb(*argset),
                msg=test_msg('Failed to translate.', *argset))

            argset = (v['hexval'],)
            self.assertEqual(
                v['code'],
                hex2term(*argset),
                msg=test_msg('Failed to translate.', *argset))

            argset = (v['hexval'],)
            self.assertEqual(
                v['hexval'],
                hex2termhex(*argset),
                msg=test_msg('Failed to translate.', *argset))

            # rgb2*
            argset = v['rgb']
            self.assertEqual(
                v['hexval'],
                rgb2hex(*argset),
                msg=test_msg('Failed to translate.', *argset))

            argset = v['rgb']
            self.assertEqual(
                v['code'],
                rgb2term(*argset),
                msg=test_msg('Failed to translate.', *argset))

            argset = v['rgb']
            self.assertEqual(
                v['hexval'],
                rgb2termhex(*argset),
                msg=test_msg('Failed to translate.', *argset))

            # term2*
            argset = (v['code'],)
            self.assertEqual(
                v['hexval'],
                term2hex(*argset),
                msg=test_msg('Failed to translate.', *argset))

            argset = (v['code'],)
            self.assertTupleEqual(
                v['rgb'],
                term2rgb(*argset),
                msg=test_msg('Failed to translate.', *argset))

            for hexval, termhex in self.termhex_close:
                argset = (hexval,)
                self.assertEqual(
                    termhex,
                    hex2termhex(*argset),
                    msg=test_msg('Failed on close match.', *argset))


if __name__ == '__main__':
    print('Running tests for Colr v. {}'.format(__version__))
    # unittest.main() calls sys.exit(status_code).
    unittest.main(argv=sys.argv, verbosity=2)  # type: ignore
