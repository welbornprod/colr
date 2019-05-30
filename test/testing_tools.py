#!/usr/bin/env python3
""" Colr - Testing Tools
    These are some unittest funcs/classes to help with testing.
    -Christopher Welborn 2-27-17
"""
import inspect
import json
import sys
import unittest
from contextlib import suppress
from io import (
    BytesIO,
    StringIO,
)
from unittest.case import _AssertRaisesContext
from typing import (
    Any,
    Callable,
    Mapping,
    Optional,
    no_type_check,
)


from colr import (
    Colr,
    InvalidColr,
    InvalidStyle,
)
from colr.__main__ import (
    entry_point,
    main,
)


class _NotSet(object):
    def __bool__(self):
        return False

    def __str__(self):
        return '<Not Set>'


# Singleton instance, something other than None to mean 'Not Set'.
NotSet = _NotSet()


def _equality_msg(op, a, b, msg=None):
    """ The ne_msg and eq_msg wrap this function to reduce code duplication.
        It builds a message suitable for an assert*Equal msg parameter.
    """
    fmta = str(Colr(repr(a), 'yellow'))
    try:
        if repr(a) != str(a):
            fmta = '{} ({}) {}'.format(fmta, a, type(a).__name__)
    except TypeError as ex:
        # str() returned non-string type. Catch it now, instead of pushing
        # to PyPi.
        raise TypeError('{} (A value) (type: {}) (value: {!r})'.format(
            ex,
            type(a).__name__,
            a,
        ))

    fmtb = str(Colr(repr(b), 'green'))
    try:
        if repr(b) != str(b):
            fmtb = '{} ({}) {}'.format(fmtb, b, type(b).__name__)
    except TypeError as ex:
        # str() returned non-string type. Catch it now, instead of pushing
        # to PyPi.
        raise TypeError('{} (B value) (type: {}) (value: {!r})'.format(
            ex,
            type(b).__name__,
            b,
        ))

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
    if s.count(':') == 1:
        stdmsg, _, msg = s.partition(':')  # type: ignore
    else:
        stdmsg, msg = s, None  # type: ignore
    return '{funcsig}: {stdmsg}{msgdiv}{msg}'.format(
        funcsig=format_call_str(*args, **kwargs),
        stdmsg=Colr(stdmsg, 'red', style='bright'),
        msgdiv=': ' if msg else '',
        msg=Colr(msg, 'red'),
    )


def format_call_str(*args: Any, **kwargs: Mapping[Any, Any]):
    """ Build a formatted string for a function signature. """
    use_func_name = None  # type: ignore
    with suppress(KeyError):
        use_func = kwargs.pop('_call_func')  # type: ignore
        if use_func is not None:
            use_func_name = use_func.__qualname__  # type: ignore
        else:
            # Default level uses the caller of format_call_str.
            kwargs.setdefault('_level', 3)

    otherargs = None  # type: ignore
    otherkwargs = None  # type: ignore
    with suppress(KeyError):
        otherargs = kwargs.pop('_other_args')
    with suppress(KeyError):
        otherkwargs = kwargs.pop('_other_kwargs')
    op = 'and'  # type: str
    with suppress(KeyError):
        userop = kwargs.pop('_op')  # type: ignore
        op = userop or op  # type: ignore
    funcsig = format_func_sig(use_func_name, *args, **kwargs)
    if otherargs or otherkwargs:
        otherargs = otherargs or []  # type: ignore
        otherkwargs = otherkwargs or {}  # type: ignore
        otherkwargs['_level'] = kwargs.get('_level', None)  # type: ignore
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


def func_name(
        level: Optional[int] = 1,
        parent: Optional[Callable] = None) -> str:
    """ Return the name of the function that is calling this function. """
    frame = inspect.currentframe()
    # Go back a number of frames (usually 1).
    backlevel = level or 1
    while backlevel > 0:
        frame = frame.f_back  # type: ignore
        backlevel -= 1
    if parent:
        func = '{}.{}'.format(
            parent.__class__.__name__,
            frame.f_code.co_name,  # type: ignore
        )
        return func

    return frame.f_code.co_name  # type: ignore


