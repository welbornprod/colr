#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" test_progress.py
    Unit tests for colr/progress.py.

    -Christopher Welborn 3-16-2017
"""

import sys
import unittest

from colr import (
    __version__,
    Colr,
)
from colr.progress import (
    AnimatedProgress,
    Frames,
    FrameSet,
    StaticProgress,
    WriterProcess,
    WriterProcessBase,
)

from .testing_tools import (
    ColrTestCase,
    TestFile,
)

# Green has a problem with initializing a Process with a Value attached:
GREEN_ISSUE_URL = 'https://github.com/CleanCut/green/issues/154'
# Until this issue is resolved, the WriterProcessBase subclasses can't be
# tested. All of this can be deleted when the issue is resolved.
GREEN_ISSUE_RESOLVED = False
GREEN_ISSUE_MSG = 'Waiting for resolution for: {}'.format(GREEN_ISSUE_URL)


print('Testing Colr.Progress v. {}'.format(__version__))


class FrameSetTests(ColrTestCase):

    @staticmethod
    def iterable_str(iterable):
        """ Shortcut for ''.join(str(x) for x in iterable). """
        return ''.join(str(x) for x in iterable)

    def test_add(self):
        """ Controls should be added to each other, Colrs, or strs. """
        types = {
            'FrameSet': FrameSet(('a', 'b', 'c')),
            'list': ['a', 'b', 'c'],
            'tuple': ('a', 'b', 'c'),
        }
        for othername, other in types.items():
            fset = FrameSet(('1', '2', '3'))
            try:
                newfset = fset + other
            except TypeError as ex:
                self.fail(
                    'FrameSet + {} should not raise a TypeError.'.format(
                        othername
                    ))
            else:

                self.assertIsInstance(
                    newfset,
                    FrameSet,
                    msg=(
                        'Adding {} to a FrameSet did not return a FrameSet.'
                    ).format(othername)
                )
                ctl_str_result = ''.join((
                    self.iterable_str(fset),
                    self.iterable_str(other),
                ))
                s = str(newfset)
                self.assertEqual(
                    ctl_str_result,
                    s,
                    msg='str(FrameSet()) did not match.'
                )

    def test_bytes(self):
        """ bytes(FrameSet()) should encode self.data. """
        s = 'test'
        a = s.encode()
        b = bytes(FrameSet(s))
        self.assertEqual(a, b, msg='Encoded FrameSet is not the same.')

    def test_hash(self):
        """ hash(FrameSet()) should return a unique hash for self.data. """
        a, b = hash(FrameSet('test')), hash(FrameSet('test'))
        self.assertCallEqual(
            a,
            b,
            func=hash,
            args=[a],
            otherargs=[b],
            msg='Mismatched hash values.',
        )
        b = hash(FrameSet('another'))
        self.assertCallNotEqual(
            a,
            b,
            func=hash,
            args=[a],
            otherargs=[b],
            msg='Hash values should not match.',
        )

    def test_init(self):
        """ FrameSets can be initialized with several types of iterables. """
        def generator(s):
            yield from s

        teststr = 'test'
        types = (
            teststr,
            list(teststr),
            tuple(teststr),
            generator(teststr),
        )
        for itertype in types:
            self.assertCallIsInstance(
                FrameSet(itertype),
                FrameSet,
                func=FrameSet,
                args=(itertype, ),
                msg='Failed to initialize from a good iterable ({}).'.format(
                    type(itertype).__name__,
                ),
            )


@unittest.skipUnless(GREEN_ISSUE_RESOLVED, GREEN_ISSUE_MSG)
class AnimatedProgressTests(ColrTestCase):
    """ Tests for colr.progress.AnimatedProgress. """

    def test_frame_delay(self):
        """ FrameSet delays should be honored, unless overridden. """

        fset = FrameSet('test', name='test_frames', delay=0.7)
        p = AnimatedProgress(
            'message',
            frames=fset,
            file=TestFile(),
        )

        self.assertAlmostEqual(
            p.delay,
            fset.delay,
            delta=0.1,
            msg='FrameSet delay was not honored.',
        )

        # Overridden frame delays:
        manual_delay = 0.9
        p_manual = AnimatedProgress(
            'message',
            frames=fset,
            delay=manual_delay,
            file=TestFile(),
        )

        self.assertAlmostEqual(
            p_manual.delay,
            manual_delay,
            delta=0.1,
            msg='FrameSet delay was not overridden.',
        )

        import multiprocessing as mp
        for finalizer in mp.util._finalizer_registry.values():
            for arg in finalizer._args:
                addr = getattr(arg, 'address', None)
                if addr is None:
                    continue
                print('ADDRESS: {}'.format(addr))


@unittest.skipUnless(GREEN_ISSUE_RESOLVED, GREEN_ISSUE_MSG)
class WriterProcessTests(ColrTestCase):
    """ Tests for the WriterProcess. """
    def test_init(self):
        p = WriterProcess('test', file=TestFile())
        # Redundant test, checking green's weird FileNotFoundError.
        self.assertIsInstance(
            p,
            WriterProcess,
            msg='Failed to initialize WriterProcess.',
        )


@unittest.skipUnless(GREEN_ISSUE_RESOLVED, GREEN_ISSUE_MSG)
class WriterProcessBaseTests(ColrTestCase):
    """ Tests for the WriterProcessBase. """
    def test_init(self):
        from multiprocessing import Lock, Queue, Value
        from ctypes import c_bool, c_double

        p = WriterProcessBase(
            Queue(maxsize=1),
            Lock(),
            Value(c_bool, True),
            Value(c_double, 0),
            Value(c_double, 0),
            file=TestFile(),
        )
        # Redundant test, checking green's weird FileNotFoundError.
        self.assertIsInstance(
            p,
            WriterProcessBase,
            msg='Failed to initialize WriterProcessBase.',
        )


# Minimum test case for GREEN_ISSUE_URL.
DEBUGGING_GREEN_ISSUE = True


@unittest.skipUnless(DEBUGGING_GREEN_ISSUE, 'No need to run a non-test.')
class ProcessTests(unittest.TestCase):
    """ Debugging FileNotFoundError when using a multiprocessing.Value. """

    def test_process(self):

        def func(v):
            v.value = 1.23
            print(v.value)
        import multiprocessing
        from ctypes import c_double

        val = multiprocessing.Value(c_double, 0)
        multiprocessing.Process(
            target=func,
            args=(val, )
        )


if __name__ == '__main__':
    # unittest.main() calls sys.exit(status_code).
    unittest.main(argv=sys.argv, verbosity=2)  # type: ignore
