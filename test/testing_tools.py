#!/usr/bin/env python3
""" Colr - Testing Tools
    These are some unittest funcs/classes to help with testing.
    -Christopher Welborn 2-27-17
"""
import inspect
import unittest
from contextlib import suppress
from io import StringIO
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
    stdmsg, _, msg = s.partition(':')
    return '{funcsig}: {stdmsg}{msgdiv}{msg}'.format(
        funcsig=format_call_str(*args, **kwargs),
        stdmsg=Colr(stdmsg, 'red', style='bright'),
        msgdiv=': ' if msg else '',
        msg=Colr(msg, 'red'),
    )


def format_call_str(*args: Any, **kwargs: Mapping[Any, Any]):
    """ Build a formatted string for a function signature. """
    use_func_name = None
    with suppress(KeyError):
        use_func = kwargs.pop('_call_func')
        if use_func is not None:
            use_func_name = use_func.__qualname__
        else:
            # Default level uses the caller of format_call_str.
            kwargs.setdefault('_level', 3)

    otherargs = None
    otherkwargs = None
    with suppress(KeyError):
        otherargs = kwargs.pop('_other_args')
    with suppress(KeyError):
        otherkwargs = kwargs.pop('_other_kwargs')
    op = 'and'
    with suppress(KeyError):
        userop = kwargs.pop('_op')
        op = userop or op
    funcsig = format_func_sig(use_func_name, *args, **kwargs)
    if otherargs or otherkwargs:
        otherargs = otherargs or []
        otherkwargs = otherkwargs or {}
        otherkwargs['_level'] = kwargs.get('_level', None)
        funcsig = ' {} '.format(op).join((
            funcsig,
            format_func_sig(use_func_name, *otherargs, **otherkwargs)
        ))
    return funcsig


def format_func_sig(name, *args, **kwargs):
    """ Format a function signature.
        Pass None for a name and use _level=<frames_backward> to use the
        calling function.
    """
    # Default level uses the caller of format_func_sig.
    level = 2
    with suppress(KeyError):
        level = kwargs.pop('_level')

    argstr = Colr(', ').join(Colr(repr(a), 'cyan') for a in args)
    kwargstr = ', '.join(
        '{}={}'.format(Colr(k, 'lightblue'), Colr(repr(v), 'cyan'))
        for k, v in kwargs.items()
    )
    argrepr = Colr(', ').join(s for s in (argstr, kwargstr) if s)
    return '{funcname}{args}'.format(
        funcname=Colr(
            name or func_name(level=level),
            'blue',
            style='bright'
        ),
        args=Colr(argrepr).join('(', ')', style='bright'),
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
    # This is how many frames it takes to get back to the test method
    # that calls the assert method that uses this context.
    # It's for getting the calling test name when building messages.
    calling_test_level = 6

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
                _level=self.calling_test_level,
            )
        )


@no_type_check
class ColrTestCase(unittest.TestCase):
    # This is how many frames it takes to get back to the test method
    # that calls these assert methods.
    # It's for getting the calling test name when building messages.
    calling_test_level = 5

    def assertAlmostEqual(self, a, b, places=None, msg=None, delta=None):
        """ Like self.assertAlmostEqual, with a better message. """
        try:
            super().assertAlmostEqual(
                a,
                b,
                places=places,
                msg=msg,
                delta=delta,
            )
        except self.failureException:
            raise self.failureException(_equality_msg('!~', a, b, msg=msg))

    def assertAlmostNotEqual(self, a, b, places=None, msg=None, delta=None):
        """ Like self.assertAlmostNotEqual, with a better message. """
        try:
            super().assertAlmostNotEqual(
                a,
                b,
                places=places,
                msg=msg,
                delta=delta,
            )
        except self.failureException:
            raise self.failureException(_equality_msg('~', a, b, msg=msg))

    def assertCallEqual(
            self, a, b, func=None,
            args=None, kwargs=None,
            otherargs=None, otherkwargs=None, msg=None):
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
                _level=self.calling_test_level,
                _other_args=otherargs,
                _other_kwargs=otherkwargs,
                _op='!=',
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
                _level=self.calling_test_level,
                _op='!=',
            )
        )

    def assertCallNotEqual(
            self, a, b, func=None,
            args=None, kwargs=None,
            otherargs=None, otherkwargs=None, msg=None):
        """ Like self.assertNotEqual, but includes the func call info. """
        if a != b:
            return None

        callargs = args or []
        callkwargs = kwargs or {}
        raise self.failureException(
            call_msg(
                _equality_msg('==', a, b, msg=msg),
                *callargs,
                **callkwargs,
                _call_func=func,
                _level=self.calling_test_level,
                _other_args=otherargs,
                _other_kwargs=otherkwargs,
                _op='==',
            )
        )

    def assertCallIsInstance(
            self, obj, cls, func=None,
            args=None, kwargs=None,
            otherargs=None, otherkwargs=None, msg=None):
        try:
            super().assertIsInstance(obj, cls, msg=msg)
        except self.failureException as ex:
            stdmsg = ex.args[0] if ex.args else None
            callargs = args or []
            callkwargs = kwargs or {}
            raise self.failureException(
                call_msg(
                    _equality_msg('is not', obj, cls, msg=stdmsg),
                    *callargs,
                    **callkwargs,
                    _other_args=otherargs,
                    _other_kwargs=otherkwargs,
                    _call_func=func,
                    _level=3,
                    _op='is not',
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
                _level=self.calling_test_level,
                _op='!=',
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
            self, a, b, func=None,
            args=None, kwargs=None,
            otherargs=None, otherkwargs=None, msg=None):
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
                    _other_args=otherargs,
                    _other_kwargs=otherkwargs,
                    _call_func=func,
                    _level=3,
                    _op='!=',
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


class TestFile(StringIO):
    """ A file object that deletes it's content every time you call
        str(TestFile).
    """
    def __str__(self):
        self.seek(0)
        s = self.read()
        self.truncate(0)
        self.seek(0)
        return s
