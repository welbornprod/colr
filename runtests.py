#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" runtests.py
    Glorified shortcut to `green -vv -q ARGS...`.
    Provides some sane defaults and extra output.
    -Christopher Welborn 03-19-2017
"""

import os
import re
import subprocess
import sys
import unittest
from importlib import import_module

from green import __version__ as green_version
from colr import (
    __version__ as colr_version,
    auto_disable as colr_auto_disable,
    docopt,
    Colr as C,
)

colr_auto_disable()

APPNAME = 'Colr'
APPVERSION = colr_version
NAME = '{} Test Runner'.format(APPNAME)
VERSION = '0.2.0'
VERSIONSTR = '{} v. {}'.format(NAME, VERSION)
SCRIPT = os.path.split(os.path.abspath(sys.argv[0]))[1]
SCRIPTDIR = os.path.abspath(sys.path[0])

USAGESTR = """{versionstr}
    Runs tests using `green` and provides a little more info.

    Usage:
        {script} -h | -v
        {script} (-C | -c)
        {script} [-d] [-s] [-r | -R]
        {script} [-d] [-s] [-r | -R] TESTS...
        {script} (-l | -L) [PATTERN...]

    Options:
        PATTERN              : Regex/text pattern to match against test names.
        TESTS                : Test names for `green`.
        -C,--view-browser    : Shortcut to open the html coverage report
        -c,--view-coverage   : View coverage report in the console.
        -d,--dryrun          : Just show test names.
        -h,--help            : Show this help message.
        -L,--listall         : List all test names with their full name.
        -l,--list            : List all test cases/names.
        -r,--run-coverage    : Run coverage.
        -R,--quiet-coverage  : Run coverage without stdout output.
        -s,--stdout          : Allow stdout (removes -q from green args).
                               in google-chrome.
        -v,--version         : Show version.
