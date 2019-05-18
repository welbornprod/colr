#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" benchmark.py
    Benchmarks for `colr.Colr`/`colr.color`.
    -Christopher Welborn 05-18-2019
"""

import os
import re
import sys
from timeit import Timer
from types import FunctionType

from colr import (
    Colr as C,
    docopt,
)
from printdebug import DebugColrPrinter
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import Terminal256Formatter

NAME = 'Colr - Benchmarks'
VERSION = '0.0.1'
VERSIONSTR = '{} v. {}'.format(NAME, VERSION)
SCRIPT = os.path.split(os.path.abspath(sys.argv[0]))[1]
SCRIPTDIR = os.path.abspath(sys.path[0])

DEFAULT_REPEAT = 3
DEFAULT_NUMBER = 10000

USAGESTR = """{versionstr}
    Usage:
        {script} -h | -v
        {script} [-D] [-n num] [-r num] [PATTERN]

    Options:
        PATTERN              : Text/regex pattern to match against benchmark
                               names.
                               Only matching benchmark functions will run.
        -D,--debug           : Show some debug info while running.
        -h,--help            : Show this help message.
        -n num,--number num  : Number of code runs per time test.
                               Default: {default_num}
        -r num,--repeat num  : Number of time to repeat the time test.
                               Default: {default_repeat}
        -v,--version         : Show version.