@no_type_check  # type: ignore
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


@no_type_check  # type: ignore
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

    def assertCallDictEqual(
            self, a, b=NotSet, func=NotSet,
            args=None, kwargs=None,
            otherargs=None, otherkwargs=None, msg=None):
        self.assertUnitTestMethodEqual(
            super().assertDictEqual,
            a,
            b,
            func=func,
            args=args,
            kwargs=kwargs,
            otherargs=otherargs,
            otherkwargs=otherkwargs,
            msg=msg,
        )

    def assertCallEqual(
            self, a, b=NotSet, func=None,
            args=None, kwargs=None,
            otherargs=None, otherkwargs=None, msg=None):
        """ Like self.assertEqual, but includes the func call info. """
        a, b = self.fix_ab_args(a, b, func, args, kwargs)
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
            self, val=NotSet, func=NotSet, args=None, kwargs=None, msg=None):
        """ Like self.assertFalse, but includes the func call info. """
        val = self.fix_val_arg(val, func, args, kwargs)
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

    def assertCallListEqual(
            self, a, b=NotSet, func=NotSet,
            args=None, kwargs=None,
            otherargs=None, otherkwargs=None, msg=None):
        self.assertUnitTestMethodEqual(
            super().assertListEqual,
            a,
            b,
            func=func,
            args=args,
            kwargs=kwargs,
            otherargs=otherargs,
            otherkwargs=otherkwargs,
            msg=msg,
        )

    def assertCallNotEqual(
            self, a, b=NotSet, func=NotSet,
            args=None, kwargs=None,
            otherargs=None, otherkwargs=None, msg=None):
        """ Like self.assertNotEqual, but includes the func call info. """
        a, b = self.fix_ab_args(a, b, func, args, kwargs)
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

    def assertCallRaises(
            self, exception, func=None, args=None, kwargs=None, msg=None):
        """ Like self.assertRaises, but includes the func call info. """
        # TODO: Make func(args, kwargs) callable by this method like the
        #       other assertCall* methods.
        context = ColrAssertRaisesContext(
            exception,
            self,
            func=func,
            args=args,
            kwargs=kwargs
        )
        return context.handle('assertCallRaises', [], {'msg': msg})

    def assertCallTrue(
            self, val=NotSet, func=NotSet, args=None, kwargs=None, msg=None):
        """ Like self.assertTrue, but includes the func call info. """
        val = self.fix_val_arg(val, func, args, kwargs)
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

    def assertCallTupleEqual(
            self, a, b, func=None,
            args=None, kwargs=None,
            otherargs=None, otherkwargs=None, msg=None):

        self.assertUnitTestMethodEqual(
            super().assertTupleEqual,
            a,
            b,
            func=func,
            args=args,
            kwargs=kwargs,
            otherargs=otherargs,
            otherkwargs=otherkwargs,
            msg=msg,
        )

    def assertEqual(self, a, b, msg=None):
        if a == b:
            return None
        raise self.failureException(_equality_msg('!=', a, b, msg=msg))

    def assertGreater(self, a, b, msg=None):
        if a > b:
            return None
        raise self.failureException(_equality_msg('<=', a, b, msg=msg))

    def assertGreaterEqual(self, a, b, msg=None):
        if a >= b:
            return None
        raise self.failureException(_equality_msg('<', a, b, msg=msg))

    def assertLess(self, a, b, msg=None):
        if a < b:
            return None
        raise self.failureException(_equality_msg('>=', a, b, msg=msg))

    def assertLessEqual(self, a, b, msg=None):
        if a <= b:
            return None
        raise self.failureException(_equality_msg('>', a, b, msg=msg))

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

    def assertUnitTestMethodEqual(
            self, method, a, b=NotSet, func=NotSet,
            args=None, kwargs=None,
            otherargs=None, otherkwargs=None, msg=None):
        a, b = self.fix_ab_args(a, b, func, args, kwargs)

        try:
            method(a, b, msg=msg)
        except self.failureException as ex:
            stdmsg = None
            if ex.args:
                stdmsg = ex.args[0].rpartition(':')[-1]
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
                    _level=self.calling_test_level,
                    _op='!=',
                )
            )

    def call_msg(self, s, *args, **kwargs):
        """ Convenience method, a wrapper for `call_msg`. """
        kwargs.setdefault('_level', 4)
        with suppress(KeyError):
            kwargs.setdefault('_call_func', kwargs.pop('func'))
        return call_msg(s, *args, **kwargs)

    def fix_ab_args(self, a, b, func, args, kwargs):
        if b is NotSet:
            if not func:
                raise ValueError('Must supply `b` if not using `func`.')
            # User passed the expected result, compute the returned result.
            b = a
            a = func(*(args or []), **(kwargs or {}))
        return a, b

    def fix_val_arg(self, val, func, args, kwargs):
        if val is NotSet:
            if not func:
                raise ValueError('Must supply `val` if not using `func`.')
            val = func(*(args or []), **(kwargs or {}))
        return val


