#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" colr.__main__.py
    Provides a basic cmdline tool for color-formatted text.
    Example:
        python3 -m colr "Hello World" "green"
        # or:
        python3 -m colr "Hello World" -s "bright" -f "green"
    -Christopher Welborn 12-05-2015
"""

import os
import sys

from .colr import __version__, auto_disable, strip_codes, Colr as C

try:
    from docopt import docopt
except ImportError as eximp:
    print('\n'.join((
        'Import error: {}',
        '\nThe colr tool requires docopt to parse command line args.',
        'You can install it using pip:',
        '    pip install docopt'
    )).format(eximp))
    sys.exit(1)

NAME = 'Colr Tool'
VERSIONSTR = '{} v. {}'.format(NAME, __version__)
SCRIPT = os.path.split(os.path.abspath(sys.argv[0]))[1]
SCRIPTDIR = os.path.abspath(sys.path[0])

USAGESTR = """{versionstr}
    Usage:
        {script} -h | -v
        {script} [TEXT] [FORE] [BACK] [STYLE]          [-a] [-e] [-l num] [-n]
        {script} [TEXT] [-f fore] [-b back] [-s style] [-a] [-e] [-l num] [-n]
        {script} [TEXT] -g num [-c num]                [-a] [-e] [-l num] [-n]
        {script} -x [TEXT]

    Options:
        TEXT                   : Text to print. If not given, stdin is used.
        FORE                   : Name or number for fore color to use.
        BACK                   : Name or number for back color to use.
        STYLE                  : Name for style to use.
        -a,--auto-disable      : Automatically disable colors when output
                                 target is not a terminal.
        -b name,--back name    : Name or number for back color to use.
        -c num,--count num     : Number of characters per color step when
                                 using --gradient.
                                 Default: 1
        -e,--err               : Print to stderr instead of stdout.
        -f name,--fore name    : Name or number for fore color to use.
        -g num,--gradient num  : Use the gradient method starting at `num`.
                                 Default: 17
        -h,--help              : Show this help message.
        -l num,--ljust num     : Left justify the text before coloring,
                                 using `num` as the overall width.
        -n,--newline           : Do not append a newline character (\\n).
        -s name,--style name   : Name for style to use.
        -x,--stripcodes        : Strip all color codes from text.
        -v,--version           : Show version.

    Colors and style names can be given in any order when flags are used.
    Without using the flags, they must be given in order (fore, back, style).

""".format(script=SCRIPT, versionstr=VERSIONSTR)


def main(argd):
    """ Main entry point, expects doctopt arg dict as argd. """
    if argd['--auto-disable']:
        auto_disable()

    txt = argd['TEXT'] or read_stdin()
    fd = sys.stderr if argd['--err'] else sys.stdout
    end = '' if argd['--newline'] else '\n'
    if argd['--stripcodes']:
        print(strip_codes(txt), file=fd, end=end)
        return 0

    fore = get_name_arg(argd, '--fore', 'FORE', default=None)
    back = get_name_arg(argd, '--back', 'BACK', default=None)
    style = get_name_arg(argd, '--style', 'STYLE', default=None)

    if argd['--gradient']:
        # Build a gradient from user args.
        clr = gradient(
            txt,
            start=try_int(argd['--gradient'], 17),
            step=try_int(argd['--count'], 1),
            fore=fore,
            back=back,
            style=style)
    else:
        # Normal colored output.
        clr = C(txt, fore=fore, back=back, style=style)

    if argd['--ljust']:
        clr = clr.ljust(try_int(argd['--ljust']))

    print(str(clr), file=fd, end=end)
    return 0


def get_name_arg(argd, *argnames, default=None):
    """ Return the first argument value given.
        When not given, return default.
    """
    val = None
    for argname in argnames:
        if argd[argname]:
            val = argd[argname].lower().strip()
            break
    return val if val else default


def gradient(txt, start=0, step=1, fore=None, back=None, style=None):
    """ Build a gradient string from user args and return it.
        Arguments:
            txt    : The text to style.
            start  : Color number to start from. Default: 0
            step   : Number of characters per color step. Default: 1
            fore   : Fore color. If given, the background is the gradient.
            back   : Back color. If given, the foreground is the gradient.
            style  : Style name to use for the text.
    """
    return str(C(txt).gradient(
        start=start,
        step=step,
        fore=fore,
        back=back,
        style=style))


def read_stdin():
    """ Read text from stdin, and print a helpful message for ttys. """
    if sys.stdin.isatty() and sys.stdout.isatty():
        print('\nReading from stdin until end of file (Ctrl + D)...')

    return sys.stdin.read()


def try_int(s, default=None):
    """ Try parsing a string into an integer.
        If None is passed, default is returned.
        On failure, InvalidNumber is raised.
    """
    if not s:
        return default
    try:
        val = int(s)
    except (TypeError, ValueError):
        raise InvalidNumber(s)

    return val


class InvalidNumber(ValueError):
    """ A ValueError for when parsing an int fails.
        Provides a better error message.
    """

    def __init__(self, string):
        self.string = string

    def __str__(self):
        return 'Invalid number: {}'.format(self.string)

if __name__ == '__main__':
    try:
        mainret = main(docopt(USAGESTR, version=VERSIONSTR))
    except (EOFError, KeyboardInterrupt):
        print('\nUser cancelled.\n', file=sys.stderr)
        mainret = 2
    except BrokenPipeError:
        print(
            '\nBroken pipe, input/output was interrupted.\n',
            file=sys.stderr)
        mainret = 3
    except InvalidNumber as exnum:
        print('\n{}'.format(exnum), file=sys.stderr)
        mainret = 4

    sys.exit(mainret)
