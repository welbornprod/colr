#!/usr/bin/env python3

""" test_base.py
    Unit tests for colr/base.py
    -Christopher Welborn 05-19-2019
"""

from colr.base import (
    ChainedBase,
    get_code_indices,
    get_indices,
    get_indices_list,
)
from .testing_tools import ColrTestCase


class BaseTests(ColrTestCase):
    """ Tests for colr/base.py ChainedBase. """
    def test_add(self):
        """ __add__ should add ChainedBases, and raise TypeError for others.
        """
        cb = ChainedBase('')
        cb = cb + 'test'
        self.assertEqual(
            cb,
            ChainedBase('test'),
        )

        with self.assertRaises(TypeError):
            cb += 25

    def test_call(self):
        """ Calling a ChainedBase appends data to it. """
        cb = ChainedBase('')
        cb('test')
        self.assertEqual(
            cb,
            ChainedBase('test'),
            msg='Call did not add data.',
        )

    def test_format(self):
        """ __format__ should work, and raise errors where needed. """
        cb = ChainedBase('test')
        cases = {
            '{}': 'test',
            '{:>8}': '    test',
            '{:<8}': 'test    ',
        }
        for fmt, expected in cases.items():
            s = fmt.format(cb)
            self.assertCallEqual(
                s,
                expected,
                func=str.format,
                args=('test', ),
                msg='Failed to format ChainedBase.',
            )
        badfmt = '{:>BAD}'
        raiser = self.assertCallRaises(
            ValueError,
            func=str.format,
            args=(badfmt, ),
            msg='Failed to raise on bad width specifier.',
        )
        with raiser:
            badfmt.format(cb)

    def test_getitem(self):
        """ __getitem__ should navigate escape codes, and raise on errors.
        """
        cb = ChainedBase('\x1b[31mtesting\x1b[0m')
        cases = (
            (0, '\x1b[31mt'),
            (3, '\x1b[31mt'),
            ((2, ), '\x1b[31mte'),
            ((1, 3), '\x1b[31mes'),
            ((0, 6, 2), '\x1b[31mtsig'),
            # A [::n] slice.
            ((6, 6, 1), '\x1b[31mtesting'),
            # Reversed slices.
            # A [::-n] slice.
            ((6, 6, -1), '\x1b[31mgnitset'),
            ((6, 0, -1), '\x1b[31mgnitse'),
            ((6, 0, -2), '\x1b[31mgist'),
        )
        for index, expected in cases:
            if isinstance(index, tuple):
                index = slice(*index)
            self.assertCallEqual(
                cb[index],
                ChainedBase(expected),
                func=cb.__getitem__,
                args=(index, ),
                msg='Failed to ignore escape codes in __getitem__',
            )

        with self.assertRaises(IndexError):
            cb[7]
        with self.assertRaises(IndexError):
            cb[slice(7, 10)]

    def test_len(self):
        """ __len__ should return len(self.data). """
        # This is mostly here for test coverage.
        cb = ChainedBase('test')
        self.assertEqual(
            len(cb),
            4,
            msg='__len__ failed.',
        )


class BaseFunctionTests(ColrTestCase):
    """ Tests for colr/base.py helper functions. """
    def test_get_code_indices(self):
        """ get_code_indices should locate escape codes. """
        cases = {
            # None
            'no codes': {},
            # Start
            '\x1b[31m;one code': {0: '\x1b[31m'},
            # Start, End
            '\x1b[31mtest\x1b[0m': {0: '\x1b[31m', 9: '\x1b[0m'},
            # Start, Middle, End
            '\x1b[1m\x1b[47m\x1b[31mtest\x1b[0m': {
                0: '\x1b[1m',
                4: '\x1b[47m',
                9: '\x1b[31m',
                18: '\x1b[0m',
            },
        }
        for s, expected in cases.items():
            result = get_code_indices(s)
            self.assertCallDictEqual(
                result,
                expected,
                func=get_code_indices,
                args=(s, ),
                msg='Failed to find code indices.',
            )

    def test_get_indices(self):
        """ get_indices should locate chars and escape codes. """
        cases = {}
        # None
        cases['no codes'] = {i: c for i, c in enumerate('no codes')}
        # Start
        cases['\x1b[31m;one code'] = {0: '\x1b[31m'}
        cases['\x1b[31m;one code'].update(
            {i + 5: c for i, c in enumerate(';one code')}
        )
        # Start, End
        cases['\x1b[31mtest\x1b[0m'] = {0: '\x1b[31m', 9: '\x1b[0m'}
        cases['\x1b[31mtest\x1b[0m'].update(
            {i + 5: c for i, c in enumerate('test')}
        )
        # Start, Middle, End
        cases['\x1b[1m\x1b[47m\x1b[31mtest\x1b[0m'] = {
            0: '\x1b[1m',
            4: '\x1b[47m',
            9: '\x1b[31m',
            18: '\x1b[0m',
        }
        cases['\x1b[1m\x1b[47m\x1b[31mtest\x1b[0m'].update(
            {i + 14: c for i, c in enumerate('test')}
        )
        for s, expected in cases.items():
            result = get_indices(s)
            self.assertCallDictEqual(
                result,
                expected,
                func=get_code_indices,
                args=(s, ),
                msg='Failed to find code and char indices.',
            )

    def test_get_indices_list(self):
        """ get_indices_list should locate chars and escape codes. """
        cases = {}
        # None
        cases['no codes'] = list('no codes')
        # Start
        cases['\x1b[31m;one code'] = ['\x1b[31m']
        cases['\x1b[31m;one code'].extend(';one code')
        # Start, End
        cases['\x1b[31mtest\x1b[0m'] = [
            '\x1b[31m',
            't',
            'e',
            's',
            't',
            '\x1b[0m',
        ]

        # Start, Middle, End
        cases['\x1b[1m\x1b[47m\x1b[31mtest\x1b[0m'] = [
            '\x1b[1m',
            '\x1b[47m',
            '\x1b[31m',
            't',
            'e',
            's',
            't',
            '\x1b[0m',
        ]

        for s, expected in cases.items():
            result = get_indices_list(s)
            self.assertCallListEqual(
                result,
                expected,
                func=get_indices_list,
                args=(s, ),
                msg='Failed to find code and char indices.',
            )