class ColrToolTestCase(ColrTestCase):
    def assertEntry(
            self, argd, stdout=None, stderr=None, should_fail=False,
            msg=None):
        ret, out, err = self.run_entry_output(
            argd,
            should_fail=should_fail,
        )
        # Check return code.
        if should_fail:
            self.assertGreater(
                ret,
                0,
                msg=msg or 'entry_point() return a zero exit status.',
            )
        else:
            try:
                self.assertEqual(
                    ret,
                    0,
                    msg=msg or 'entry_point() returned a non-zero exit status.',
                )
            except self.failureException as ex:
                if err:
                    msg = '\n'.join((
                        str(ex),
                        '\nStderr:',
                        err,
                    ))
                    raise self.failureException(msg) from ex
                else:
                    raise

        # Check expected stderr output.
        if should_fail and (stderr is not None):
            self.assertEqual(
                err,
                stderr,
                msg=msg or 'entry_point() printed something to stderr.',
            )
        elif not should_fail:
            self.assertEqual(
                err,
                stderr or '',
                msg=msg or 'entry_point() printed something to stderr.',
            )
        # Check expected stdout output, or that there was some output at least.
        if should_fail and (stdout is not None):
            self.assertEqual(
                out,
                stdout,
                msg=msg or 'Output from entry_point() did not match.',
            )
        elif not should_fail:
            self.assertGreater(
                len(out),
                0,
                msg=msg or 'entry_point() did not produce any stdout output.',
            )

    def assertEntryIn(
            self, argd, stdout=None, stderr=None, should_fail=False,
            msg=None):
        """ Assert that entry_point runs, and stdout/stderr contain the strings
            given (`stdout` and `stderr`).
        """
        ret, out, err = self.run_entry_output(
            argd,
            should_fail=should_fail,
        )
        # Check return code.
        if should_fail:
            self.assertGreater(
                ret,
                0,
                msg='entry_point() return a zero exit status.',
            )
        else:
            try:
                self.assertEqual(
                    ret,
                    0,
                    msg='entry_point() returned a non-zero exit status.',
                )
            except self.failureException as ex:
                if err:
                    msg = '\n'.join((
                        str(ex),
                        '\nStdErr:',
                        err,
                    ))
                    raise self.failureException(msg) from ex
                else:
                    raise
        if stderr is not None:
            # Check expected stderr output.
            self.assertIn(
                stderr,
                err,
                msg=msg or 'entry_point() stderr did not contain the string.',
            )
        # Check expected stdout output, or that there was some output at least.
        if stdout is not None:
            self.assertIn(
                stdout,
                out,
                msg=msg or 'entry_point() stdout did not contain the string.',
            )

    def assertMain(
            self, argd, stdout=None, stderr=None, should_fail=False,
            msg=None):
        ret, out, err = self.run_main_output(
            argd,
            should_fail=should_fail,
        )
        # Check return code.
        if should_fail:
            self.assertGreater(
                ret,
                0,
                msg=msg or 'main() return a zero exit status.',
            )
        else:
            try:
                self.assertEqual(
                    ret,
                    0,
                    msg=msg or 'main() returned a non-zero exit status.',
                )
            except self.failureException as ex:
                if err:
                    msg = '\n'.join((
                        str(ex),
                        '\nStderr:',
                        err,
                    ))
                    raise self.failureException(msg) from ex
                else:
                    raise

        # Check expected stderr output.
        if should_fail and (stderr is not None):
            self.assertEqual(
                err,
                stderr,
                msg=msg or 'main() printed something to stderr.',
            )
        elif not should_fail:
            self.assertEqual(
                err,
                stderr or '',
                msg=msg or 'main() printed something to stderr.',
            )
        # Check expected stdout output, or that there was some output at least.
        if should_fail and (stdout is not None):
            self.assertEqual(
                out,
                stdout,
                msg=msg or 'Output from main() did not match.',
            )
        elif not should_fail:
            self.assertGreater(
                len(out),
                0,
                msg=msg or 'main() did not produce any stdout output.',
            )

    def assertMainIn(
            self, argd, stdout=None, stderr=None, should_fail=False,
            msg=None):
        """ Assert that main runs, and stdout/stderr contain the strings
            given (`stdout` and `stderr`).
        """
        ret, out, err = self.run_main_output(
            argd,
            should_fail=should_fail,
        )
        # Check return code.
        if should_fail:
            self.assertGreater(
                ret,
                0,
                msg='main() return a zero exit status.',
            )
        else:
            try:
                self.assertEqual(
                    ret,
                    0,
                    msg='main() returned a non-zero exit status.',
                )
            except self.failureException as ex:
                if err:
                    msg = '\n'.join((
                        str(ex),
                        '\nStdErr:',
                        err,
                    ))
                    raise self.failureException(msg) from ex
                else:
                    raise
        if stderr is not None:
            # Check expected stderr output.
            self.assertIn(
                stderr,
                err,
                msg=msg or 'main() stderr did not contain the string.',
            )
        # Check expected stdout output, or that there was some output at least.
        if stdout is not None:
            self.assertIn(
                stdout,
                out,
                msg=msg or 'main() stdout did not contain the string.',
            )

    def make_argd(self, argd):
        """ Make a copy of self.argd and update it with values from argd.
            Returns the updated copy.
        """
        d = {k: v for k, v in self.argd.items()}
        d.update(argd)
        return d

    def run_entry_output(self, argd, should_fail=False):
        """ Run entry_point() with the given argd, and return the
            exit code and output (exit_code, stdout, stderr).
        """
        with StdErrCatcher() as stderr:
            with StdOutCatcher() as stdout:
                ret = self.run_entry_test(argd, should_fail=should_fail)
                return ret, stdout.output, stderr.output

    def run_entry_test(self, argd, should_fail=False):
        """ Run entry_point() with the given argd, and fail on any errors. """
        argd = self.make_argd(argd)
        try:
            entry_point(argd)
        except (InvalidColr, InvalidStyle) as ex:
            if should_fail:
                raise
            # This should not have happened. Show detailed arg/exc info.
            self.fail(
                'Colr tool failed to run:\n{}\n    argd: {}'.format(
                    ex,
                    json.dumps(argd, sort_keys=True, indent=4)
                )
            )
        except SystemExit as ex:
            return ex.code
        self.fail('entry_point() did not exit cleanly.')

    def run_main_output(self, argd, should_fail=False):
        """ Run main() with the given argd, and return the
            exit code and output (exit_code, stdout, stderr).
        """
        with StdErrCatcher() as stderr:
            with StdOutCatcher() as stdout:
                ret = self.run_main_test(argd, should_fail=should_fail)
                return ret, stdout.output, stderr.output

    def run_main_test(self, argd, should_fail=False):
        """ Run main() with the given argd, and fail on any errors. """
        argd = self.make_argd(argd)
        try:
            ret = main(argd)
        except (InvalidColr, InvalidStyle) as ex:
            if should_fail:
                raise
            # This should not have happened. Show detailed arg/exc info.
            self.fail(
                'Colr tool failed to run:\n{}\n    argd: {}'.format(
                    ex,
                    json.dumps(argd, sort_keys=True, indent=4)
                )
            )
        return ret


