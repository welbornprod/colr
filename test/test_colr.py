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
    codes,
    color,
    Colr,
    get_codes,
    InvalidColr,
    name_data,
    strip_codes,
)
from colr.controls import Control
from colr.trans import (
    is_code,
    is_ext_code,
    is_rgb_code,
    rgb2hex,
)

from .testing_tools import ColrTestCase

# Save names in list format, for random.choice().
name_data_names = list(name_data)


class ColrTests(ColrTestCase):
    """ Tests for the colr.Colr object. """

    def example_args(self):
        """ Return a dict of {example-arg-type: example-args} to be used
            for testing Colr.
        """
        return {
            'fore': {
                'fore': self.random_color(),
            },
            'fore-back': {
                'fore': self.random_color(),
                'back': self.random_color(),
            },
            'fore-back-style': {
                'fore': self.random_color(),
                'back': self.random_color(),
                'style': self.random_style(),
            },
            'hex-fore': {
                'fore': self.random_hex(),
            },
            'hex-fore-back': {
                'fore': self.random_hex(),
                'back': self.random_hex(),
            },
            'hex-fore-back-style': {
                'fore': self.random_hex(),
                'back': self.random_hex(),
                'style': self.random_style(),
            },
            'rgb-fore': {
                'fore': self.random_rgb(),
            },
            'rgb-fore-back': {
                'fore': self.random_rgb(),
                'back': self.random_rgb(),
            },
            'rgb-fore-back-style': {
                'fore': self.random_rgb(),
                'back': self.random_rgb(),
                'style': self.random_style(),
            },
        }

    def has_closing_code(self, clr):
        """ Return True if a Colr() ends with a closing code. """
        try:
            lastcode = get_codes(clr)[-1]
        except IndexError:
            # No codes at all.
            return False
        return lastcode == closing_code

    def random_color(self):
        """ Return a random, but valid, fore/back argument from `codes`. """
        return random.choice(list(codes['fore']))

    def random_hex(self):
        """ Return a random, but valid, hex argument. """
        return rgb2hex(*self.random_rgb())

    def random_rgb(self):
        """ Return a random, but valid, RGB tuple arg. """
        return tuple(
            random.randint(0, 255)
            for _ in range(3)
        )

    def random_style(self):
        """ Return a random, valid, style argument from `codes`. """
        return random.choice(list(codes['style']))

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

    def test_getitem(self):
        """ Colr.__getitem__ should grab escape codes before and after. """
        # Simple string indexing, with color codes.
        exampleargs = self.example_args()
        # Reset styles should be kept at the start of a Colr.
        for stylename in codes['style']:
            exampleargs['style_{}'.format(stylename)] = {
                'fore': self.random_color(),
                'back': self.random_color(),
                'style': stylename,
            }
        for argtype, kwargs in exampleargs.items():
            index = random.randint(0, len(argtype) - 1)
            clr = Colr(argtype, **kwargs)
            clr_s = clr[index]
            self.assertCallEqual(
                clr_s,
                Colr(argtype[index], **kwargs),
                func=Colr.__getitem__,
                args=(clr, index, ),
                kwargs=kwargs,
                msg='Failed to keep color codes for __getitem__.',
            )

    def test_getitem_after_chained(self):
        """ Colr.__getitem__ on a chained Colr should keep escape codes. """
        # Indexing after chaining.
        clr = Colr('test', 'red').blue('this').rgb(25, 25, 25, 'thing')
        stripped = clr.stripped()
        self.assertGreater(
            len(stripped),
            6,
            msg='Stripped Colr was missing characters: {!r}'.format(stripped),
        )
        clr_s = clr[5]
        expected_clr = Colr(closing_code, fore='red').blue('h')

        self.assertCallEqual(
            clr_s,
            expected_clr,
            func=Colr.__getitem__,
            args=(clr, 5),
            msg='Failed to keep color codes for chained __getitem__.',
        )

    def test_getitem_slice(self):
        """ Colr.__getitem__ should handle slices/ranges. """
        clr = Colr('test', 'red').blue('this').rgb(0, 0, 0, 'thing')
        stripped = clr.stripped()
        self.assertGreater(
            len(stripped),
            6,
            msg='Stripped Colr was missing characters: {!r}'.format(stripped),
        )
        clr_s = clr[:]
        expected_clr = Colr(clr_s)

        self.assertCallEqual(
            clr_s,
            expected_clr,
            func=Colr.__getitem__,
            args=(clr, slice(None, None)),
            msg='Failed to keep color codes for __getitem__ range.',
        )

        clr_s = clr[4:8]
        expected_clr = Colr().red(closing_code).blue('this')

        self.assertCallEqual(
            clr_s,
            expected_clr,
            func=Colr.__getitem__,
            args=(clr, slice(4, 8)),
            msg='Failed to keep color codes for __getitem__ range.',
        )

        clr_s = clr[8:]
        expected_clr = (
            Colr(closing_code, fore='red')
            .blue(closing_code)
            .rgb(0, 0, 0, 'thing')
        )

        self.assertCallEqual(
            clr_s,
            expected_clr,
            func=Colr.__getitem__,
            args=(clr, slice(8)),
            msg='Failed to keep color codes for __getitem__ range.',
        )

        # These are actual examples from the docs.
        clr = Colr('test', 'blue')
        clr_s = clr[1:3]
        self.assertCallEqual(
            clr_s,
            Colr('es', 'blue'),
            func=Colr.__getitem__,
            args=(clr, slice(1, 3)),
            msg='failed to slice correctly.',
        )

        # Original Colr to slice up.
        clr = Colr('test', 'red').blue('this').rgb(25, 25, 25, 'thing')
        examples = (
            # Integer index with clr[5].
            (
                5,
                Colr(closing_code, fore='red').blue('h'),
            ),
            # All (copy) with clr[:], except closing_codes aren't needed.
            (
                slice(None, None),
                clr,
            ),
            # Starting index with clr[8:]
            (
                slice(8, None),
                (
                    Colr(closing_code, fore='red')
                    .blue(closing_code)
                    .rgb(25, 25, 25, 'thing')
                ),
            ),
        )

        for sliceobj, expected in examples:
            slicerepr = str(sliceobj)
            if isinstance(sliceobj, slice):
                slicerepr = '{}:{}:{}'.format(
                    *sliceobj.indices(len(clr.stripped()))
                )
            self.assertCallEqual(
                clr[sliceobj],
                expected,
                func=Colr.__getitem__,
                args=(clr, sliceobj),
                msg='Failed to slice correctly with Colr()[{}] ({!r})'.format(
                    slicerepr,
                    sliceobj,
                ),
            )

    def test_gradient(self):
        """ Colr.gradient should recognize names and rainbow offsets. """
        valid_names = list(Colr.gradient_names)
        valid_names.extend(range(1, 254))
        valid_names.extend((False, True, None, '', 0, 1.2))
        for valid_name in valid_names:
            try:
                Colr('test').gradient(name=valid_name)
            except ValueError:
                self.fail(self.call_msg(
                    'Colr.gradient failed on a known name.',
                    valid_name,
                    func=Colr().gradient,
                ))
        invalid_names = ('block', 'bash', 'berry')
        for invalid_name in invalid_names:
            try:
                Colr('test').gradient(name=invalid_name)
            except ValueError:
                pass
            else:
                self.fail(self.call_msg(
                    'Failed to raise on invalid name.',
                    invalid_name,
                    func=Colr().gradient,
                ))

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

    def test_lstrip(self):
        """ Colr.lstrip should strip characters and return another Colr. """
        teststrings = (
            (None, '   test', 'test'),
            (' ', '    test', 'test'),
            ('X', 'XXXXtest', 'test'),
            ('Xx', 'XXxxXxxXxXtest', 'test'),
            (
                closing_code,
                ''.join((closing_code, 'test')),
                'test'
            ),
        )
        for chars, s, expected in teststrings:
            clr = Colr(s)
            stripped = clr.lstrip(chars)
            self.assertCallEqual(
                str(stripped),
                expected,
                func=Colr.lstrip,
                args=(clr, ),
                kwargs={'chars': chars},
                msg='Failed to strip characters.',
            )
            self.assertCallIsInstance(
                stripped,
                Colr,
                func=Colr.lstrip,
                args=(clr, ),
                kwargs={'chars': chars},
                msg='Did not return a Colr instance.',
            )
        testcolrs = []
        for chars, s, expected in teststrings:
            if chars == closing_code:
                # Cannot strip closing code from a colorized closing_code.
                continue
            for argtype, kwargs in self.example_args().items():
                testcolrs.append(
                    (chars, Colr(s, **kwargs), Colr(expected, **kwargs))
                )

        for chars, clr, expected in testcolrs:
            stripped = clr.lstrip(chars)
            self.assertCallEqual(
                stripped,
                expected,
                func=Colr.lstrip,
                args=(clr, ),
                kwargs={'chars': chars},
                msg='Failed to strip characters from colorized Colr.',
            )

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

    def test_rstrip(self):
        """ Colr.rstrip should strip characters and return another Colr. """
        teststrings = (
            (None, 'test   ', 'test'),
            (' ', 'test    ', 'test'),
            ('X', 'testXXXX', 'test'),
            ('Xx', 'testXXxxXxxXxX', 'test'),
            (
                closing_code,
                ''.join(('test', closing_code)),
                'test'
            ),
        )
        for chars, s, expected in teststrings:
            clr = Colr(s)
            stripped = clr.rstrip(chars)
            self.assertCallEqual(
                str(stripped),
                expected,
                func=Colr.rstrip,
                args=(clr, ),
                kwargs={'chars': chars},
                msg='Failed to strip characters.',
            )
            self.assertCallIsInstance(
                stripped,
                Colr,
                func=Colr.rstrip,
                args=(clr, ),
                kwargs={'chars': chars},
                msg='Did not return a Colr instance.',
            )
        testcolrs = []
        for chars, s, expected in teststrings:
            if chars == closing_code:
                # Cannot strip closing code from a colorized closing_code.
                continue
            for argtype, kwargs in self.example_args().items():
                testcolrs.append(
                    (chars, Colr(s, **kwargs), Colr(expected, **kwargs))
                )

        for chars, clr, expected in testcolrs:
            stripped = clr.rstrip(chars)
            self.assertCallEqual(
                stripped,
                expected,
                func=Colr.rstrip,
                args=(clr, ),
                kwargs={'chars': chars},
                msg='Failed to strip characters from colorized Colr.',
            )

    def test_strip(self):
        """ Colr.strip should strip characters and return another Colr. """
        teststrings = (
            (None, '    test   ', 'test'),
            (' ', '    test    ', 'test'),
            ('X', 'XXXXtestXXXX', 'test'),
            ('Xx', 'XxxXXxXxXXxtestXXxxXxxXxX', 'test'),
            (
                closing_code,
                ''.join((closing_code, 'test', closing_code)),
                'test'
            ),
        )
        for chars, s, expected in teststrings:
            clr = Colr(s)
            stripped = clr.strip(chars)
            self.assertCallEqual(
                str(stripped),
                expected,
                func=Colr.strip,
                args=(clr, ),
                kwargs={'chars': chars},
                msg='Failed to strip characters.',
            )
            self.assertCallIsInstance(
                stripped,
                Colr,
                func=Colr.strip,
                args=(clr, ),
                kwargs={'chars': chars},
                msg='Did not return a Colr instance.',
            )
        testcolrs = []
        for chars, s, expected in teststrings:
            if chars == closing_code:
                # Cannot strip closing code from a colorized closing_code.
                continue
            for argtype, kwargs in self.example_args().items():
                testcolrs.append(
                    (chars, Colr(s, **kwargs), Colr(expected, **kwargs))
                )

        for chars, clr, expected in testcolrs:
            stripped = clr.strip(chars)
            self.assertCallEqual(
                stripped,
                expected,
                func=Colr.strip,
                args=(clr, ),
                kwargs={'chars': chars},
                msg='Failed to strip characters from colorized Colr.',
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


if __name__ == '__main__':
    print('Testing Colr v. {}'.format(__version__))
    # unittest.main() calls sys.exit(status_code).
    unittest.main(argv=sys.argv, verbosity=2)  # type: ignore
