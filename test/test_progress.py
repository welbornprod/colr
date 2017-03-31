#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" test_progress.py
    Unit tests for colr/progress.py.

    -Christopher Welborn 3-16-2017
"""

import sys
import unittest
from ctypes import c_bool, c_double
from multiprocessing import Lock, Queue, Value
from multiprocessing.queues import Empty
from time import sleep

from colr import (
    __version__,
    Colr,
)
from colr.progress import (
    AnimatedProgress,
    Bars,
    BarSet,
    Frames,
    FrameSet,
    ProgressBar,
    ProgressTimedOut,
    StaticProgress,
    WriterProcess,
    WriterProcessBase,
)

from .testing_tools import (
    ColrTestCase,
    TestFile,
)


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

    def test_timeout(self):
        """ AnimatedProgress should throw ProgressTimedOut when timed out. """
        timeout = 0.25
        sleepsecs = timeout * 2
        p = AnimatedProgress('test', timeout=timeout, file=TestFile())
        p.start()
        while sleepsecs > 0:
            sleep(timeout)
            sleepsecs -= timeout
            if p.exception and not isinstance(p.exception, ProgressTimedOut):
                self.fail(
                    'Error was raised, but not ProgressTimedOut:\n{}'.format(
                        p.tb_lines
                    )
                )
        try:
            p.stop()
        except ProgressTimedOut:
            pass
        else:
            self.fail('Failed to raise ProgressTimedOut.')


class BarsTests(ColrTestCase):
    """ Tests for the Bars class. """

    def test_get_by_name(self):
        """ Bars.get_by_name() should return known BarSets. """
        for name in ('blocks', ):
            try:
                blocks = Bars.get_by_name(name)
            except ValueError:
                self.fail(
                    self.call_msg(
                        'Failed to get known name.',
                        name,
                        func=Bars.get_by_name,
                    )
                )
            self.assertCallIsInstance(
                blocks,
                BarSet,
                func=Bars.get_by_name,
                args=(name, ),
                msg='Returned non-BarSet object.',
            )

    def test_names(self):
        """ Bars.names() sould return a non-empty list of names. """
        names = Bars.names()
        nameslen = len(names)
        self.assertCallNotEqual(
            nameslen,
            0,
            func=len,
            args=(names),
            msg='Bars.names() returned an empty list.',
        )

    def test_register(self):
        """ Bars.register should register new BarSets. """
        name = 'test_barset'
        fset = BarSet('abc', name=name)
        Bars.register(fset)
        if getattr(Bars, name, None) is None:
            self.fail(
                self.call_msg(
                    'Failed to register BarSet attribute.',
                    name,
                    func=Bars.register,
                )
            )


class BarSetTests(ColrTestCase):
    """ Tests for the BarSet object. """
    @staticmethod
    def iterable_str(iterable):
        """ Shortcut for ''.join(str(x) for x in iterable). """
        return ''.join(str(x) for x in iterable)

    def test_add(self):
        """ Controls should be added to each other, Colrs, or strs. """
        types = {
            'BarSet': BarSet(('a', 'b', 'c')),
            'list': ['a', 'b', 'c'],
            'tuple': ('a', 'b', 'c'),
        }
        for othername, other in types.items():
            fset = BarSet(('1', '2', '3'))
            try:
                newfset = fset + other
            except TypeError as ex:
                self.fail(
                    'BarSet + {} should not raise a TypeError.'.format(
                        othername
                    ))
            else:

                self.assertIsInstance(
                    newfset,
                    BarSet,
                    msg=(
                        'Adding {} to a BarSet did not return a BarSet.'
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
                    msg='str(BarSet()) did not match.'
                )

    def test_as_colr(self):
        """ BarSet.as_colr() should Colrize all frames. """
        fset = BarSet('abc', name='test_frameset')
        colrfset = fset.as_colr(fore='red')
        fsetlen = len(fset)
        colrfsetlen = len(colrfset)
        self.assertCallEqual(
            colrfsetlen,
            fsetlen,
            func=len,
            args=(colrfsetlen, ),
            otherargs=(fsetlen, ),
            msg='Colorized BarSet length was mismatched.',
        )
        for item in colrfset:
            self.assertCallIsInstance(
                item,
                Colr,
                func=BarSet.as_colr,
                args=(item, ),
                msg='Colorized BarSet item is not a Colr.',
            )

    def test_as_gradient(self):
        """ BarSet.as_gradient() should Colrize all frames. """
        fset = BarSet('abc', name='test_frameset')
        colrfset = fset.as_gradient(name='red')
        fsetlen = len(fset)
        colrfsetlen = len(colrfset)
        self.assertCallEqual(
            colrfsetlen,
            fsetlen,
            func=len,
            args=(colrfsetlen, ),
            otherargs=(fsetlen, ),
            msg='Colorized BarSet length was mismatched.',
        )
        for item in colrfset:
            self.assertCallIsInstance(
                item,
                Colr,
                func=BarSet.as_gradient,
                args=(item, ),
                msg='Colorized BarSet item is not a Colr.',
            )

    def test_as_rainbow(self):
        """ BarSet.as_rainbow() should Colrize all frames. """
        fset = BarSet('abc', name='test_frameset')
        colrfset = fset.as_rainbow()
        fsetlen = len(fset)
        colrfsetlen = len(colrfset)
        self.assertCallEqual(
            colrfsetlen,
            fsetlen,
            func=len,
            args=(colrfsetlen, ),
            otherargs=(fsetlen, ),
            msg='Colorized BarSet length was mismatched.',
        )
        for item in colrfset:
            self.assertCallIsInstance(
                item,
                Colr,
                func=BarSet.as_rainbow,
                args=(item, ),
                msg='Colorized BarSet item is not a Colr.',
            )

    def test_bytes(self):
        """ bytes(BarSet()) should encode self.data. """
        s = 'test'
        a = s.encode()
        b = bytes(BarSet(s))
        self.assertEqual(a, b, msg='Encoded BarSet is not the same.')

    def test_from_str(self):
        """ BarSet.from_str should create a set of bar frames. """
        s = 'abcd'
        name = 'test_bars'
        expected = BarSet(
            (
                'a   ',
                'ab  ',
                'abc ',
                'abcd',
            ),
            name=name,
        )
        bset = BarSet.from_str(s, name=name)
        self.assertEqual(
            bset,
            expected,
            msg='Failed to create BarSet from str.'
        )

    def test_hash(self):
        """ hash(BarSet()) should return a unique hash for self.data. """
        a, b = hash(BarSet('test')), hash(BarSet('test'))
        self.assertCallEqual(
            a,
            b,
            func=hash,
            args=[a],
            otherargs=[b],
            msg='Mismatched hash values.',
        )
        b = hash(BarSet('another'))
        self.assertCallNotEqual(
            a,
            b,
            func=hash,
            args=[a],
            otherargs=[b],
            msg='Hash values should not match.',
        )

    def test_init(self):
        """ BarSets can be initialized with several types of iterables. """
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
                BarSet(itertype),
                BarSet,
                func=BarSet,
                args=(itertype, ),
                msg='Failed to initialize from a good iterable ({}).'.format(
                    type(itertype).__name__,
                ),
            )


class FramesTests(ColrTestCase):
    """ Tests for the Frames class. """

    def test_get_by_name(self):
        """ Frames.get_by_name() should return known FrameSets. """
        for name in ('dots', 'dots_blue', 'dots_chase_lightred'):
            try:
                dots = Frames.get_by_name(name)
            except ValueError:
                self.fail(
                    self.call_msg(
                        'Failed to get known name.',
                        name,
                        func=Frames.get_by_name,
                    )
                )
            self.assertCallIsInstance(
                dots,
                FrameSet,
                func=Frames.get_by_name,
                args=(name, ),
                msg='Returned non-FrameSet object.',
            )

    def test_names(self):
        """ Frames.names() sould return a non-empty list of names. """
        names = Frames.names()
        nameslen = len(names)
        self.assertCallNotEqual(
            nameslen,
            0,
            func=len,
            args=(names),
            msg='Frames.names() returned an empty list.',
        )

    def test_register(self):
        """ Frames.register should register new FrameSets. """
        name = 'test_frameset'
        fset = FrameSet('abc', name=name)
        Frames.register(fset)
        if getattr(Frames, name, None) is None:
            self.fail(
                self.call_msg(
                    'Failed to register FrameSet attribute.',
                    name,
                    func=Frames.register,
                )
            )


class FrameSetTests(ColrTestCase):
    """ Tests for the FrameSet object. """
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

    def test_as_colr(self):
        """ FrameSet.as_colr() should Colrize all frames. """
        fset = FrameSet('abc', name='test_frameset')
        colrfset = fset.as_colr(fore='red')
        fsetlen = len(fset)
        colrfsetlen = len(colrfset)
        self.assertCallEqual(
            colrfsetlen,
            fsetlen,
            func=len,
            args=(colrfsetlen, ),
            otherargs=(fsetlen, ),
            msg='Colorized FrameSet length was mismatched.',
        )
        for item in colrfset:
            self.assertCallIsInstance(
                item,
                Colr,
                func=FrameSet.as_colr,
                args=(item, ),
                msg='Colorized FrameSet item is not a Colr.',
            )

    def test_as_gradient(self):
        """ FrameSet.as_gradient() should Colrize all frames. """
        fset = FrameSet('abc', name='test_frameset')
        colrfset = fset.as_gradient(name='red')
        fsetlen = len(fset)
        colrfsetlen = len(colrfset)
        self.assertCallEqual(
            colrfsetlen,
            fsetlen,
            func=len,
            args=(colrfsetlen, ),
            otherargs=(fsetlen, ),
            msg='Colorized FrameSet length was mismatched.',
        )
        for item in colrfset:
            self.assertCallIsInstance(
                item,
                Colr,
                func=FrameSet.as_gradient,
                args=(item, ),
                msg='Colorized FrameSet item is not a Colr.',
            )

    def test_as_rainbow(self):
        """ FrameSet.as_rainbow() should Colrize all frames. """
        fset = FrameSet('abc', name='test_frameset')
        colrfset = fset.as_rainbow()
        fsetlen = len(fset)
        colrfsetlen = len(colrfset)
        self.assertCallEqual(
            colrfsetlen,
            fsetlen,
            func=len,
            args=(colrfsetlen, ),
            otherargs=(fsetlen, ),
            msg='Colorized FrameSet length was mismatched.',
        )
        for item in colrfset:
            self.assertCallIsInstance(
                item,
                Colr,
                func=FrameSet.as_rainbow,
                args=(item, ),
                msg='Colorized FrameSet item is not a Colr.',
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


class ProgressBarTests(ColrTestCase):
    """ Tests for the ProgressBar object. """
    def test_init(self):
        """ ProgressBar should initialize. """
        p = ProgressBar('test', file=TestFile())
        self.assertCallIsInstance(
            p,
            ProgressBar,
            func=ProgressBar,
            args=('test', ),
            msg='Failed to initialize ProgressBar from good arguments.',
        )

    def test_timeout(self):
        """ ProgressBar should throw ProgressTimedOut when timed out. """
        timeout = 0.25
        sleepsecs = timeout * 2
        p = ProgressBar('test', timeout=timeout, file=TestFile())
        p.start()
        while sleepsecs > 0:
            sleep(timeout)
            sleepsecs -= timeout
            if p.exception and not isinstance(p.exception, ProgressTimedOut):
                self.fail(
                    'Error was raised, but not ProgressTimedOut:\n{}'.format(
                        p.tb_lines
                    )
                )
        try:
            p.stop()
        except ProgressTimedOut:
            pass
        else:
            self.fail('Failed to raise ProgressTimedOut.')


class StaticProgressTests(ColrTestCase):
    """ Tests for the StaticProgress object. """
    def test_init(self):
        """ StaticProgress should initialize. """
        p = StaticProgress('test', file=TestFile())
        self.assertIsInstance(
            p,
            StaticProgress,
            msg='Failed to initialize StaticProgress',
        )

    def test_timeout(self):
        """ StaticProgress should throw ProgressTimedOut when timed out. """
        timeout = 0.25
        sleepsecs = timeout * 2
        p = StaticProgress('test', timeout=timeout, file=TestFile())
        p.start()
        while sleepsecs > 0:
            sleep(timeout)
            sleepsecs -= timeout
        try:
            p.stop()
        except ProgressTimedOut:
            pass
        else:
            self.fail('Failed to raise ProgressTimedOut.')


class WriterProcessTests(ColrTestCase):
    """ Tests for the WriterProcess. """
    def test_init(self):
        """ WriterProcess should initialize. """
        p = WriterProcess('test', file=TestFile())
        # Redundant test, checking green's weird FileNotFoundError.
        self.assertIsInstance(
            p,
            WriterProcess,
            msg='Failed to initialize WriterProcess.',
        )

    def test_timeout(self):
        """ WriterProcess should throw ProgressTimedOut when timed out. """
        timeout = 0.25
        sleepsecs = timeout * 2
        p = WriterProcess('test', timeout=timeout, file=TestFile())
        p.start()
        sleep(0.1)
        while sleepsecs > 0:
            sleep(timeout)
            sleepsecs -= timeout
        p.stop()
        try:
            exc, tb_lines = p.exc_queue.get()
        except Empty:
            self.fail('Failed to raise ProgressTimedOut.')
        else:
            if not isinstance(exc, ProgressTimedOut):
                self.fail(
                    'Error raised, but not ProgressTimedOut:\n{}'.format(
                        ''.join(tb_lines)
                    )
                )


class WriterProcessBaseTests(ColrTestCase):
    """ Tests for the WriterProcessBase. """
    def test_init(self):
        """ Should init from good args. """
        p = WriterProcessBase(
            Queue(maxsize=1),
            Queue(maxsize=1),
            Lock(),
            Value(c_bool, True),
            Value(c_double, 0),
            Value(c_double, 0),
            timeout=None,
            file=TestFile(),
        )
        # Redundant test, checking green's weird FileNotFoundError.
        self.assertIsInstance(
            p,
            WriterProcessBase,
            msg='Failed to initialize WriterProcessBase.',
        )

    def test_timeout(self):
        """ Should throw a ProgressTimedOut exception when timed out. """
        timeout = Value(c_double, 1)
        sleepsecs = timeout.value * 2
        errqueue = Queue(maxsize=1)
        p = WriterProcessBase(
            Queue(maxsize=1),
            errqueue,
            Lock(),
            Value(c_bool, True),
            Value(c_double, 0),
            Value(c_double, 0),
            timeout=timeout,
            file=TestFile(),
        )
        p.start()
        sleep(0.1)
        while sleepsecs > 0:
            sleep(timeout.value)
            sleepsecs -= timeout.value
        p.stop()
        try:
            exc, tb_lines = errqueue.get()
        except Empty:
            self.fail('Failed to raise ProgressTimedOut.')
        else:
            if not isinstance(exc, ProgressTimedOut):
                self.fail(
                    'Error raised, but not ProgressTimedOut:\n{}'.format(
                        ''.join(tb_lines)
                    )
                )


if __name__ == '__main__':
    print('Testing Colr.Progress v. {}'.format(__version__))
    # unittest.main() calls sys.exit(status_code).
    unittest.main(argv=sys.argv, verbosity=2)  # type: ignore