class StdOutCatcher(object):
    """ Catches stdout for code inside the 'with' block.

        Usage:
            with StdOutCatcher(escaped=True, max_length=160) as fakestdout:
                # stdout is stored in fakestdout.output
                print('okay')
            # stdout is back to normal
            # retrieve the captured output..
            print('output was: {}'.format(fakestdout.output))
    """
    def __init__(self, tty=True, max_length=0):
        self.tty = tty
        # Maximum length before trimming output
        self.max_length = max_length
        # Output
        self.output = ''
        self.length = 0
        self.max_exceeded = False

    def __enter__(self):
        # Replace fileobj with self, fileobj.write() will be self.write()
        sys.stdout = self
        return self

    def __exit__(self, type, value, traceback):
        # Fix stdout.
        sys.stdout = sys.__stdout__
        return False

    def flush(self):
        """ Doesn't do anything, but it's here for compatibility. """
        return None

    def isatty(self):
        return self.tty

    @property
    def name(self):
        return getattr(
            sys.stdout,
            'name',
            getattr(sys.stdout, '__name__', type(sys.stdout).__name__)
        )

    def write(self, s):
        if not isinstance(s, str):
            raise TypeError('write() expects a str, got: {}'.format(
                type(s).__name__
            ))
        if (not s) or self.max_exceeded:
            # Nothing to write, or max-length was already exceeded.
            return 0

        # Save output
        self.output = ''.join((
            self.output,
            s
        ))
        # Trim and block the next call if we are already at max_length.
        if (self.max_length > 0) and len(self.output) >= self.max_length:
            self.output = self.output[:self.max_length]
            self.max_exceeded = True
        # Output length may have been trimmed.
        self.length = len(self.output)
        return len(s)


