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

from random import randint

from .colr import (
    __version__,
    codes,
    Colr as C,
    auto_disable,
    codeformat,
    disabled,
    extforeformat,
    get_code_num,
    get_codes,
    get_known_codes,
    get_known_name,
    strip_codes,
)

from .trans import ColorCode

try:
    from .colr_docopt import docopt
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
SCRIPT = 'colr'
SCRIPTDIR = os.path.abspath(sys.path[0])

USAGESTR = """{versionstr}
    Usage:
        {script} -h | -v
        {script} [TEXT] [FORE] [BACK] [STYLE]
                 [-a] [-e] [-c num | -l num | -r num] [-n]
        {script} [TEXT] [-f fore] [-b back] [-s style]
                 [-a] [-e] [-c num | -l num | -r num] [-n]
        {script} [TEXT] [FORE] [BACK] [STYLE]
                 [-a] [-e] [-c num | -l num | -r num] [-n] -g name [-q num] [-w num]
        {script} [TEXT] [-f fore] [-b back] [-s style ]
                 [-a] [-e] [-c num | -l num | -r num] [-n] -g name [-q num] [-w num]
        {script} [TEXT] [FORE] [BACK] [STYLE]
                 [-a] [-e] [-c num | -l num | -r num] [-n] -R [-o num] [-q num] [-w num]
        {script} [TEXT] [-f fore] [-b back] [-s style]
                 [-a] [-e] [-c num | -l num | -r num] [-n] -R [-o num] [-q num] [-w num]
        {script} -x [TEXT] [-a] [-e] [-c num | -l num | -r num] [-n]
        {script} -t [-a] [CODE...]
        {script} -z [-a] [-u] [TEXT]

    Options:
        CODE                      : One or more codes to translate.
        TEXT                      : Text to print. If not given, stdin is used.
        FORE                      : Name or number for fore color to use.
        BACK                      : Name or number for back color to use.
        STYLE                     : Name for style to use.
        -a,--auto-disable         : Automatically disable colors when output
                                    target is not a terminal.
        -b name,--back name       : Name or number for back color to use.
        -c num,--center num       : Center justify the text before coloring,
                                    using `num` as the overall width.
        -e,--err                  : Print to stderr instead of stdout.
        -f name,--fore name       : Name or number for fore color to use.
        -g name,--gradient name   : Use the gradient method by color name.
                                    Default: black
        -h,--help                 : Show this help message.
        -l num,--ljust num        : Left justify the text before coloring,
                                    using `num` as the overall width.
        -n,--newline              : Do not append a newline character (\\n).
        -o num,--offset           : Offset for start of rainbow.
                                    Default: random number between 0-255
        -q num,--frequency num    : Frequency of colors in the rainbow.
                                    Higher value means more colors.
                                    Best when in the range 0.0-1.0.
                                    This does not affect black and white.
                                    Default: 0.1
        -r num,--rjust num        : Right justify the text before coloring,
                                    using `num` as the overall width.
        -R,--rainbow              : Use the rainbow method.
        -s name,--style name      : Name for style to use.
        -t,--translate            : Translate one or more term codes,
                                    hex values, or rgb values.
        -u,--unique               : Only report unique color codes with -z.
        -w num,--spread num       : Spread/width of each color in the rainbow
                                    or gradient.
                                    Default: 3.0
        -x,--stripcodes           : Strip all color codes from text.
        -v,--version              : Show version.
        -z,--listcodes            : List all escape codes found in text.

    Colors and style names can be given in any order when flags are used.
    Without using the flags, they must be given in order (fore, back, style).

""".format(script=SCRIPT, versionstr=VERSIONSTR)  # noqa


def main():
    """ Main entry point, expects doctopt arg dict as argd. """
    argd = docopt(USAGESTR, version=VERSIONSTR, script=SCRIPT)
    if argd['--auto-disable']:
        auto_disable()

    if argd['--translate']:
        # Just translate a simple code and exit.
        try:
            print('\n'.join(translate(argd['CODE'] or read_stdin().split())))
        except ValueError as ex:
            print_err('Translation error: {}'.format(ex))
            return 1
        return 0
    elif argd['--listcodes']:
        # List all escape codes found in some text and exit.
        return list_known_codes(
            argd['TEXT'] or read_stdin(),
            unique=argd['--unique']
        )

    txt = argd['TEXT'] or read_stdin()
    fd = sys.stderr if argd['--err'] else sys.stdout
    end = '' if argd['--newline'] else '\n'

    if argd['--stripcodes']:
        txt = justify(strip_codes(txt), argd)
        print(txt, file=fd, end=end)
        return 0

    clr = get_colr(txt, argd)

    # Center, ljust, rjust, or not.
    clr = justify(clr, argd)
    if clr:
        print(str(clr), file=fd, end=end)
        return 0
    # Error while building Colr.
    return 1


