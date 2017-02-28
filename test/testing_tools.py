#!/usr/bin/env python3
""" Colr - Testing Tools
    These are some unittest funcs/classes to help with testing.
    -Christopher Welborn 2-27-17
"""
import inspect
import unittest
from contextlib import suppress
from unittest.case import _AssertRaisesContext
from typing import Any, Callable, Mapping, Optional, no_type_check

from colr import Colr


def _equality_msg(op, a, b, msg=None):
    """ The ne_msg and eq_msg wrap this function to reduce code duplication.
        It builds a message suitable for an assert*Equal msg parameter.
    """
    fmta = str(Colr(repr(a), 'yellow'))
    if repr(a) != str(a):
        fmta = '{} ({})'.format(fmta, a)
    fmtb = str(Colr(repr(b), 'green'))
    if repr(b) != str(b):
        fmtb = '{} ({})'.format(fmtb, b)

    return '\n'.join((
        '\n  {} {}'.format(
            fmta,
            Colr(op, 'red', style='bright')
        ),
        '  {}'.format(fmtb),
        '\n{}'.format(Colr(msg, 'red')) if msg else '',
    ))


def call_msg(s: str, *args: Any, **kwargs: Mapping[Any, Any]):
    """ Return a message suitable for the `msg` arg in asserts,
        including the calling function name.
    """
    use_func_name = None
    with suppress(KeyError):
        use_func = kwargs.pop('_call_func')
        use_func_name = use_func.__qualname__
    level = 2
    with suppress(KeyError):
        level = kwargs.pop('_level')

    argstr = Colr(', ').join(Colr(repr(a), 'cyan') for a in args)
    kwargstr = ', '.join(
        '{}={}'.format(Colr(k, 'lightblue'), Colr(repr(v), 'cyan'))
        for k, v in kwargs.items()
    )
    argrepr = Colr(', ').join(s for s in (argstr, kwargstr) if s)
    stdmsg, _, msg = s.partition(':')
    return '{funcname}{args}: {stdmsg}: {msg}'.format(
        funcname=Colr(
            use_func_name or func_name(level=level),
            'blue',
            style='bright'
        ),
        args=Colr(argrepr).join('(', ')', style='bright'),
        stdmsg=Colr(stdmsg, 'red', style='bright'),
        msg=Colr(msg, 'red'),
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


@no_type_check
class ColrAssertRaisesContext(_AssertRaisesContext):
    def __init__(
            self, expected, test_case, expected_regex=None,
            func=None, args=None, kwargs=None):
        super().__init__(expected, test_case, expected_regex=expected_regex)
        self.func = func
        self.args = args or []
        self.kwargs = kwargs or {}

    def _raiseFailure(self, std_msg):
        raise self.test_case.failureException(
            call_msg(
                self.test_case._formatMessage(self.msg, std_msg),
                *self.args,
                **self.kwargs,
                _call_func=self.func,
                _level=4,
            )
        )


@no_type_check
class ColrTestCase(unittest.TestCase):
    def assertCallEqual(
            self, a, b, func=None, args=None, kwargs=None, msg=None):
        """ Like self.assertEqual, but includes the func call info. """
        if a == b:
            return None

        callargs = args or []
        callkwargs = kwargs or {}
        raise self.failureException(
            call_msg(
                _equality_msg('!=', a, b, msg=msg),
                *callargs,
                **callkwargs,
                _call_func=func,
                _level=3,
            )
        )

    def assertCallFalse(
            self, val, func=None, args=None, kwargs=None, msg=None):
        """ Like self.assertFalse, but includes the func call info. """
        if not val:
            return None
        callargs = args or []
        callkwargs = kwargs or {}
        raise self.failureException(
            call_msg(
                _equality_msg('!=', val, False, msg=msg),
                *callargs,
                **callkwargs,
                _call_func=func,
                _level=3,
            )
        )

    def assertCallTrue(
            self, val, func=None, args=None, kwargs=None, msg=None):
        """ Like self.assertTrue, but includes the func call info. """
        if val:
            return None
        callargs = args or []
        callkwargs = kwargs or {}
        raise self.failureException(
            call_msg(
                _equality_msg('!=', val, True, msg=msg),
                *callargs,
                **callkwargs,
                _call_func=func,
                _level=3,
            )
        )

    def assertCallRaises(
            self, exception, func=None, args=None, kwargs=None, msg=None):
        """ Like self.assertRaises, but includes the func call info. """
        context = ColrAssertRaisesContext(
            exception,
            self,
            func=func,
            args=args,
            kwargs=kwargs
        )
        return context.handle('assertCallRaises', [], {'msg': msg})

    def assertCallTupleEqual(
            self, a, b, func=None, args=None, kwargs=None, msg=None):
        try:
            super().assertTupleEqual(a, b, msg=msg)
        except self.failureException as ex:
            stdmsg = ex.args[0] if ex.args else None
            callargs = args or []
            callkwargs = kwargs or {}
            raise self.failureException(
                call_msg(
                    _equality_msg('!=', a, b, msg=stdmsg),
                    *callargs,
                    **callkwargs,
                    _call_func=func,
                    level=3,
                )
            )

    def assertEqual(self, a, b, msg=None):
        if a == b:
            return None
        raise self.failureException(_equality_msg('!=', a, b, msg=msg))

    def assertNotEqual(self, a, b, msg=None):
        if a != b:
            return None
        raise self.failureException(_equality_msg('==', a, b, msg=msg))

    def assertTupleEqual(self, a, b, msg=None):
        try:
            super().assertTupleEqual(a, b, msg=msg)
        except self.failureException as ex:
            stdmsg = ex.args[0] if ex.args else None
            raise self.failureException(
                _equality_msg('!=', a, b, msg=stdmsg)
            )