""".format(script=SCRIPT, versionstr=VERSIONSTR)

COVERAGE_DIR = os.path.join(SCRIPTDIR, 'coverage_html')


def main(argd):
    """ Main entry point, expects doctopt arg dict as argd. """
    # Use the test directory when no args are given.
    green_exe = get_green_exe()
    if argd['--list'] or argd['--listall']:
        userpats = [
            try_repat(s, default=None)
            for s in argd['PATTERN']
        ]

        return list_tests(full=argd['--listall'], patterns=userpats)
    elif argd['--view-browser']:
        return view_coverage_browser()
    elif argd['--view-coverage']:
        return view_coverage()

    green_args = parse_test_names(argd['TESTS']) or ['test']
    if argd['--dryrun']:
        return print_test_names(green_args)
    cmd = [green_exe, '-vv']
    if not argd['--stdout']:
        cmd.append('-q')
    if argd['--run-coverage'] or argd['--quiet-coverage']:
        cmd.append('-R')

    cmd.extend(green_args)
    print_header(cmd)

    exitcode = subprocess.run(cmd).returncode
    if exitcode:
        return exitcode
    # Success.
    if argd['--run-coverage'] or argd['--quiet-coverage']:
        # Create coverage report.
        return run_coverage(quiet=argd['--quiet-coverage'])

    return exitcode


def filter_test_info(patterns, test_info):
    """ Filter info returned from `load_test_info` using a list of compiled
        regex patterns. Only tests that match test method names, case names,
        or module names are returned in the same format as `load_test_info()`.

        If `patterns` is Falsey, the `test_info` is returned immediately.
    """
    if not patterns:
        return test_info
    filtered = {}
    for modulename, cases in test_info.items():
        keep_module = pats_search(patterns, modulename)
        if keep_module:
            filtered.setdefault(modulename, {})
        casenames = {type(c).__name__: c for c in cases}
        for casename in sorted(casenames):
            case = casenames[casename]
            keep_case = pats_search(patterns, casename)
            if keep_case:
                filtered.setdefault(modulename, {})
                filtered[modulename].setdefault(case, [])
            keepmethods = [
                methodname
                for methodname in sorted(cases[case])
                if pats_search(patterns, methodname)
            ]
            if keepmethods:
                # Add matching test methods, even if the module/case name
                # did not match.
                filtered.setdefault(modulename, {case: None})
                filtered[modulename][case] = keepmethods

    return filtered


def get_green_exe():
    """ Get the green executable for this Python version. """
    paths = set(
        s for s in os.environ.get('PATH', '').split(':')
        if s and os.path.isdir(s)
    )
    pyver = '{v.major}.{v.minor}'.format(v=sys.version_info)
    greenmajorexe = 'green{}'.format(sys.version_info.major)
    greenexe = 'green{}'.format(pyver)
    for trypath in paths:
        greenpath = os.path.join(trypath, greenexe)
        greenmajorpath = os.path.join(trypath, greenmajorexe)
        if os.path.exists(greenpath):
            return greenpath
        elif os.path.exists(greenmajorpath):
            return greenmajorpath
    raise MissingDependency('cannot find an executable for `green`.')


def get_test_cases(modulename, package='test'):
    """ Load all TestCase classes by module name. """
    modl = get_test_module(modulename, package=package)
    cases = []
    for attr in dir(modl):
        try:
            val = getattr(modl, attr, None)
        except AttributeError:
            # This can happen in weird cases.
            continue
        if type(val).__name__ != 'type':
            continue
        if issubclass(val, unittest.TestCase):
            cases.append(val())
    return cases


def get_test_files(package='test'):
    """ Load all test_XX.py module names from the test dir. """
    try:
        files = [s for s in os.listdir(package) if s.startswith('test_')]
    except EnvironmentError as ex:
        raise EnvironmentError(
            'Unable to list "test" dir: {}\n{}'.format(os.getcwd(), ex)
        )
    return [os.path.splitext(s)[0] for s in files]


def get_test_methods(testcase):
    """ Retrieve a list of test method names from a TestCase instance. """
    return [s for s in dir(testcase) if s.startswith('test_')]


def get_test_module(modulename, package='test'):
    """ Load a module object by name. """
    # thispath = sys.path.pop(0)
    cwd = os.getcwd()
    testpath = os.path.join(cwd, package)
    if not os.path.isdir(testpath):
        raise EnvironmentError('Test package not found: {}'.format(testpath))
    if testpath not in sys.path:
        sys.path.insert(0, testpath)
    if cwd not in sys.path:
        sys.path.insert(0, cwd)
    root = os.path.split(cwd)[-1]
    try:
        import_module(package, package=root)
    except ImportError as ex:
        raise ImportError('Cannot import test module: {}'.format(ex))
    try:
        modl = import_module('{}.{}'.format(package, modulename))
    except ImportError as ex:
        raise ImportError('Cannot import module: {}'.format(ex))

    return modl


def get_test_names(package='test'):
    """ Get a flat list of all test modules/cases/names, with their full path.
    """
    yield package
    for modulename, cases in load_test_info(package=package).items():
        yield '.'.join((package, modulename))
        casenames = {type(c).__name__: c for c in cases}
        for casename in sorted(casenames):
            yield '.'.join((package, modulename, casename))
            case = cases[casenames[casename]]
            for methodname in sorted(case):
                yield '.'.join((package, modulename, casename, methodname))


def list_tests(package='test', full=False, patterns=None):
    """ List all discoverable tests. """
    test_info = filter_test_info(
        patterns,
        load_test_info(package=package),
    )
    for modulename, cases in test_info.items():
        modulefmt = C(modulename, 'blue', style='bright')
        casenames = {type(c).__name__: c for c in cases}
        if not full:
            print(modulefmt(':'))
        for casename in sorted(casenames):
            methodnames = cases[casenames[casename]]
            casefmt = C(casename, 'cyan')
            if not full:
                print('  {}'.format(casefmt))
            for methodname in sorted(methodnames):
                methodfmt = C(methodname, 'green')
                if full:
                    print(C('.').join(modulefmt, casefmt, methodfmt))
                else:
                    print('    {}'.format(methodfmt))
            if full and (not methodnames):
                # Methods were filtered out.
                print(C('.').join(modulefmt, casefmt))
        if full and (not casenames):
            # Methods and cases were filtered out.
            print(modulefmt)

    return 0


def load_test_info(package='test'):
    """ Return a dict of {file: {testcase: [test_names...]}} """
    if not os.path.isdir(package):
        print_err('Cannot find test package (\'{}\') dir in: {}'.format(
            package,
            os.getcwd(),
        ))
        return {}
    testinfo = {}
    for modulename in get_test_files(package=package):
        testinfo[modulename] = {}
        for case in get_test_cases(modulename):
            testmethods = get_test_methods(case)
            if not testmethods:
                continue
            testinfo[modulename][case] = testmethods

    return testinfo


def parse_test_names(names):
    """ Prepend 'test.' to test names without it.
        Return a list of test names.
    """
    fixed = set()
    for testname in TESTNAMES:

        for i, name in enumerate(names):
            if not name:
                # Already done.
                continue
            if (name == testname) or (testname.endswith(name)):
                fixed.add(testname)
                names[i] = ''
    return sorted(fixed)


def pats_search(patterns, s):
    """ Returns a list of pattern matches against `s` for all regex patterns
        in the `patterns` list.
    """
    matches = []
    for p in patterns:
        match = p.search(s)
        if match is not None:
            matches.append(match)
    return matches


def print_err(*args, **kwargs):
    """ A wrapper for print() that uses stderr by default.
        Colorizes messages, unless a Colr itself is passed in.
    """
    if kwargs.get('file', None) is None:
        kwargs['file'] = sys.stderr

    # Use color if the file is a tty.
    if kwargs['file'].isatty():
        # Keep any Colr args passed, convert strs into Colrs.
        msg = kwargs.get('sep', ' ').join(
            str(a) if isinstance(a, C) else str(C(a, 'red'))
            for a in args
        )
    else:
        # The file is not a tty anyway, no escape codes.
        msg = kwargs.get('sep', ' ').join(
            str(a.stripped() if isinstance(a, C) else a)
            for a in args
        )

    print(msg, **kwargs)


def print_header(cmd):
    """ Print some info about the Colr and Green versions being used. """
    textcolors = {'fore': 'cyan'}
    libcolors = {'fore': 'blue', 'style': 'bright'}
    vercolors = {'fore': 'blue'}
    execolors = {'fore': 'green', 'style': 'bright'}
    argcolors = {'fore': 'green'}

    def fmt_app_info(name, ver):
        """ Colorize a library and version number. """
        return C(' v. ', **textcolors).join(
            C(name, **libcolors),
            C(ver, **vercolors)
        )

    def fmt_cmd_args(cmdargs):
        """ Colorize a command and argument list. """
        return C(' ').join(
            C(cmdargs[0], **execolors),
            C(' ').join(C(s, **argcolors) for s in cmdargs[1:]),
        ).join('(', ')', style='bright')

    print('{}\n'.format(
        C(' ').join(
            C('Testing', **textcolors),
            fmt_app_info(APPNAME, APPVERSION),
            C('using', **textcolors),
            fmt_app_info('Green', green_version),
            fmt_cmd_args(cmd),
        )
    ))
    print(
        C(': ').join(
            C('Running from', 'cyan'),
            C(os.getcwd(), 'blue', style='bright'),
        ),
    )


def print_test_names(names):
    """ Print formatted test names. """
    print(C(':').join(
        C('Parsed test names', 'cyan'),
        C(len(names), 'blue', style='bright'),
    ))
    for name in names:
        print(C(name, 'blue'))

    return 0 if names else 1


def run_coverage(quiet=False):
    """ Run coverage, and return an exit status code. """
    print(C(': ').join(
        C('Creating coverage report in', 'cyan'),
        C(COVERAGE_DIR, 'blue', style='bright'),
    ))
    covcmd = [
        'coverage',
        'html',
        '--directory',
        COVERAGE_DIR,
        '--title',
        'Coverage for Colr v. {}'.format(colr_version),
    ]
    exitcode = subprocess.run(covcmd).returncode
    if exitcode:
        return exitcode
    if quiet:
        return exitcode
    return view_coverage()


def try_repat(s, default=None):
    """ Try compiling a regex pattern.
        If `s` is Falsey, `default` is returned.
        On errors, InvalidArg is raised.
        On success, a compiled regex pattern is returned.
    """
    if not s:
        return default
    try:
        p = re.compile(s, flags=re.IGNORECASE)
    except re.error as ex:
        raise InvalidArg('Invalid pattern: {}\n{}'.format(s, ex))
    return p


def view_coverage():
    """ Print the coverage report to the console. """
    coverage_file = os.path.join(SCRIPTDIR, '.coverage')
    if not os.path.exists(coverage_file):
        raise InvalidArg('No coverage file found, run coverage: {}'.format(
            coverage_file,
        ))
    # Show console report.
    print(C('').join(C('\nCoverage Report', 'cyan'), ':'))

    covreportcmd = [
        'coverage',
        'report',
    ]
    try:
        output = subprocess.check_output(
            covreportcmd,
            stderr=subprocess.STDOUT,
        ).decode()
    except subprocess.CalledProcessError:
        return 1
    if not output.startswith('Name'):
        print_err(output)
        return 1

    divline = C('-' * 45, 'dimgrey')
    for line in output.splitlines():
        if line.startswith('--'):
            # Divider line.
            print(divline)
            continue
        name, statements, miss, cover = line.split()
        namefmt = C(name).ljust(25)
        statementsfmt = C(statements, (46, 137, 255)).rjust(5)
        try:
            miss = int(miss)
            if miss == 0:
                missfmt = C(miss, 'lightgreen', style='bright').rjust(6)
            else:
                missfmt = C(miss, 'red').rjust(6)
        except ValueError:
            # Actual 'Miss' header.
            missfmt = C(miss, 'red').rjust(6)
        try:
            cover = int(cover.rstrip('%'))
            if cover == 100:
                covercolr = {'fore': 'lightgreen', 'style': 'bright'}
            elif cover > 49:
                covercolr = {'fore': 'green'}
            else:
                covercolr = {'fore': 'red'}
            coverfmt = C('{}%'.format(cover), **covercolr).rjust(6)
        except ValueError:
            # Actual 'Cover' header.
            coverfmt = C(cover, 'green').rjust(6)
        print(C(' ').join(namefmt, statementsfmt, missfmt, coverfmt))
    return 0


def view_coverage_browser():
    """ Open the html coverage report in google-chrome. """
    indexfile = os.path.join(COVERAGE_DIR, 'index.html')
    if not os.path.exists(indexfile):
        print_err(C(': ').join(
            C('Missing coverage report file', 'red'),
            C(indexfile, 'blue'),
        ))
        print_err(C(' ').join(
            C('Run', 'red'),
            C('./runtests.py -R', 'blue').join('`', '`'),
            C('to generate it.', 'red'),
        ))
        return 1

    cmd = ['google-chrome', indexfile]
    print(C(': ').join(
        C('Running', 'cyan'),
        C(' ').join(
            C(cmd[0], 'blue', style='bright'),
            C(' '.join(cmd[1:]), 'blue'),
        ),
    ))
    subprocess.Popen(cmd)
    return 0


class InvalidArg(ValueError):
    """ Raised when the user has used an invalid argument. """
    def __init__(self, msg=None):
        self.msg = msg or ''

    def __str__(self):
        if self.msg:
            return 'Invalid argument, {}'.format(self.msg)
        return 'Invalid argument!'


class MissingDependency(EnvironmentError):
    def __init__(self, msg=None):
        self.msg = msg or ''

    def __str__(self):
        if self.msg:
            return 'Missing dependency, {}'.format(self.msg)
        return 'Missing a dependency!'


TESTNAMES = reversed(list(get_test_names()))

if __name__ == '__main__':
    try:
        mainret = main(docopt(USAGESTR, version=VERSIONSTR, script=SCRIPT))
    except (InvalidArg, MissingDependency) as ex:
        print_err(ex)
        mainret = 1
    except (EOFError, KeyboardInterrupt):
        print_err('\nUser cancelled.\n')
        mainret = 2
    except BrokenPipeError:
        print_err('\nBroken pipe, input/output was interrupted.\n')
        mainret = 3
    sys.exit(mainret)