class StdErrCatcher(StdOutCatcher):
    def __enter__(self):
        # Replace stderr with self, stderr.write() will be self.write()
        sys.stderr = self
        return self

    def __exit__(self, type, value, traceback):
        # Fix stderr.
        sys.stderr = sys.__stderr__
        return False

    @property
    def name(self):
        return getattr(
            sys.stderr,
            'name',
            getattr(sys.stderr, '__name__', type(sys.stderr).__name__)
        )


class TestFileBytes(BytesIO):
    """ A file object that deletes it's content every time you call
        str(TestFileBytes).
    """
    def __init__(self, data=None, tty=False):
        self.tty = tty
        if data:
            self.write(data)

    def __bytes__(self):
        self.seek(0)
        s = self.read()
        self.truncate(0)
        self.seek(0)
        return s

    def __str__(self):
        return repr(bytes(self))

    def isatty(self):
        return self.tty


class TestFile(StringIO):
    """ A file object that deletes it's content every time you call
        str(TestFile).
    """
    def __init__(self, data=None, tty=False):
        self.tty = tty
        super().__init__()
        self.buffer = TestFileBytes(data=data, tty=tty)

    def __str__(self):
        try:
            self.seek(0)
        except ValueError as ex:
            if 'uninitialized' not in str(ex).lower():
                raise
        s = self.read()
        self.truncate(0)
        self.seek(0)
        return s

    def isatty(self):
        return self.tty

    def write(self, s):
        try:
            data = s.decode()
        except AttributeError:
            data = s

        try:
            super().write(data)
        except ValueError as ex:
            # I/O operation on uninitialized object?
            if 'uninitialized' not in str(ex).lower():
                raise
        self.buffer.write(data.encode())
