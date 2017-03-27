#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" runtests.py
    Glorified shortcut to `green -vv -q ARGS...`.
    Provides some sane defaults and extra output.
    -Christopher Welborn 03-19-2017
"""

import os
import subprocess
import sys
import traceback

from green import __version__ as green_version
from colr import (
    __version__ as colr_version,
    auto_disable as colr_auto_disable,
    docopt,
    Colr as C,
)


try:
    from test import test_colr_tool  # noqa
    from test import test_colr  # noqa
    from test import test_controls  # noqa
    from test import test_progress  # noqa
except Exception as ex:
    print(
        C('\n').join(
            C('Failed to import test modules. Something is wrong:', 'red'),
            '{}: {}'.format(
                C(type(ex).__name__, 'red', style='bright'),
                C(ex, 'magenta'),
            )
        ),
        file=sys.stderr,
    )

    traceback.print_exc()
    sys.exit(1)
colr_auto_disable()

NAME = 'Colr Test Runner'
VERSION = '0.0.1'
VERSIONSTR = '{} v. {}'.format(NAME, VERSION)
SCRIPT = os.path.split(os.path.abspath(sys.argv[0]))[1]
SCRIPTDIR = os.path.abspath(sys.path[0])

USAGESTR = """{versionstr}
    Runs tests using `green` and provides a little more info.

    Usage:
        {script} [-h | -v]
        {script} [-s] TESTS...

    Options:
        TESTS         : Test names for `green`.
        -h,--help     : Show this help message.
        -s,--stdout   : Allow stdout (removes -q from green args).
        -v,--version  : Show version.
""".format(script=SCRIPT, versionstr=VERSIONSTR)


def main(argd):
    """ Main entry point, expects doctopt arg dict as argd. """
    # Use the test directory when no args are given.
    green_exe = get_green_exe()
    green_args = parse_test_names(argd['TESTS']) or ['test']
    cmd = [green_exe, '-vv']
    if not argd['--stdout']:
        cmd.append('-q')
    cmd.extend(green_args)
    print_header(cmd)

    return subprocess.run(cmd).returncode


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


def parse_test_names(names):
    """ Prepend 'test.' to test names without it.
        Return a list of test names.
    """
    parsed = []
    for name in names:
        if name == 'test':
            parsed.append(name)
        elif not name.startswith('test.'):
            parsed.append('test.{}'.format(name))
        else:
            # TODO: Better test discovery, auto naming for things like
            #       ColrTests -> test.test_colr.ColrTests
            parsed.append(name)
    return parsed


def print_err(*args, **kwargs):
    """ A wrapper for print() that uses stderr by default. """
    if kwargs.get('file', None) is None:
        kwargs['file'] = sys.stderr
    print(*args, **kwargs)


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
            fmt_app_info('Colr', colr_version),
            C('using', **textcolors),
            fmt_app_info('Green', green_version),
            fmt_cmd_args(cmd),
        )
    ))


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
