#!/usr/bin/env python3

""" test_base.py
    Unit tests for colr/base.py
    -Christopher Welborn 05-19-2019
"""

from colr.base import (
    ChainedBase,
    ChainedPart,
    CodePart,
    TextPart,
    get_code_indices,
    get_indices,
    get_indices_list,
)
from .testing_tools import (
    ColrTestCase,
    TestFileBytes,
)


class BaseTests(ColrTestCase):
    """ Tests for colr/base.py ChainedBase. """
    def test_add(self):
        """ __add__ should add ChainedBases, and raise TypeError for others.
        """
        cb = ChainedBase('')
        self.assertCallEqual(
            ChainedBase('test'),
            func=cb.__add__,
            args=('test', ),
            msg='Failed to add data to a ChainedBase.',
        )
        # radd
        self.assertCallEqual(
            ChainedBase('test'),
            func=cb.__radd__,
            args=('test', ),
            msg='Failed to radd data to a ChainedBase.',
        )

        with self.assertRaises(TypeError):
            cb + 25
        with self.assertRaises(TypeError):
            25 + cb

    def test_call(self):
        """ Calling a ChainedBase appends data to it. """
        cb = ChainedBase('')
        self.assertCallEqual(
            ChainedBase('test'),
            func=cb.__call__,
            args=('test', ),
            msg='Call did not add data.',
        )

    def test_center(self):
        """ Center justify should behave like str.just, without escape codes.
        """
        s = '\x1b[31mtesting\x1b[0m'
        cb = ChainedBase(s)
        self.assertCallEqual(
            ChainedBase('  {} '.format(s)),
            func=cb.center,
            args=(10, ),
            msg='Failed to properly center a ChainedBase.',
        )

    def test_format(self):
        """ __format__ should work, and raise errors where needed. """
        cb = ChainedBase('test')
        cases = {
            '{}': 'test',
            '{:}': 'test',
            '{:8}': 'test    ',
            '{:>8}': '    test',
            '{:<8}': 'test    ',
            '{:^8}': '  test  ',
        }
        for fmt, expected in cases.items():
            self.assertCallEqual(
                expected,
                func=fmt.format,
                args=(cb, ),
                msg='Failed to format ChainedBase.',
            )
        for badfmt in ('{:>BAD}', '{:BAD}'):
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
            # A slice that ends past the string.
            ((45, 99), ''),
            # A negative slice that ends before the string.
            ((-1, -3), ''),
            # Reversed slices.
            # A [::-n] slice.
            ((6, 6, -1), '\x1b[31mgnitset'),
            # A [6:0:-1] slice.
            ((6, 0, -1), '\x1b[31mgnitse'),
            # A slice that starts way outside the bounds.
            ((65, 0, -1), '\x1b[31mgnitse'),
            # A stepping slice less than -1.
            ((6, 0, -2), '\x1b[31mgist'),
        )
        for index, expected in cases:
            if isinstance(index, tuple):
                index = slice(*index)
            self.assertCallEqual(
                ChainedBase(expected),
                func=cb.__getitem__,
                args=(index, ),
                msg='Failed to ignore escape codes in __getitem__',
            )

        err_cases = (7, -8)
        for index in err_cases:
            raiser = self.assertRaises(
                IndexError,
                msg='Failed to raise for bad index: {!r}'.format(index)
            )
            with raiser:
                cb[index]
        index = 'wat'
        raiser = self.assertRaises(
            TypeError,
            msg='Failed to raise for bad index: {!r}'.format(index),
        )
        with raiser:
            # Index must be integer/slice.
            cb[index]

        index = slice(0, 2, 0)
        raiser = self.assertRaises(
            ValueError,
            msg='Failed to raise for 0 step.',
        )
        with raiser:
            # Step cannot be 0.
            cb[index]

    def test_index(self):
        """ index() should behave like self.data.index(). """
        cb = ChainedBase('\x1b[31mtesting\x1b[0m')
        cases = {
            '\x1b': 0,
            't': 5,
            'ing': 9,
        }
        for substr, expected in cases.items():
            self.assertCallEqual(
                expected,
                func=cb.index,
                args=(substr, ),
                msg='Failed to find index for known substr: {!r}'.format(substr)
            )

    def test_join(self):
        """ join() should join self.data for ChainedBases and strings. """
        cases = {
            ('a', ): 'a',
            ('a', 'b'): 'ab',
            (('a', 'b', 'c'), ): 'abc',
            (ChainedBase('ac'), ): 'ac',
            (ChainedBase('ac'), ChainedBase('bc')): 'acbc',
            ((ChainedBase('a'), ChainedBase('b'), ChainedBase('c')), ): 'abc',
            ((ChainedBase('ac'), 'b', ChainedBase('cc')), ): 'acbcc',
        }
        for joinargs, expected in cases.items():
            self.assertCallEqual(
                ChainedBase(expected),
                func=ChainedBase('').join,
                args=joinargs,
                msg='Failed to join strings correctly.',
            )

    def test_just(self):
        """ ljust()/rjust() should work around escape codes. """
        s = '\x1b[31mtest\x1b[0m'
        rjustcases = {
            0: '\x1b[31mtest\x1b[0m',
            8: '    \x1b[31mtest\x1b[0m',
        }
        for width, expected in rjustcases.items():
            self.assertCallEqual(
                ChainedBase(expected),
                func=ChainedBase(s).rjust,
                args=(width, ),
                msg='Failed to rjust ChainedBase correctly.',
            )
        ljustcases = {
            0: '\x1b[31mtest\x1b[0m',
            8: '\x1b[31mtest\x1b[0m    ',
        }
        for width, expected in ljustcases.items():
            self.assertCallEqual(
                ChainedBase(expected),
                func=ChainedBase(s).ljust,
                args=(width, ),
                msg='Failed to ljust ChainedBase correctly.',
            )
            # New text.
            self.assertCallEqual(
                ChainedBase(expected),
                func=ChainedBase().ljust,
                kwargs={'text': s, 'width': width},
                msg='Failed to ljust(text={!r}) ChainedBase correctly.'.format(
                    s,
                ),
            )

        # Bad width should raise ValueError.
        cb = ChainedBase(s)
        for func in (cb.ljust, cb.rjust):
            raiser = self.assertCallRaises(
                ValueError,
                func=func,
                kwargs={'width': 'BAD'},
                msg='Failed to raise in {} for bad `width` arg.'.format(
                    func.__name__,
                ),
            )
            with raiser:
                func(width='BAD')

        # Text squeezer should honor existing data.
        cb = ChainedBase('test')
        self.assertCallEqual(
            ChainedBase('testthis    '),
            func=cb.ljust,
            args=(12, ),
            kwargs={'text': 'this', 'squeeze': True},
            msg='Failed to "squeeze" old text and new text for ljust.',
        )
        self.assertCallEqual(
            ChainedBase('test    this'),
            func=cb.rjust,
            args=(12, ),
            kwargs={'text': 'this', 'squeeze': True},
            msg='Failed to "squeeze" old text and new text for rjust.',
        )

    def test_len(self):
        """ __len__ should return len(self.data). """
        # This is mostly here for test coverage.
        cb = ChainedBase('test')
        self.assertCallEqual(
            4,
            func=cb.__len__,
            msg='__len__ failed.',
        )

    def test_lstrip(self):
        """ lstrip() should act like str.lstrip(). """
        cases = {
            '  test': 'test',
            '\n\ttest': 'test',
            '\n\n\t\t  \n\n \t\ttest': 'test',
        }
        for s, expected in cases.items():
            self.assertCallEqual(
                ChainedBase(expected),
                func=ChainedBase(s).lstrip,
                msg='Failed to lstrip ChainedBase.',
            )

    def test_lt(self):
        """ __lt__ should operate on ChainedBases and strings. """
        a = ChainedBase('a')
        b = ChainedBase('b')
        self.assertLess(
            a,
            b,
            msg='__lt__ failed to recognize the proper order.'
        )
        self.assertLess(
            a,
            'c',
            msg='__lt__ failed to recognize the proper order for str.'
        )
        with self.assertRaises(TypeError):
            a < 5

    def test_mul(self):
        """ __mul__ should act like str.__mul__. """
        a = ChainedBase('a')
        self.assertEqual(
            a * 3,
            ChainedBase('aaa'),
            msg='Failed to multiply ChainedBase data.'
        )
        # rmul
        self.assertEqual(
            3 * a,
            ChainedBase('aaa'),
            msg='Failed to multiply ChainedBase data.'
        )

        with self.assertRaises(TypeError):
            # Non-int multiplier.
            a * 'wat'
        with self.assertRaises(TypeError):
            # Non-int rmultiplier.
            'wat' * a

    def test_parts(self):
        """ parts() should recognize code parts and text parts. """
        s = '\x1b[31mtesting\x1b[0m'
        cb = ChainedBase(s)
        parts = cb.parts()
        self.assertTrue(
            parts[0].is_code(),
            msg='First part should be a code part.',
        )
        self.assertFalse(
            parts[0].is_text(),
            msg='First part should be a code part.',
        )
        self.assertTrue(
            parts[1].is_text(),
            msg='Second part should be a text part.',
        )
        self.assertFalse(
            parts[1].is_code(),
            msg='Second part should be a text part.',
        )
        self.assertTrue(
            parts[2].is_code(),
            msg='Third part should be a code part.',
        )
        self.assertFalse(
            parts[2].is_text(),
            msg='Third part should be a code part.',
        )
        # __eq__
        codepart = CodePart(s, start=0, stop=5)
        self.assertEqual(
            parts[0],
            codepart,
            msg='CodePart doesn\'t match.'
        )
        textpart = TextPart(s, start=5, stop=12)
        self.assertEqual(
            parts[1],
            textpart,
            msg='TextPart doesn\'t match.'
        )
        # __eq__ should raise TypeError.
        raiser = self.assertRaises(
            TypeError,
            msg='Failed to raise for bad type.',
        )
        for badtype in (1, 'a', 0.3, [], {}):
            with raiser:
                codepart == badtype
            with raiser:
                textpart == badtype

        # __hash__
        self.assertEqual(
            hash(parts[0]),
            hash(codepart),
            msg='hash() failed on same code part.',
        )
        self.assertEqual(
            hash(parts[1]),
            hash(textpart),
            msg='hash() failed on same text part.',
        )

        # __repr__
        self.assertEqual(
            repr(codepart),
            'CodePart({!r})'.format(s[codepart.start:codepart.stop]),
            msg='repr() failed on CodePart.',
        )
        self.assertEqual(
            repr(textpart),
            'TextPart({!r})'.format(s[textpart.start:textpart.stop]),
            msg='repr() failed on TextPart.',
        )

        # ChainedPart cannot be used directly.
        raiser = self.assertRaises(
            NotImplementedError,
            msg='Failed to raise when using a ChainedPart directly.',
        )
        with raiser:
            ChainedPart('a', 0, 0).is_code()
        with raiser:
            ChainedPart('a', 0, 0).is_text()

    def test_rstrip(self):
        """ rstrip() should act like str.rstrip(). """
        cases = {
            'test  ': 'test',
            'test\n\t': 'test',
            'test\n\n\t\t  \n\n \t\t': 'test',
        }
        for s, expected in cases.items():
            self.assertCallEqual(
                ChainedBase(expected),
                func=ChainedBase(s).rstrip,
                msg='Failed to rstrip ChainedBase.',
            )

    def test_str(self):
        """ str() should return str(self.data). """
        # Mostly here for test coverage.
        cases = {
            'test': 'test',
            0: '0',
            1: '1',
            1.5: '1.5',
            tuple(): '()',
            tuple((1, 2)): '(1, 2)',
        }
        # str() called on a ChainedBase.
        for initarg, expected in cases.items():
            cb = ChainedBase(initarg)
            self.assertCallEqual(
                expected,
                func=str,
                args=(cb, ),
                msg='str() failed to return the proper string for {!r}.'.format(
                    initarg,
                ),
            )
        # ChainedBase.str method.
        for initarg, expected in cases.items():
            cb = ChainedBase(initarg)
            self.assertCallEqual(
                expected,
                func=cb.str,
                msg='str() failed to return the proper string for {!r}.'.format(
                    initarg,
                ),
            )
        # Initialized with False/True
        for val in (False, True):
            cb = ChainedBase(val)
            self.assertCallEqual(
                str(val),
                func=str,
                args=(cb, ),
                msg='str() failed to return the proper string for False.',
            )

    def test_strip(self):
        """ strip() should act like str.strip(). """
        cases = {
            '  test  ': 'test',
            '\n\ttest\n\t': 'test',
            '\n\n\t\t  \n\n \t\ttest\n\n\t\t  \n\n \t\t': 'test',
        }
        for s, expected in cases.items():
            self.assertCallEqual(
                ChainedBase(expected),
                func=ChainedBase(s).strip,
                msg='Failed to strip ChainedBase.',
            )
        charcases = (
            ('\x1b[31mtest\x1b[0m', '\x1b[31m', 'test\x1b[0m'),
            ('\x1b[31mtest\x1b[0m', '\x1b[0m', '\x1b[31mtest'),
            ('test', '\x1b[0m', 'test'),
        )
        for s, chars, expected in charcases:
            self.assertCallEqual(
                ChainedBase(expected),
                func=ChainedBase(s).strip,
                args=(chars, ),
                msg='Failed to strip escape codes properly.',
            )

    def test_write(self):
        """ write() should write self.data and then clear it. """
        cb = ChainedBase('test')
        file = TestFileBytes()
        cb.write(file=file)
        self.assertCallEqual(
            bytes(file),
            b'test',
            func=cb.write,
            kwargs={'file': file},
            msg='Failed to write to file object.',
        )
        self.assertEqual(
            cb,
            ChainedBase(''),
            msg='Failed to clear self.data after write() call.',
        )

        cb = ChainedBase('again')
        cb.write(file=file, end='\n')
        self.assertCallEqual(
            bytes(file),
            b'again\n',
            func=cb.write,
            kwargs={'file': file, 'end': '\n'},
            msg='Failed to write to file object with `end`.',
        )
        self.assertEqual(
            cb,
            ChainedBase(''),
            msg='Failed to clear self.data after write() call.',
        )

        cb = ChainedBase('with delay')
        cb.write(file=file, end='\n', delay=0.005)
        self.assertCallEqual(
            bytes(file),
            b'with delay\n',
            func=cb.write,
            kwargs={'file': file, 'end': '\n', 'delay': 0.005},
            msg='Failed to write to file object with delay.',
        )
        self.assertEqual(
            cb,
            ChainedBase(''),
            msg='Failed to clear self.data after write() call.',
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
            self.assertCallDictEqual(
                expected,
                func=get_code_indices,
                args=(s, ),
                msg='Failed to find code indices.',
            )

    def test_get_indices(self):
        """ get_indices should locate chars and escape codes. """
        cases = {
            # Empty string case.
            '': {},
            # No escape code case.
            'no codes': {i: c for i, c in enumerate('no codes')},
        }
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
            self.assertCallDictEqual(
                expected,
                func=get_indices,
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
            self.assertCallListEqual(
                expected,
                func=get_indices_list,
                args=(s, ),
                msg='Failed to find code and char indices.',
            )
