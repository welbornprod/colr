#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" test_colr.py
    Unit tests for colr.py.

    -Christopher Welborn 12-09-2015
"""

import random
import sys
import unittest

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
from colr.controls import Control
from colr.trans import (
    is_code,
    is_ext_code,
    is_rgb_code,
)

from .testing_tools import ColrTestCase

print('Testing Colr v. {}'.format(__version__))

# Save names in list format, for random.choice().
name_data_names = list(name_data)


class ColrTests(ColrTestCase):

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

    def has_closing_code(self, clr):
        """ Return True if a Colr() ends with a closing code. """
        return str(clr).endswith(closing_code)

    def test_add(self):
        """ Colrs should be added to each other, Controls, or strs. """
        types = {
            'Colr': Colr('Test', 'red'),
            'Control': Control().move_down(1),
            'str': 'testing',
        }
        for othername, other in types.items():
            clr = Colr('Testing', 'blue')
            try:
                newclr = clr + other
            except TypeError as ex:
                self.fail(
                    'Colr + {} should not raise a TypeError.'.format(
                        othername
                    ))
            else:

                self.assertIsInstance(
                    newclr,
                    Colr,
                    msg=(
                        'Adding {} to a Colr did not return a Colr.'
                    ).format(othername)
                )
                clr_str_result = ''.join((str(clr), str(other)))
                s = str(newclr)
                self.assertEqual(
                    clr_str_result,
                    s,
                    msg='str(Colr()) did not match.'
                )

    def test_bytes(self):
        """ bytes(Colr()) should encode self.data. """
        s = 'test'
        a = s.encode()
        b = bytes(Colr(s))
        self.assertEqual(a, b, msg='Encoded Colr is not the same.')

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
        for invalidargs in ((256, 0, 0), (-1, 0, 0)):
            with self.assertCallRaises(
                    InvalidColr,
                    func=Colr.rgb,
                    args=invalidargs,
                    msg='Failed to raise for invalid values.'):
                Colr().rgb(*invalidargs)
            with self.assertCallRaises(
                    InvalidColr,
                    func=Colr.b_rgb,
                    args=invalidargs,
                    msg='Failed to raise for invalid values.'):
                Colr().b_rgb(*invalidargs)

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

    def test_closingcode(self):
        """ The reset/closing code should be appended when necessary. """
        # No code should be appended.
        nocodeargs = (
            # No arguments given at all.
            tuple(),
            # Empty string with color arg.
            ('', 'red'),
            # None with no args.
            (None, ),
            # None with color args.
            (None, 'red'),
        )
        for argset in nocodeargs:
            self.assertCallFalse(
                self.has_closing_code(Colr(*argset)),
                func=Colr,
                args=argset,
                msg='Closing code should not be added.',
            )

        withcodeargs = {
            'justfore': {'fore': 'red'},
            'foreback': {'fore': 'red', 'back': 'blue'},
            'all': {'fore': 'red', 'back': 'blue', 'style': 'bright'},
            'justback': {'back': 'blue'},
            'juststyle': {'style': 'bright'},
        }
        for text, kwargs in withcodeargs.items():
            self.assertCallTrue(
                self.has_closing_code(Colr(text, **kwargs)),
                func=Colr,
                args=[text],
                kwargs=kwargs,
                msg='Failed to add closing code.',
            )

        # Normally falsey values should also append a code if color/style
        # args are given. Only `None` and `''` are exempt from this.
        for value in (False, 0):
            argset = (value, 'red')
            self.assertCallTrue(
                self.has_closing_code(Colr(*argset)),
                func=Colr,
                args=argset,
                msg='Failed to add closing code for falsey value.',
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
            self.assertCallEqual(
                val,
                fmtinfo['expected'],
                func=Colr.__format__,
                args=[fmt],
                msg='Colr.__format__ failed for valid format.',
            )

        # Colr.format should not break this.
        val = Colr('Test {:<10} Out', 'blue').format(Colr('This', 'red'))
        expected = (
            '\x1b[34mTest \x1b[31mThis\x1b[0m       Out\x1b[0m'
        )
        self.assertEqual(
            str(val),
            expected,
            msg='Colr(\'{}\').format(Colr()) breaks formatting!',
        )

    def test_hash(self):
        """ hash(Colr()) should return a unique hash for self.data. """
        a, b = hash(Colr('test', 'red')), hash(Colr('test', 'red'))
        self.assertCallEqual(
            a,
            b,
            func=hash,
            args=(a, ),
            otherargs=(b, ),
            msg='Mismatched hash values.',
        )
        b = hash(Colr('test', 'blue'))
        self.assertCallNotEqual(
            a,
            b,
            func=hash,
            args=(a, ),
            otherargs=(b, ),
            msg='Hash values should not match.',
        )

    def test_hex(self):
        """ Colr.color should recognize hex colors. """
        s = 'test'
        # Short/long hex values with/without hash should work.
        hexcodes = {
            'fff': 'short hex color without a hash',
            'ffffff': 'hex color without a hash',
            '#fff': 'short hex color',
            '#ffffff': 'hex color',
        }
        for hexcolr, desc in hexcodes.items():
            try:
                hexcolr = Colr(s, hexcolr)
            except InvalidColr as ex:
                self.fail('Failed to recognize {}.'.format(desc))
            termcolr = Colr(s, 231)
            self.assertEqual(
                hexcolr,
                termcolr,
                msg='Basic hex color did not match closest term color.',
            )

        # Hex values with rgb_mode=False should produce a close match.
        closematches = {
            'd7d7ff': 189,
            '008787': 30,
            'afd75f': 149,
            '000': 16,
            '000000': 16,
            'fff': 231,
            'ffffff': 231,
        }
        for hexval in sorted(closematches):
            closeterm = closematches[hexval]
            closetermcolr = Colr(s, closeterm)
            for hexvalue in (hexval, '#{}'.format(hexval)):
                hexcolr = Colr(s, hexvalue)
                self.assertCallEqual(
                    hexcolr,
                    closetermcolr,
                    func=Colr.color,
                    args=[s, hexvalue],
                    msg='Hex value is not the same output as close term.',
                )
                chainedhexcolr = Colr().hex(hexvalue, s, rgb_mode=False)
                self.assertCallEqual(
                    chainedhexcolr,
                    closetermcolr,
                    func=Colr.hex,
                    args=[hexval, s],
                    kwargs={'rgb_mode': False},
                    msg='Chained hex value is not the same as close term.'
                )

    def test_hex_rgb_mode(self):
        """ Colr.hex should use true color when rgb_mode is True. """
        s = 'test'
        # Hex values with rgb_mode=True should do a straight conversion.
        hexrgb = {
            'bada55': (186, 218, 85),
            'cafeba': (202, 254, 186),
            '858585': (133, 133, 133),
            '010203': (1, 2, 3),
        }
        for hexval, rgbval in hexrgb.items():
            hexcolr = Colr().hex(hexval, s, rgb_mode=True)
            rgbcolr = Colr().rgb(*rgbval, s)
            self.assertCallEqual(
                hexcolr,
                rgbcolr,
                func=Colr.hex,
                args=[hexval, s],
                kwargs={'rgb_mode': True},
                msg='Chained hex in rgb_mode did not match rgb.',
            )
            hexcolr = Colr(s).b_hex(hexval, rgb_mode=True)
            rgbcolr = Colr(s).b_rgb(*rgbval)
            self.assertCallEqual(
                hexcolr,
                rgbcolr,
                func=Colr.b_hex,
                args=[hexval],
                kwargs={'rgb_mode': True},
                msg='Chained b_hex in rgb_mode did not match b_rgb.',
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

        colrvals = {
            'Colr': Colr(s, fore='green', back='blue', style='bright'),
            'color func': color(s, fore='red', back='blue', style='bright'),
            'chained': Colr().red().bggreen().bright(s),
            'chained extended': Colr().f_55().b_55().bright(s),
            'chained rgb': Colr().rgb(25, 25, 25).b_rgb(55, 55, 55).bright(s),
            'Colr.rainbow': Colr(s).rainbow(),
            'Colr.rainbow rgb': Colr(s).rainbow(rgb_mode=True),
        }
        for desc, colrval in colrvals.items():
            self.assertCallEqual(
                s,
                strip_codes(colrval),
                func=strip_codes,
                args=[colrval],
                msg='Failed to strip codes from {} string.'.format(desc),
            )

    def test_stripped(self):
        """ Colr.stripped() should return strip_codes(Colr()). """
        data = 'This is a test.'
        c = Colr(data, fore='red', style='bright')
        datalen = len(data)
        stripped = c.stripped()
        strippedlen = len(stripped)
        self.assertCallEqual(
            datalen,
            strippedlen,
            func=c.stripped,
            msg='Stripped Colr has different length.',
        )
        self.assertCallEqual(
            data,
            stripped,
            func=c.stripped,
            msg='Stripped Colr has different content.',
        )

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


# # These are failing tests, to check the format for ColrTestCase messages.
class FailingTests(ColrTestCase):
    def test_fail_eq(self):
        """ Non-equal failures should print a pretty message. """
        # self.assertEqual(1, 2, msg='Nope, not equal.')
        # self.assertNotEqual(1, 1, msg='Oops, they are equal')
        # self.assertCallEqual(
        #     1,
        #     2,
        #     func=str,
        #     args=[1],
        #     otherargs=[2],
        #     kwargs={'testing': True},
        #     otherkwargs={'testing': True},
        #     msg='Nope, not equal.',
        # )
        # self.assertCallNotEqual(
        #     1,
        #     1,
        #     func=str,
        #     args=[1],
        #     kwargs={'testing': True},
        #     otherargs=[1],
        #     otherkwargs={'testing': True},
        #     msg='Oops, they are equal.',
        # )
        # self.assertCallTupleEqual(
        #     (1,),
        #     (2,),
        #     func=str,
        #     args=[1],
        #     kwargs={'testing': True},
        #     otherargs=[2],
        #     otherkwargs={'testing': True},
        #     msg='Nope, not equal.',
        # )
        # self.assertCallTrue(
        #     False,
        #     func=str,
        #     args=[1],
        #     kwargs={'testing': True},
        #     msg='Nope not true.',
        # )
        # self.assertCallFalse(
        #     True,
        #     func=str,
        #     args=[1],
        #     kwargs={'testing': True},
        #     msg='Nope not false.',
        # )
        # with self.assertCallRaises(
        #         ValueError,
        #         func=None,#str,
        #         args=[1],
        #         kwargs={'testing': True},
        #         msg='Nope, did not raise.'):
        #     pass


if __name__ == '__main__':
    # unittest.main() calls sys.exit(status_code).
    unittest.main(argv=sys.argv, verbosity=2)  # type: ignore