""".format(
    default_num=DEFAULT_NUMBER,
    default_repeat=DEFAULT_REPEAT,
    script=SCRIPT,
    versionstr=VERSIONSTR,
)

debugprinter = DebugColrPrinter()
debugprinter.disable()
debug = debugprinter.debug
debug_err = debugprinter.debug_err

pygments_lexer = get_lexer_by_name('python3')
pygments_formatter = Terminal256Formatter(bg='dark', style='monokai')


def main(argd):
    """ Main entry point, expects docopt arg dict as argd. """
    debugprinter.enable(argd['--debug'])
    return run_benchmarks(pattern=argd['PATTERN'])


def bench_Colr(repeat=None, number=None):
    argsets = (
        {'args': ('fore', 'red')},
        {'args': ('fore bold', ), 'kwargs': {'style': 'bold'}},
        (
            {'args': ('fore', 'red')},
            {'args': ('bold', ), 'kwargs': {'style': 'bold'}}
        ),
    )
    results = []
    for argset in argsets:
        if not isinstance(argset, (list, tuple)):
            argset = (argset, )
        results.append(
            time_code(build_code_Colr, *argset, repeat=repeat, number=number)
        )
    return results


def bench_color(repeat=None, number=None):
    argsets = (
        {'args': ('fore', 'red')},
        {'args': ('fore bold', ), 'kwargs': {'style': 'bold'}},
        (
            {'args': ('fore', 'red')},
            {'args': ('bold', ), 'kwargs': {'style': 'bold'}}
        ),
    )
    results = []
    for argset in argsets:
        if not isinstance(argset, (list, tuple)):
            argset = (argset, )
        results.append(
            time_code(build_code_color, *argset, repeat=repeat, number=number)
        )
    return results


def build_code_Colr(*argsets):
    validate_argsets(*argsets)
    colrstrs = []
    for argset in argsets:
        colrstrs.append(str(ArgStr.from_argset('Colr', argset)))
    if len(colrstrs) == 1:
        return colrstrs[0]

    colrstr_code = ', '.join(colrstrs)
    return f'C(\' \').join({colrstr_code})'


def build_code_color(*argsets):
    """ Arguments:
            argset  : One or more dict of args: {'args': [], 'kwargs': {}}
    """
    validate_argsets(*argsets)
    funcstrs = [
        str(ArgStr.from_argset('color', argset))
        for argset in argsets
    ]
    if len(argsets) == 1:
        return funcstrs[0]
    funcstr_code = ', '.join(funcstrs)
    return f'\' \'.join(({funcstr_code}))'


def format_code(s):
    """ Use pygments to syntax highlight python code. """
    return highlight(s, pygments_lexer, pygments_formatter).strip()


def get_bench_name(func):
    """ Get a benchmark name, based on it's function (strip the `bench_` part.)
    """
    return func.__name__.partition('_')[-1]


def get_benchmark_funcs():
    """ Get all bench_* functions. """
    globls = globals()
    funcs = [
        globls[k]
        for k in globls
        if k.startswith('bench_') and isinstance(globls[k], FunctionType)
    ]
    debug(f'Found bench_* funcs: {len(funcs)}')
    return sorted(funcs, key=lambda f: f.__name__)


def parse_int(s, default=None):
    """ Parse a string as an integer, returns `default` for falsey value.
        Raises InvalidArg with a message on invalid numbers.
    """
    if not s:
        # None, or less than 1.
        return default
    try:
        val = int(s)
    except ValueError:
        raise InvalidArg('invalid number: {}'.format(s))
    return val


def print_err(*args, **kwargs):
    """ A wrapper for print() that uses stderr by default. """
    if kwargs.get('file', None) is None:
        kwargs['file'] = sys.stderr
    print(*args, **kwargs)


def run_bench_set(func, repeat=None, number=None):
    name = get_bench_name(func)
    debug(f'Running benchmarks (for: {name}')
    namefmt = C(name, 'blue', style='bright')
    label = f'{namefmt}:'
    print(f'\n{label}')
    for code, time in func():
        codefmt = format_code(code)
        timefmt = C('').join(C(f'{time:>3.3f}', 'cyan'), C('s', 'dimgrey'))
        print(f'    {timefmt}: {codefmt}')


def run_benchmarks(pattern=None, repeat=None, number=None):
    pat = try_repat(pattern, default=None)
    repeat = parse_int(repeat, default=3)
    number = parse_int(number, default=10000)
    count = 0
    funcs = get_benchmark_funcs()
    for func in funcs:
        debug(f'Found: {func.__name__}')
        if (pat is not None) and (pat.search(get_bench_name(func)) is None):
            # Doesn't match the pattern.
            debug(f'Ignoring for pattern: {pat.pattern!r}', align=True)
            continue
        count += 1
        run_bench_set(func, repeat=repeat, number=number)
    return 0 if count else 1


def time_code(code_builder, *argsets, repeat=None, number=None):
    """ Arguments:
            argset  : One or more dict of args: {'args': [], 'kwargs': {}}
            repeat  : Number of times to repeat the test.
            number  : Number of code runs per test.
    """
    validate_argsets(*argsets)
    code = code_builder(*argsets)
    t = Timer(code, setup='from colr import Colr, color;C = Colr;')
    debug(f'Timing: {code}')
    result = min(
        t.repeat(
            repeat=repeat or DEFAULT_REPEAT,
            number=number or DEFAULT_NUMBER,
        )
    )
    return code, result


def try_repat(s, default=None):
    """ Try compiling a regex pattern.
        If `s` is Falsey, `default` is returned.
        On errors, InvalidArg is raised.
        On success, a compiled regex pattern is returned.
    """
    if not s:
        return default
    try:
        p = re.compile(s)
    except re.error as ex:
        raise InvalidArg('Invalid pattern: {}\n{}'.format(s, ex))
    return p


def validate_argsets(*argsets):
    """ Arguments:
            argset  : One or more dict of args: {'args': [], 'kwargs': {}}
    """
    for argset in argsets:
        if not isinstance(argset, dict):
            typ = type(argset).__name__
            raise ValueError(
                f'Expecting one or more dict of args, got: ({typ}) {argset!r}'
            )


class ArgStr(object):
    """ Builds "code" for a function call from args and kwargs.
        Used in the timing of functions.
    """

    def __init__(self, func_name, *args, **kwargs):
        self.func_name = func_name
        self.args = args or []
        self.kwargs = kwargs or {}

    def __str__(self):
        argstr = ', '.join(repr(s) for s in self.args)
        kwargstr = ', '.join(f'{k}={v!r}' for k, v in self.kwargs.items())
        argpcs = []
        if argstr:
            argpcs.append(argstr)
        if kwargstr:
            argpcs.append(kwargstr)
        fullargs = ', '.join(argpcs)
        return f'{self.func_name}({fullargs})'

    def add_method(self, method_name, argset):
        self.func_name = f'{str(self)}.{method_name}'
        self.args = argset.get('args', [])
        self.kwargs = argset.get('kwargs', {})
        self.add_methods(argset.get('methods', {}))
        return self

    def add_methods(self, method_argsets):
        for methname, methargset in method_argsets.items():
            self.add_method(methname, methargset)
        return self

    @classmethod
    def from_argset(cls, func_name, argset):
        cls = cls(
            func_name,
            *(argset.get('args', [])),
            **(argset.get('kwargs', {})),
        )
        return cls.add_methods(argset.get('methods', {}))


class InvalidArg(ValueError):
    """ Raised when the user has used an invalid argument. """
    def __init__(self, msg=None):
        self.msg = msg or ''

    def __str__(self):
        if self.msg:
            return 'Invalid argument, {}'.format(self.msg)
        return 'Invalid argument!'


if __name__ == '__main__':
    try:
        mainret = main(docopt(USAGESTR, version=VERSIONSTR, script=SCRIPT))
    except InvalidArg as ex:
        print_err(ex)
        mainret = 1
    except (EOFError, KeyboardInterrupt):
        print_err('\nUser cancelled.\n')
        mainret = 2
    except BrokenPipeError:
        print_err('\nBroken pipe, input/output was interrupted.\n')
        mainret = 3
    sys.exit(mainret)