def get_colr(txt, argd):
    """ Return a Colr instance based on user args. """
    fore = get_name_arg(argd, '--fore', 'FORE', default=None)
    back = get_name_arg(argd, '--back', 'BACK', default=None)
    style = get_name_arg(argd, '--style', 'STYLE', default=None)

    if argd['--gradient']:
        # Build a gradient from user args.
        try:
            clr = C(txt).gradient(
                name=argd['--gradient'],
                spread=try_int(argd['--spread'], 1, minimum=0),
                fore=fore,
                back=back,
                style=style
            )
        except ValueError as ex:
            print_err('Error: {}'.format(ex))
            return None
    elif argd['--rainbow']:
        clr = C(txt).rainbow(
            fore=fore,
            back=back,
            style=style,
            freq=try_float(argd['--frequency'], 0.1, minimum=0),
            offset=try_int(argd['--offset'], randint(0, 255), minimum=0),
            spread=try_float(argd['--spread'], 3.0, minimum=0)
        )

    else:
        # Normal colored output.
        clr = C(txt, fore=fore, back=back, style=style)
    return clr


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


def justify(clr, argd):
    """ Justify str/Colr based on user args. """
    if argd['--ljust']:
        return clr.ljust(try_int(argd['--ljust'], minimum=0))
    if argd['--rjust']:
        return clr.rjust(try_int(argd['--rjust'], minimum=0))
    if argd['--center']:
        return clr.center(try_int(argd['--center'], minimum=0))
    return clr


def list_known_codes(s, unique=True):
    """ Find and print all known escape codes in a string,
        using get_known_codes.
    """
    total = 0
    for codedesc in get_known_codes(s, unique=unique):
        total += 1
        print(codedesc)
    plural = 'code' if total == 1 else 'codes'
    codetype = ' unique' if unique else ''
    print('\nFound {}{} escape {}.'.format(total, codetype, plural))
    return 0 if total > 0 else 1


def print_err(*args, **kwargs):
    """ A wrapper for print() that uses stderr by default. """
    if kwargs.get('file', None) is None:
        kwargs['file'] = sys.stderr
    print(C(kwargs.get('sep', ' ').join(args), fore='red'), **kwargs)


def read_stdin():
    """ Read text from stdin, and print a helpful message for ttys. """
    if sys.stdin.isatty() and sys.stdout.isatty():
        print('\nReading from stdin until end of file (Ctrl + D)...')

    return sys.stdin.read()


def translate(usercodes):
    """ Translate one or more hex, term, or rgb value into the others.
        Yields strings with the results for each code translated.
    """
    for code in usercodes:
        code = code.strip().lower()
        if code.isalpha() and (code in codes['fore']):
            # Basic color name.
            yield translate_basic(code)
        else:
            if ',' in code:
                try:
                    r, g, b = (int(c.strip()) for c in code.split(','))
                except (TypeError, ValueError):
                    raise InvalidNumber(code, label='Invalid rgb value:')
                code = (r, g, b)

            colorcode = ColorCode(code)

            if disabled():
                yield str(colorcode)
            yield colorcode.example()


def translate_basic(usercode):
    """ Translate a basic color name to color with explanation. """
    codenum = get_code_num(codes['fore'][usercode])
    colorcode = codeformat(codenum)
    msg = 'Name: {:>10}, Number: {:>3}, EscapeCode: {!r}'.format(
        usercode,
        codenum,
        colorcode
    )
    if disabled():
        return msg
    return str(C(msg, fore=usercode))


def try_float(s, default=None, minimum=None):
    """ Try parsing a string into a float.
        If None is passed, default is returned.
        On failure, InvalidFloat is raised.
    """
    if not s:
        return default
    try:
        val = float(s)
    except (TypeError, ValueError):
        raise InvalidNumber(s, label='Invalid float value:')
    if (minimum is not None) and (val < minimum):
        val = minimum
    return val


def try_int(s, default=None, minimum=None):
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
    if (minimum is not None) and (val < minimum):
        val = minimum
    return val


class InvalidNumber(ValueError):
    """ A ValueError for when parsing an int fails.
        Provides a better error message.
    """

    def __init__(self, string, label=None):
        self.string = string
        self.label = label or 'Invalid number:'

    def __str__(self):
        return '{s.label} {s.string}'.format(s=self)


if __name__ == '__main__':
    try:
        mainret = main()
    except (EOFError, KeyboardInterrupt):
        print_err('\nUser cancelled.\n')
        mainret = 2
    except BrokenPipeError:
        print_err('\nBroken pipe, input/output was interrupted.\n')
        mainret = 3
    except (ValueError, InvalidNumber) as exnum:
        print_err('\n{}'.format(exnum))
        mainret = 4

    sys.exit(mainret)
