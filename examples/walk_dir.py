#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" walk_dir.py
    Colr example usage. Walks a directory, printing things along the way.
    -Christopher Welborn 03-26-2017
"""

import os
import sys

NAME = 'Colr Example - Walk Dir.'
VERSION = '0.0.1'
VERSIONSTR = '{} v. {}'.format(NAME, VERSION)
SCRIPT = os.path.split(os.path.abspath(sys.argv[0]))[1]
SCRIPTDIR = os.path.abspath(sys.path[0])

# Add Colr development path to sys.path.
sys.path.insert(0, os.path.abspath(os.path.join(SCRIPTDIR, '..')))

try:
    # Importing colr version separately, to include in future import errors.
    from colr import __version__ as colr_version
except ImportError as ex:
    print(
        'Cannot import __version__ from colr!: {}'.format(ex),
        file=sys.stderr,
    )
    sys.exit(1)

try:
    from colr import (
        AnimatedProgress,
        auto_disable as colr_auto_disable,
        Bars,
        Colr as C,
        docopt,
        Frames,
        ProgressBar,
    )
except ImportError as ex:
    print(
        '\n'.join((
            'Error importing colr dependencies (using v. {colrver}):',
            '  {ex}'
        )).format(ex=ex, colrver=colr_version),
        file=sys.stderr,
    )
    sys.exit(1)

colr_auto_disable()

USAGESTR = """{versionstr}

    Example program using Colr v. {colrver}.
    Walks a directory, printing each one along the way, using either
    a colr.AnimatedProgress or a colr.ProgressBar.

    Usage:
        {script} -h | -v
        {script} [DIR] [-p]

    Options:
        DIR            : Starting directory to walk. This example lasts longer
                         with large directories.
                         Default: /
        -h,--help      : Show this help message.
        -p,--progress  : Use a ProgressBar instead of an AnimatedProgress.
        -v,--version   : Show version.

    Currently using Colr v. {colrver}
""".format(script=SCRIPT, versionstr=VERSIONSTR, colrver=colr_version)


def main(argd):
    """ Main entry point, expects doctopt arg dict as argd. """
    startdir = argd['DIR'] or '/'
    if not os.path.isdir(startdir):
        raise InvalidArg('not a valid start directory: {}'.format(startdir))

    if argd['--progress']:
        return walk_dir_progress(startdir)
    return walk_dir_animated(startdir)


def print_err(*args, **kwargs):
    """ A wrapper for print() that uses stderr by default. """
    if kwargs.get('file', None) is None:
        kwargs['file'] = sys.stderr
    print(*args, **kwargs)


def walk_dir_animated(path, maxdircnt=1000):
    """ Walk a directory, printing status updates along the way. """
    p = AnimatedProgress(
        'Walking {}...'.format(path),
        frames=Frames.dots_orbit.as_rainbow(),
        show_time=True,
    )
    rootcnt = 0
    print('\nStarting animated progress.')
    with p:
        for root, dirs, files in os.walk(path):
            rootcnt += 1
            if rootcnt % 50 == 0:
                p.text = 'Walking {}...'.format(C(root, 'cyan'))
            if rootcnt > maxdircnt:
                # Stop is called because we are printing before the
                # AnimatedProgress is finished running.
                p.stop()
                print('\nFinished walking {} directories.'.format(
                    C(maxdircnt, 'blue', style='bright')
                ))
                break
        else:
            # AnimatedProgress still running, `stop` it before printing.
            p.stop()
            print_err('\nNever made it to {} directories ({}).'.format(
                C(maxdircnt, 'blue', style='bright'),
                C(rootcnt, 'red', style='bright'),
            ))
    print('\nFinished with animated progress.')
    return 0


def walk_dir_progress(path, maxdircnt=5000, file=sys.stdout):
    """ Walk a directory, printing status updates along the way. """
    p = ProgressBar(
        'Walking {}'.format(C(path, 'cyan')),
        bars=Bars.numbers_blue.with_wrapper(('(', ')')),
        show_time=True,
        file=file,
    )
    rootcnt = 0
    print('\nStarting progress bar...')
    p.start()

    for root, dirs, files in os.walk(path):
        rootcnt += 1
        if rootcnt % 100 == 0:
            p.update(
                percent=min((rootcnt / maxdircnt) * 100, 100),
                text='Walking {}...'.format(
                    C(os.path.split(root)[-1], 'cyan'),
                )
            )

        if rootcnt > maxdircnt:
            # Stop is called because we are printing before the
            # AnimatedProgress is finished running.
            p.stop()
            print(
                '\nFinished walking {} directories.'.format(
                    C(maxdircnt, 'blue', style='bright')
                ),
                file=file,
            )
            break
    else:
        # AnimatedProgress still running, `stop` it before printing.
        p.stop()
        print_err(
            '\nNever made it to {} directories ({}).'.format(
                C(maxdircnt, 'blue', style='bright'),
                C(rootcnt, 'red', style='bright'),
            )
        )
    print('\nFinished with progress bar.')
    return 0


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
