#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" benchmark.py
    Benchmarks for `colr.Colr`/`colr.color`.
    -Christopher Welborn 05-18-2019
"""

import os
import re
import subprocess
import sys
from timeit import Timer
from types import FunctionType

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import Terminal256Formatter

from colr import (
    AnimatedProgress,
    Colr as C,
    Frames,
    docopt,
)
from easysettings import load_json_settings
from printdebug import DebugColrPrinter

NAME = 'Colr - Benchmarks'
VERSION = '0.0.1'
VERSIONSTR = '{} v. {}'.format(NAME, VERSION)
SCRIPT = os.path.split(os.path.abspath(sys.argv[0]))[1]
SCRIPTDIR = os.path.abspath(sys.path[0])

CONFIG_FILE = os.path.join(SCRIPTDIR, 'benchmarks.json')
DEFAULT_REPEAT = 3
DEFAULT_NUMBER = 10000

USAGESTR = """{versionstr}
    Usage:
        {script} -h | -v
        {script} [-D] -l
        {script} [-D] [-n num] [-r num] [-S] [PATTERN]

    Options:
        PATTERN              : Text/regex pattern to match against benchmark
                               names.
                               Only matching benchmark functions will run.
        -D,--debug           : Show some debug info while running.
        -h,--help            : Show this help message.
        -l,--list            : List any previously saved benchmarks.
        -n num,--number num  : Number of code runs per time test.
                               Default: {default_num}
        -r num,--repeat num  : Number of time to repeat the time test.
                               Default: {default_repeat}
        -S,--save            : Save the benchmark results in benchmarks.json.
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

config = load_json_settings(CONFIG_FILE, default={'times': {}})

# Global git branch being worked on, set in `main()`.
git_branch = None

# An indented, rainbowed, dots Frame.
default_frames = (
    Frames.dots.prepend(' ' * 9).append(' ').as_rainbow()
)

# Difference between benchmarks before they are "marked".
max_diff = 0.005


def main(argd):
    """ Main entry point, expects docopt arg dict as argd. """
    global git_branch
    debugprinter.enable(argd['--debug'])
    git_branch = get_git_branch()
    config['times'].setdefault(git_branch, {})
    if argd['--list']:
        return list_benchmarks()
    return run_benchmarks(
        pattern=try_repat(argd['PATTERN'], default=None),
        repeat=max(1, parse_int(argd['--repeat'], default=DEFAULT_REPEAT)),
        number=max(100, parse_int(argd['--number'], default=DEFAULT_NUMBER)),
        save=argd['--save'],
    )


def bench_Colr(repeat=None, number=None):
    argsets = (
        {'args': ('this', 'red')},
        {'args': ('this thing', ), 'kwargs': {'style': 'bold'}},
        (
            {'args': ('this', 'red')},
            {'args': ('thing', ), 'kwargs': {'style': 'bold'}}
        ),
        {
            'args': ('this', 'red'),
            'method': {
                'bold': {'args': (' thing', )},
            },
        },
        {
            'method': {
                'red': {
                    'args': ('this', ),
                    'method': {
                        'bold': {'args': (' thing', )},
                    },
                },
            }
        }
    )
    for argset in argsets:
        if not isinstance(argset, (list, tuple)):
            argset = (argset, )
        yield time_code(
            build_code_Colr,
            *argset,
            repeat=repeat,
            number=number,
        )


def bench_color(repeat=None, number=None):
    argsets = (
        {'args': ('this', 'red')},
        {'args': ('this thing', ), 'kwargs': {'style': 'bold'}},
        (
            {'args': ('this', 'red')},
            {'args': ('thing', ), 'kwargs': {'style': 'bold'}}
        ),
    )
    for argset in argsets:
        if not isinstance(argset, (list, tuple)):
            argset = (argset, )
        yield time_code(
            build_code_color,
            *argset,
            repeat=repeat,
            number=number,
        )


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


def format_result(name, time, code, indent=4):
    """ Format a timing result for printing. """
    codefmt = format_code(code)
    prevtime = config['times'][git_branch].get(name, {}).get(code, None)
    if (prevtime is not None) and ((time - prevtime) > max_diff):
        timeargs = {'fore': 'red', 'style': 'bright'}
    else:
        timeargs = {'fore': 'cyan'}
    timefmt = C('').join(C(f'{time:>3.3f}', **timeargs), C('s', 'dimgrey'))
    indent = ' ' * indent
    return f'{indent}{timefmt}: {codefmt}'


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


def get_git_branch():
    """ Return the current git branch being worked on. """
    cmd = ['git', 'status', '--porcelain=v2', '--branch']
    out = subprocess.check_output(cmd).decode()
    for line in out.splitlines():
        if not line.startswith('# branch.head'):
            continue
        branch = line.split(' ')[-1]
        return branch

    raise ValueError('\n'.join((
        'Unable to determine branch from `git status`.',
        f'Output was:\n{out}\n'
    )))


def list_benchmarks():
    """ Print any previously saved benchmarks. """
    count = 0
    for branch in sorted(config['times']):
        branchfmt = C(branch, 'blue', style='bright')
        print(f'{branchfmt}:')
        if not config['times'][branch]:
            print(C(': ').join(
                C('        No benchmarks saved for', 'red'),
                branchfmt,
            ))
            continue
        for name in sorted(config['times'][branch]):
            namefmt = C(name, 'green', style='bright')
            print(f'    {namefmt}:')
            for code, time in config['times'][branch][name].items():
                print(format_result(name, time, code, indent=8))
                count += 1

    if not count:
        print_err('No benchmarks have been saved.')
        return 1
    return 0


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


def run_bench_set(func, repeat=None, number=None, save=False):
    name = get_bench_name(func)
    config['times'][git_branch].setdefault(name, {})
    debug(f'Running benchmarks (for: {name}')
    namefmt = C(name, 'blue', style='bright')
    label = f'{namefmt}:'
    print(f'\n{label}')
    for code, time in func(repeat=repeat, number=number):
        print(format_result(name, time, code))
        if save:
            config['times'][git_branch][name][code] = time


def run_benchmarks(pattern=None, repeat=None, number=None, save=False):
    count = 0
    funcs = get_benchmark_funcs()
    for func in funcs:
        name = get_bench_name(func)
        debug(f'Found: ({name}) {func.__name__}')
        if (pattern is not None) and (pattern.search(name) is None):
            # Doesn't match the pattern.
            debug(f'Ignoring for pattern: {pattern.pattern!r}', align=True)
            continue
        count += 1
        run_bench_set(func, repeat=repeat, number=number, save=save)
    if save:
        debug(f'Saving benchmarks in: {CONFIG_FILE}')
        config.save()
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
    codefmt = format_code(code)
    progress = AnimatedProgress(
        codefmt,
        frames=default_frames,
        show_time=False,
    )
    repeat = repeat or DEFAULT_REPEAT
    number = number or DEFAULT_NUMBER
    with progress:
        results = t.repeat(
            repeat=repeat,
            number=number,
        )
        result = sum(results) / repeat
    progress.stop()
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
        validate_argsets(argset)
        self.func_name = f'{str(self)}.{method_name}'
        self.args = argset.get('args', [])
        self.kwargs = argset.get('kwargs', {})
        self.add_methods(argset.get('method', {}))
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
        return cls.add_methods(argset.get('method', {}))


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
