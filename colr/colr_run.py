#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" colr_run.py
    Run a subprocess, but don't let it output to stdout. Instead, capture it
    and show an animation. Stdout output from the process goes straight to
    /dev/null. Stderr too, if the -e option is given on the command line.
    -Christopher Welborn 07-08-2019
"""

import os
import subprocess
import sys

from .base import __version__ as colr_version
from .colr import (
    Colr as C,
    auto_disable as colr_auto_disable,
)
from .progress import AnimatedProgress
from .progress_frames import (
    _build_rainbow_variants,
    Frames,
)

try:
    from .colr_docopt import docopt
except ImportError as ex:
    if 'docopt' in ex.name.lower():
        print(
            'Import error while import colr_docopt: {}'.format(ex),
            file=sys.stderr,
        )
        print(
            '\nYou must have Docopt installed to use this tool.',
            file=sys.stderr,
        )
        print('Install it with: `pip install docopt`', file=sys.stderr)
    else:
        print('Cannot import docopt!: {}'.format(ex), file=sys.stderr)
    sys.exit(1)

_build_rainbow_variants(Frames)
colr_auto_disable()

NAME = 'Colr Run'
VERSION = '0.0.1'
VERSIONSTR = '{} v. {}'.format(NAME, VERSION)
SCRIPT = os.path.split(os.path.abspath(sys.argv[0]))[1]
SCRIPTDIR = os.path.abspath(sys.path[0])

USAGESTR = """{versionstr} (Colr v. {colr_version})
    Runs a program, captures/silences stdout, and prints an animation instead.

    Usage:
        {script} -h | -v
        {script} -l
        {script} [-a] [-e] [-f name] [-m msg] -- ARGS...

    Options:
        ARGS                   : Command and arguments to run.
        -a,--append            : Append command to message.
        -e,--stderr            : Capture stderr also.
        -f name,--frames name  : Name of a frame set to use.
                                 Use -l to list known names.
        -h,--help              : Show this help message.
        -l,--listframes        : List available animated frames names.
        -m msg,--msg msg       : Message to display.
        -v,--version           : Show version.

    Basic Example:
        To run a program with the default settings, -- is still required:
            {script} -- bash -c 'x=0; while ((x<1000000)); do let x+=1; done'

        Any output from the program will ruin the animation. You can silence
        stderr output with -e if you don't need it:
            {script} -e -- some-long-running-command

    Exit Status:
        The exit status of {script} is the exit status of the command being
        executed. For {script} errors, the exit status is 1 for basic errors,
        and 2 for cancelled commands.

""".format(script=SCRIPT, versionstr=VERSIONSTR, colr_version=colr_version)


def main(argd):
    """ Main entry point, expects docopt arg dict as argd. """
    if argd['--listframes']:
        return list_frames()

    try:
        frameset = Frames.get_by_name(argd['--frames'] or 'dots_rainbow')
    except ValueError:
        raise InvalidArg('not a known frame set: {}'.format(argd['--frames']))
    return run_cmd(
        argd['ARGS'],
        msg=argd['--msg'],
        frameset=frameset,
        append=argd['--append'],
        stderr=argd['--stderr'],
    )


def list_frames():
    """ List all available frames names. """
    # Filter colored frames.
    names = Frames.names()
    basicnames = [
        s for s in names
        if not getattr(Frames, s).has_codes()
    ]
    print('\nAvailable Frames ({}):\n    '.format(len(basicnames)), end='')
    print('\n    '.join(basicnames))

    colored = sorted(set(
        name.rpartition('_')[-1]
        for name in names
        if (name not in basicnames) and (not name.endswith('_rgb'))
    ))
    print(
        '\nColor variants available ({}):\n    '.format(len(colored)),
        end='',
    )
    print('\n    '.join(
        '<name>_{}'.format(s)
        for s in colored
    ))
    return 0


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


def run_cmd(args, msg=None, frameset=None, append=False, stderr=False):
    """ Run a command, but capture it's stdout. Show an animation instead.
    """
    cmdstr = ' '.join(args)
    if msg:
        if append:
            msg = f'{msg}: {cmdstr}'
    else:
        msg = cmdstr
    p = AnimatedProgress(
        msg,
        delay=0.3,
        frames=(frameset or Frames.dots_rainbow).prepend(' '),
        show_time=True,
    )
    p.start()
    try:
        ret = subprocess.check_call(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL if stderr else None,
        )
    except subprocess.CalledProcessError:
        ret = 1
    p.stop()
    return ret


class InvalidArg(ValueError):
    """ Raised when the user has used an invalid argument. """
    def __init__(self, msg=None):
        self.msg = msg or ''

    def __str__(self):
        if self.msg:
            return f'Invalid argument, {self.msg}'
        return 'Invalid argument!'


def entry_point():
    """ Wrapper for if __name__ == '__main__', for setuptools console scripts.
    """
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


if __name__ == '__main__':
    entry_point()
