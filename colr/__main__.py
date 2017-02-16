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
import traceback
from contextlib import suppress
from random import randint

from .colr import (
    __version__,
    auto_disable,
    codeformat,
    codes,
    Colr as C,
    disabled,
    get_code_num,
    get_known_codes,
    get_terminal_size,
    in_range,
    InvalidArg,
    InvalidColr,
    parse_colr_arg,
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
             [-a] [-e] [-c num | -l num | -r num] [-n] [-D]
        {script} [TEXT] [-f fore] [-b back] [-s style]
             [-a] [-e] [-c num | -l num | -r num] [-n] [-D]
        {script} [TEXT] [FORE] [BACK] [STYLE] [-a] [-e]
             [-c num | -l num | -r num] [-n] -g name
             [-q num] [-w num] [-T] [-D]
        {script} [TEXT] [-f fore] [-b back] [-s style] [-a] [-e]
             [-c num | -l num | -r num] [-n] -g name
             [-q num] [-w num] [-T] [-D]
        {script} [TEXT] [-f fore] [-b back] [-s style] [-a] [-e]
             [-c num | -l num | -r num] [-n] -G rgb_val...
        {script} [TEXT] [FORE] [BACK] [STYLE] [-a] [-e]
             [-c num | -l num | -r num] [-n] -R [-o num]
             [-q num] [-w num] [-T] [-D]
        {script} [TEXT] [-f fore] [-b back] [-s style] [-a] [-e]
             [-c num | -l num | -r num] [-n] -R [-o num]
             [-q num] [-w num] [-T] [-D]
        {script} -x [TEXT] [-a] [-e] [-c num | -l num | -r num] [-n] [-D]
        {script} -t [-a] [CODE...] [-T] [-D]
        {script} -z [-a] [-T] [-u] [TEXT] [-D]

    Options:
        CODE                      : One or more codes to translate.
        TEXT                      : Text to print.
                                    Default: stdin
        FORE                      : Name or number for fore color to use.
        BACK                      : Name or number for back color to use.
        STYLE                     : Name for style to use.
        -a,--auto-disable         : Automatically disable colors when output
                                    target is not a terminal.
        -b name,--back name       : Name or number for back color to use.
        -c num,--center num       : Center justify the text before coloring,
                                    using `num` as the overall width.
                                    If '0' is given, terminal width is used.
                                    If a negative value is given, it will be
                                    subtracted from the terminal width.
        -D,--debug                : Debug mode, print more information while
                                    running, or on errors.
        -e,--err                  : Print to stderr instead of stdout.
        -f name,--fore name       : Name or number for fore color to use.
        -g name,--gradient name   : Use the gradient method by color name.
                                    Default: black
        -G rgb,--gradientrgb rgb  : Use the rgb gradient method.
                                    You can use this twice to specify the
                                    ending rgb value, which is 255,255,255
                                    by default.
        -h,--help                 : Show this help message.
        -l num,--ljust num        : Left justify the text before coloring,
                                    using `num` as the overall width.
                                    If '0' is given, terminal width is used.
                                    If a negative value is given, it will be
                                    subtracted from the terminal width.
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
                                    If '0' is given, terminal width is used.
                                    If a negative value is given, it will be
                                    subtracted from the terminal width.
        -R,--rainbow              : Use the rainbow method.
        -s name,--style name      : Name for style to use.
        -t,--translate            : Translate one or more term codes,
                                    hex values, or rgb values.
        -T,--truecolor            : Use RGB mode when applicable.
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

DEBUG = False


def main(argd=None):
    """ Main entry point, expects doctopt arg dict as argd. """
    global DEBUG, debug

    # The argd parameter for main() is for testing purposes only.
    argd = argd or docopt(
        USAGESTR,
        version=VERSIONSTR,
        script=SCRIPT,
        # Example usage of colr_docopt colors.
        colors={
            'header': {'fore': 'yellow'},
            'script': {'fore': 'lightblue', 'style': 'bright'},
            'version': {'fore': 'lightblue'},
        }
    )

    DEBUG = argd['--debug']
    # Load real debug function if available.
    if DEBUG:
        load_debug_deps()
    else:
        debug = noop

    if argd['--auto-disable']:
        auto_disable()

    if argd['--translate']:
        # Just translate a simple code and exit.
        try:
            print('\n'.join(
                translate(
                    argd['CODE'] or read_stdin().split(),
                    rgb_mode=argd['--truecolor'],
                )
            ))
        except ValueError as ex:
            print_err('Translation error: {}'.format(ex))
            return 1
        return 0
    elif argd['--listcodes']:
        # List all escape codes found in some text and exit.
        return list_known_codes(
            argd['TEXT'] or read_stdin(),
            unique=argd['--unique'],
            rgb_mode=argd['--truecolor'],
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


def debug(*args, **kwargs):
    """ Just prints to stderr, unless printdebug is installed. Then it
        will be replaced in `main()` by `printdebug.debug`.
    """
    if kwargs.get('file', None) is None:
        kwargs['file'] = sys.stderr
    msg = kwargs.get('sep', ' ').join(str(a) for a in args)
    print('debug: {}'.format(msg), **kwargs)


def dict_pop_or(d, key, default=None):
    """ Try popping a key from a dict.
        Instead of raising KeyError, just return the default value.
    """
    val = default
    with suppress(KeyError):
        val = d.pop(key)
    return val


def get_colr(txt, argd):
    """ Return a Colr instance based on user args. """
    fore = parse_colr_arg(get_name_arg(argd, '--fore', 'FORE', default=None))
    back = parse_colr_arg(get_name_arg(argd, '--back', 'BACK', default=None))
    style = get_name_arg(argd, '--style', 'STYLE', default=None)

    if argd['--gradient']:
        # Build a gradient from user args.
        return C(txt).gradient(
            name=argd['--gradient'],
            spread=try_int(argd['--spread'], 1, minimum=0),
            fore=fore,
            back=back,
            style=style,
            rgb_mode=argd['--truecolor'],
        )
    if argd['--gradientrgb']:
        # Build an rgb gradient from user args.
        rgb_start, rgb_stop = parse_gradient_rgb_args(argd['--gradientrgb'])
        return C(txt).gradient_rgb(
            fore=fore,
            back=back,
            style=style,
            start=rgb_start,
            stop=rgb_stop,
        )
    if argd['--rainbow']:
        return C(txt).rainbow(
            fore=fore,
            back=back,
            style=style,
            freq=try_float(argd['--frequency'], 0.1, minimum=0),
            offset=try_int(argd['--offset'], randint(0, 255), minimum=0),
            spread=try_float(argd['--spread'], 3.0, minimum=0),
            rgb_mode=argd['--truecolor'],
        )

    # Normal colored output.
    return C(txt, fore=fore, back=back, style=style)


def get_name_arg(argd, *argnames, default=None):
    """ Return the first argument value given in a docopt arg dict.
        When not given, return default.
    """
    val = None
    for argname in argnames:
        if argd[argname]:
            val = argd[argname].lower().strip()
            break
    return val if val else default


def handle_err(*args):
    """ Handle fatal errors, caught in __main__ scope.
        If DEBUG is set, print a real traceback.
        Otherwise, `print_err` any arguments passed.
    """
    if DEBUG:
        print_err(traceback.format_exc(), color=False)
    else:
        print_err(*args, newline=True)


def justify(clr, argd):
    """ Justify str/Colr based on user args. """
    methodmap = {
        '--ljust': clr.ljust,
        '--rjust': clr.rjust,
        '--center': clr.center,
    }
    for flag in methodmap:
        if argd[flag]:
            if argd[flag] in ('0', '-'):
                val = get_terminal_size(default=(80, 35))[0]
            else:
                val = try_int(argd[flag], minimum=None)
                if val < 0:
                    # Negative value, subtract from terminal width.
                    val = get_terminal_size(default=(80, 35))[0] + val
            return methodmap[flag](val)

    # No justify args given.
    return clr


def list_known_codes(s, unique=True, rgb_mode=False):
    """ Find and print all known escape codes in a string,
        using get_known_codes.
    """
    total = 0
    for codedesc in get_known_codes(s, unique=unique, rgb_mode=rgb_mode):
        total += 1
        print(codedesc)
    plural = 'code' if total == 1 else 'codes'
    codetype = ' unique' if unique else ''
    print('\nFound {}{} escape {}.'.format(total, codetype, plural))
    return 0 if total > 0 else 1


def load_debug_deps():
    """ Try loading printdebug.DebugColrPrinter. If successful, replace
        the global `debug` function with DebugColrPrinter.debug.
    """
    global debug
    try:
        from printdebug import DebugColrPrinter
    except ImportError:
        return None
    debug = DebugColrPrinter().debug


def noop(*args, **kwargs):
    """ This function does nothing.
        It is used to replace other functions (to disable them).
        See: main()->if DEBUG:
    """
    return None


def parse_gradient_rgb_args(args):
    """ Parse one or two rgb args given with --gradientrgb.
        Raises InvalidArg for invalid rgb values.
        Returns a tuple of (start_rgb, stop_rgb), where the stop_rgb may be
        None if only one arg value was given and start_rgb may be None if
        no values were given.
    """
    arglen = len(args)
    if arglen < 1 or arglen > 2:
        raise InvalidArg(arglen, label='Expecting 1 or 2 \'-G\' flags, got')
    start_rgb = try_rgb(args[0]) if args else None
    stop_rgb = try_rgb(args[1]) if arglen > 1 else None
    return start_rgb, stop_rgb


def print_err(*args, **kwargs):
    """ A wrapper for print() that uses stderr by default. """
    if kwargs.get('file', None) is None:
        kwargs['file'] = sys.stderr

    color = dict_pop_or(kwargs, 'color', True)
    # Use color if asked, but only if the file is a tty.
    if color and kwargs['file'].isatty():
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
    newline = dict_pop_or(kwargs, 'newline', False)
    if newline:
        msg = '\n{}'.format(msg)
    print(msg, **kwargs)


def read_stdin():
    """ Read text from stdin, and print a helpful message for ttys. """
    if sys.stdin.isatty() and sys.stdout.isatty():
        print('\nReading from stdin until end of file (Ctrl + D)...')

    return sys.stdin.read()


def translate(usercodes, rgb_mode=False):
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
                    raise InvalidColr(code)
                code = (r, g, b)

            colorcode = ColorCode(code, rgb_mode=rgb_mode)

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
        raise InvalidNumber(s, label='Invalid float value')
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


def try_rgb(s, default=None):
    """ Try parsing a string into an rgb value (int, int, int),
        where the ints are 0-255 inclusive.
        If None is passed, default is returned.
        On failure, InvalidArg is raised.
    """
    if not s:
        return default
    try:
        r, g, b = (int(x.strip()) for x in s.split(','))
    except ValueError:
        raise InvalidRgb(s)
    if not all(in_range(x, 0, 255) for x in (r, g, b)):
        raise InvalidRgb(s)

    return r, g, b


class InvalidNumber(InvalidArg):
    """ A ValueError for when parsing an int fails.
        Provides a better error message.
    """
    default_label = 'Invalid number'


class InvalidRgb(InvalidArg):
    default_label = 'Invalid rgb value'


if __name__ == '__main__':
    try:
        mainret = main()
    except (EOFError, KeyboardInterrupt):
        print_err('\nUser cancelled.\n')
        mainret = 2
    except BrokenPipeError:
        print_err('\nBroken pipe, input/output was interrupted.\n')
        mainret = 3
    except InvalidArg as exarg:
        handle_err(exarg.as_colr())
        mainret = 4
    except ValueError as exnum:
        handle_err(exnum)
        mainret = 4

    sys.exit(mainret)
