#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" test_colr.py
    Unit tests for colr.py.

    -Christopher Welborn 12-09-2015
"""

import inspect
import random
import sys
import unittest

from typing import Any, Callable, Mapping, Optional, no_type_check

from colr import (
    __version__,
    closing_code,
    color,
    Colr,
    ColorCode,
    fix_hex,
    hex2rgb,
    hex2term,
    hex2termhex,
    InvalidColr,
    name_data,
    rgb2hex,
    rgb2term,
    rgb2termhex,
    term2hex,
    term2rgb,
    strip_codes,
)
from colr.trans import (
    is_code,
    is_ext_code,
    is_rgb_code,
)

print('Testing Colr v. {}'.format(__version__))

# Save names in list format, for random.choice().
name_data_names = list(name_data)


def _equality_msg(op, a, b, msg=None):
    """ The ne_msg and eq_msg wrap this function to reduce code duplication.
        It builds a message suitable for an assert*Equal msg parameter.
    """
    # TODO: Just subclass/patch unittest.assertEqual and friends.
    return '\n'.join((
        '\n  {} {}'.format(
            Colr(repr(a), 'yellow'),
            Colr(op, 'red', style='bright')
        ),
        '  {}'.format(Colr(repr(b), 'green')),
        '\n{}'.format(Colr(msg, 'red')) if msg else '',
    ))


def call_msg(s: str, *args: Any, **kwargs: Mapping[Any, Any]):
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


def eq_msg(a, b, msg=None):
    """ Builds a message for assertNotEqual failure. """
    return _equality_msg('==', a, b, msg=msg)


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


def ne_msg(a, b, msg=None):
    """ Builds a better message for when assertEqual fails. """
    return _equality_msg('!=', a, b, msg=msg)


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

    def test_bytes(self):
        """ bytes(Colr()) should encode self.data. """
        s = 'test'
        a = s.encode()
        b = bytes(Colr(s))
        self.assertEqual(
            a,
            b,
            msg=ne_msg(a, b, msg='Encoded Colr is not the same.')
        )

    def test_chained_attr(self):
        """ Colr should allow chained color named methods. """
        # This will raise an AttributeError if the chained method is
        # not recognized.
        try:
            self.assertIsInstance(
                Colr().reset().bg_white(),
                Colr,
                msg='Failed to create Colr with chained methods.'
            )
            self.assertIsInstance(
                Colr().f_155().b_233(),
                Colr,
                msg='Failed to create Colr with chained methods.'
            )
        except AttributeError as ex:
            self.fail('Failed to recognize known chained method: {}'.format(
                ex
            ))

        # RGB codes should work.
        self.assertIsInstance(
            Colr().rgb(255, 255, 255),
            Colr,
            msg='Failed to create Colr with chained rgb method.'
        )

        self.assertIsInstance(
            Colr().b_rgb(255, 255, 255),
            Colr,
            msg='Failed to create Colr with chained b_rgb method.'
        )

        with self.assertRaises(InvalidColr):
            Colr().rgb(256, 0, 0)
        with self.assertRaises(InvalidColr):
            Colr().rgb(-1, 0, 0)
        # Invalid rgb codes should raise a InvalidColr.
        with self.assertRaises(InvalidColr):
            Colr().b_rgb(256, 0, 0)
        with self.assertRaises(InvalidColr):
            Colr().b_rgb(256, 0, 0)

    def test_color(self):
        """ Colr.color should accept valid color names/values. """
        # None of these should raise a InvalidColr.
        s = 'test'
        try:
            Colr(s, 'red')
            Colr(s, 16)
            Colr(s, (255, 0, 0))
        except InvalidColr as ex:
            self.fail(
                'InvalidColr raised for valid color name/value: {}'.format(
                    ex
                )
            )

        # Should get the correct code type for the correct value.
        self.assertTrue(
            is_code(str(Colr(' ', 'red')).split()[0])
        )
        self.assertTrue(
            is_ext_code(str(Colr(' ', 56)).split()[0])
        )
        self.assertTrue(
            is_rgb_code(str(Colr(' ', (0, 0, 255))).split()[0])
        )

        # Should raise InvalidColr on invalid color name/value.
        with self.assertRaises(InvalidColr):
            Colr(s, 'NOTACOLOR')
        with self.assertRaises(InvalidColr):
            Colr(s, 257)
        with self.assertRaises(InvalidColr):
            Colr(s, (-1, 0, 0))
        with self.assertRaises(InvalidColr):
            Colr(s, (257, 0, 0))

    def test_colorcode(self):
        """ ColorCode should properly translate codes. """

        for v in self.conversions:
            for code in v.values():
                argset = (code,)
                self.assertEqual(
                    v,
                    ColorCode(*argset).to_dict(),
                    msg=call_msg('Failed to translate.', *argset))

        for hexval, termhex in self.termhex_close:
            argset = (hexval,)
            self.assertEqual(
                termhex,
                ColorCode(*argset).hexval,
                msg=call_msg('Failed to find known close match.', *argset))

    def test_closingcode(self):
        """ The reset/closing code should be appended when necessary. """
        # No code appended.
        nocodeargs = {
            'no_args': tuple(),
            'empty_str': ('', 'red'),
            'none_no_args': (None, ),
            'none_with_args': (None, 'red'),
        }
        for argset in nocodeargs.values():
            self.assertFalse(
                str(Colr(*argset)).endswith(closing_code),
                msg=call_msg('Code should no be added.', *argset)
            )

        withcodeargs = {
            0: {'fore': 'red'},
            False: {'fore': 'red'},
            'justfore': {'fore': 'red'},
            'foreback': {'fore': 'red', 'back': 'blue'},
            'all': {'fore': 'red', 'back': 'blue', 'style': 'bright'},
            'justback': {'back': 'blue'},
            'juststyle': {'style': 'bright'},
        }
        for text, kwargs in withcodeargs.items():
            self.assertTrue(
                str(Colr(text, **kwargs)).endswith(closing_code),
                msg=call_msg('Failed to add closing code.', text, **kwargs),
            )

    def test_fix_hex(self):
        """ fix_hex should translate short-form hex strings. """
        for argset in (('#f',), ('#ffffffXX',), ('',)):
            with self.assertRaises(
                    ValueError,
                    msg=call_msg('Failed to raise.', *argset)):
                _ = fix_hex(*argset)  # noqa

        for argset, expected in (
            (('#fff',), 'ffffff'),
            (('##000',), '000000'),
            (('aaaaaa',), 'aaaaaa')
        ):
            self.assertEqual(
                expected,
                fix_hex(*argset),
                msg=call_msg('Failed to fix hex string.', *argset))

    def test_format(self):
        """ Colr.__format__ should use Colr.ljust and friends. """
        testformats = {
            '{:<10}': {
                'name': 'Left justify',
                'expected': '\x1b[31mTest\x1b[0m      ',
            },
            '{:>10}': {
                'name': 'Right justify',
                'expected': '      \x1b[31mTest\x1b[0m',
            },
            '{:^10}': {
                'name': 'Center justify',
                'expected': '   \x1b[31mTest\x1b[0m   ',
            },
            '{:X<10}': {
                'name': 'Left custom char justify',
                'expected': '\x1b[31mTest\x1b[0mXXXXXX',
            },
            '{:X>10}': {
                'name': 'Right custom char justify',
                'expected': 'XXXXXX\x1b[31mTest\x1b[0m',
            },
            '{:X^10}': {
                'name': 'Center custom char justify',
                'expected': 'XXX\x1b[31mTest\x1b[0mXXX',
            },
            # Colr nevers sees these formats, python takes care of it.
            # Still, I want to make sure there is never a regression.
            '{:<{w}}': {
                'name': 'Left dynamic justify',
                'kwargs': {'w': 10},
                'expected': '\x1b[31mTest\x1b[0m      ',
            },
            '{:>{w}}': {
                'name': 'Right dynamic justify',
                'kwargs': {'w': 10},
                'expected': '      \x1b[31mTest\x1b[0m',
            },
            '{:^{w}}': {
                'name': 'Center dynamic justify',
                'kwargs': {'w': 10},
                'expected': '   \x1b[31mTest\x1b[0m   ',
            },
            '{:{c}<{w}}': {
                'name': 'Left dynamic custom char justify',
                'kwargs': {'c': 'X', 'w': 10},
                'expected': '\x1b[31mTest\x1b[0mXXXXXX',
            },
            '{:{c}>{w}}': {
                'name': 'Right dynamic custom char justify',
                'kwargs': {'c': 'X', 'w': 10},
                'expected': 'XXXXXX\x1b[31mTest\x1b[0m',
            },
            '{:{c}^{w}}': {
                'name': 'Center dynamic custom char justify',
                'kwargs': {'c': 'X', 'w': 10},
                'expected': 'XXX\x1b[31mTest\x1b[0mXXX',
            },
            # Regular formats handled by str(self.data).__format__
            '{!r}': {
                'name': 'repr()',
                'expected': '\'\\x1b[31mTest\\x1b[0m\'',
            },
            '{!s}': {
                'name': 'str()',
                'expected': '\x1b[31mTest\x1b[0m',
            }

        }

        for fmt, fmtinfo in testformats.items():
            val = fmt.format(
                    Colr('Test', 'red'),
                    **(fmtinfo.get('kwargs', {}))
                )
            self.assertEqual(
                val,
                fmtinfo['expected'],
                msg=ne_msg(
                    val,
                    fmtinfo['expected'],
                    msg='{} failed for Colr.__format__({!r})'.format(
                        fmtinfo['name'],
                        fmt,
                    )
                )
            )

        # Colr.format should not break this.
        val = Colr('Test {:<10} Out', 'blue').format(Colr('This', 'red'))
        expected = (
            '\x1b[34mTest \x1b[31mThis\x1b[0m       Out\x1b[0m'
        )
        self.assertEqual(
            str(val),
            expected,
            msg=ne_msg(
                val,
                expected,
                msg='Colr(\'{}\').format(Colr()) breaks formatting!'
            )
        )

    def test_hash(self):
        """ hash(Colr()) should return a unique hash for self.data. """
        a, b = hash(Colr('test', 'red')), hash(Colr('test', 'red'))
        self.assertEqual(
            a,
            b,
            msg=ne_msg(a, b, msg='Mismatched hash values.')
        )
        a, b = hash(Colr('test', 'red')), hash(Colr('test', 'blue'))
        self.assertNotEqual(
            a,
            b,
            msg=eq_msg(a, b, msg='Hash values should not match.')
        )


    def test_hex2rgb(self):
        """ hex2rgb should translate well-formed codes, and raise on errors.
        """
        testargs = (('',), ('00 0000',))
        for argset in testargs:
            with self.assertRaises(
                    ValueError,
                    msg=call_msg('Failed to raise.', *argset)):
                _ = hex2rgb(*argset)

        argset = ('#f00',)
        kwset = {'allow_short': False}
        with self.assertRaises(
                ValueError,
                msg=call_msg('Failed to raise without.', *argset, **kwset)):
            _ = hex2rgb(*argset, **kwset)  # noqa

        argset = (' #FF0000',)
        self.assertTupleEqual(
            hex2rgb(*argset),
            (255, 0, 0),
            msg=call_msg('Failed to convert padded hex string.', *argset))

        argset = ('#f00',)
        kwset = {'allow_short': True}
        self.assertTupleEqual(
            hex2rgb(*argset, **kwset),
            (255, 0, 0),
            msg=call_msg(
                'Failed to convert short form hex string.', *argset, **kwset))

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

    def test_name_data(self):
        """ Colr should use name_data.names when all other style names fail.
        """
        for _ in range(5):
            knownname = random.choice(name_data_names)
            # If this doesn't raise a InvalidColr we should be okay.
            try:
                Colr('hello world', fore=knownname)
            except InvalidColr as ex:
                self.fail('Raised InvalidColr on known name: {}\n{}'.format(
                    knownname,
                    ex
                ))

    def test_name_data_attr(self):
        """ Colr should recognize fg_<name_data> and bg_<name_data> attrs. """
        # This will raise an AttributeError if name_data isn't working.
        self.assertIsInstance(
            Colr().f_aliceblue('test'),
            Colr,
            msg='Failed to create Colr from chained name_data method.'
        )
        self.assertIsInstance(
            Colr().b_antiquewhite('test'),
            Colr,
            msg='Failed to create Colr from chained name_data method.'
        )

    def test_strip_codes(self):
        """ strip_codes() should strip all color and reset codes. """
        s = '\n'.join((
            'This is a test of strip_codes.',
            'There should be none after stripping.'
        ))

        self.assertEqual(
            s,
            strip_codes(
                Colr(s, fore='green', back='blue', style='bright')
            ),
            msg=call_msg('Failed to strip codes from Colr string.')
        )

        self.assertEqual(
            s,
            strip_codes(
                color(s, fore='red', back='blue', style='bright')
            ),
            msg=call_msg('Failed to strip codes from color string.')
        )

        self.assertEqual(
            s,
            strip_codes(
                Colr().red().bggreen().bright(s)
            ),
            msg=call_msg('Failed to strip codes from chained Colr string.')
        )

        self.assertEqual(
            s,
            strip_codes(
                Colr().f_55().b_55().bright(s)
            ),
            msg=call_msg('Failed to strip codes from extended Colr string.')
        )

        self.assertEqual(
            s,
            strip_codes(
                Colr().rgb(25, 25, 25).b_rgb(55, 55, 55).bright(s)
            ),
            msg=call_msg('Failed to strip codes from rgb Colr string.')
        )

        self.assertEqual(
            s,
            strip_codes(
                Colr(s).rainbow()
            ),
            msg=call_msg('Failed to strip codes from Colr.rainbow string.')
        )
        self.assertEqual(
            s,
            strip_codes(
                Colr(s).rainbow(rgb_mode=True)
            ),
            msg=call_msg(
                'Failed to strip codes from Colr.rainbow rgb string.'
            )
        )

    def test_stripped(self):
        """ Colr.stripped() should return strip_codes(Colr()). """
        data = 'This is a test.'
        c = Colr(data, fore='red', style='bright')
        datalen = len(data)
        stripped = c.stripped()
        strippedlen = len(stripped)
        self.assertEqual(
            datalen,
            strippedlen,
            call_msg(
                'Stripped Colr has different length.',
                datalen,
                strippedlen,
            ),
        )
        self.assertEqual(
            data,
            stripped,
            call_msg(
                'Stripped Colr has different content.',
                data,
                stripped,
            ),
        )

    def test_trans(self):
        """ Translation functions should translate codes properly. """
        for v in self.conversions:
            # hex2*
            argset = (v['hexval'],)
            self.assertTupleEqual(
                v['rgb'],
                hex2rgb(*argset),
                msg=call_msg('Failed to translate.', *argset))

            argset = (v['hexval'],)
            self.assertEqual(
                v['code'],
                hex2term(*argset),
                msg=call_msg('Failed to translate.', *argset))

            argset = (v['hexval'],)
            self.assertEqual(
                v['hexval'],
                hex2termhex(*argset),
                msg=call_msg('Failed to translate.', *argset))

            # rgb2*
            argset = v['rgb']
            self.assertEqual(
                v['hexval'],
                rgb2hex(*argset),
                msg=call_msg('Failed to translate.', *argset))

            argset = v['rgb']
            self.assertEqual(
                v['code'],
                rgb2term(*argset),
                msg=call_msg('Failed to translate.', *argset))

            argset = v['rgb']
            self.assertEqual(
                v['hexval'],
                rgb2termhex(*argset),
                msg=call_msg('Failed to translate.', *argset))

            # term2*
            argset = (v['code'],)
            self.assertEqual(
                v['hexval'],
                term2hex(*argset),
                msg=call_msg('Failed to translate.', *argset))

            argset = (v['code'],)
            self.assertTupleEqual(
                v['rgb'],
                term2rgb(*argset),
                msg=call_msg('Failed to translate.', *argset))

            for hexval, termhex in self.termhex_close:
                argset = (hexval,)
                self.assertEqual(
                    termhex,
                    hex2termhex(*argset),
                    msg=call_msg('Failed on close match.', *argset))


if __name__ == '__main__':
    # unittest.main() calls sys.exit(status_code).
    unittest.main(argv=sys.argv, verbosity=2)  # type: ignore
