#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" run_controls.py
    ...
    -Christopher Welborn 03-06-2017
"""

import os
import random
import sys
from ctypes import c_bool, c_double
from multiprocessing import Lock, Queue, Value
from random import randint

parentdir = os.path.split(os.path.abspath(sys.path[0]))[0]
if parentdir.endswith('colr'):
    # Use dev version before installed version.
    # print(
    #     '..inserting parent dir into sys.path: {}'.format(parentdir),
    #     file=sys.stderr,
    # )
    sys.path.insert(0, parentdir)

try:
    from colr import (
        Colr as C,
        docopt,
    )
    from colr.controls import (
        Control,
        cursor_hide,
        cursor_show,
        EraseMethod,
        erase_display,
        print_inplace,
        print_overwrite,
        sleep,
    )
    from colr.progress import (
        AnimatedProgress,
        Frames,
        StaticProgress,
        WriterProcess,
        WriterProcessBase,
    )
except ImportError as ex:
    print('\nUnable to import colr modules: {}\n'.format(ex), file=sys.stderr)
    sys.exit(1)

NAME = 'Controls Test Run'
VERSION = '0.0.1'
VERSIONSTR = '{} v. {}'.format(NAME, VERSION)
SCRIPT = os.path.split(os.path.abspath(sys.argv[0]))[1]
SCRIPTDIR = os.path.abspath(sys.path[0])

USAGESTR = """{versionstr}

    Run tests/examples from colr.controls.

    Usage:
        {script} -e | -h | -v
        {script} [-d secs] [-a] [-b] [-c] [-m] [-p] [-s] [-S]

    Options:
        -a,--animatedprogress  : Run progress tests.
        -b,--processbase       : Run processbase tests.
        -c,--process           : Run progress process tests.
        -d secs,--delay secs   : Time in seconds for delay.
                                 Default: 0.05
        -e,--erase             : Erase display/scrollback.
        -h,--help              : Show this help message.
        -m,--move              : Run move tests.
        -p,--print             : Run print tests.
        -S,--staticprogress    : Run static progress tests
        -s,--scroll            : Run scroll function tests.
        -v,--version           : Show version.

    The default action is to run all the tests.
""".format(script=SCRIPT, versionstr=VERSIONSTR)


def main(argd):
    """ Main entry point, expects doctopt arg dict as argd. """

    if argd['--erase']:
        erase_display(EraseMethod.ALL_MOVE_ERASE)
        return 0

    delay = parse_float_arg(argd['--delay'], default=0.05)
    test_flags = (
        ('--animatedprogress', run_animatedprogress, delay),
        ('--move', run_move, delay),
        ('--print', run_print, delay),
        ('--process', run_process, delay),
        ('--processbase', run_processbase, delay),
        ('--scroll', run_scroll, delay / 2),
        ('--staticprogress', run_staticprogress, delay),
    )
    do_all = not any(argd[f] for f, _, _ in test_flags)
    cursor_hide()
    try:
        for flag, func, funcdelay in test_flags:
            if do_all or argd[flag]:
                func(delay=funcdelay)
        cursor_show()
    except KeyboardInterrupt:
        print('\nUser cancelled.\n', file=sys.stderr)
    finally:
        cursor_show()
        if all((x is None) for x in sys.exc_info()):
            msg = '\nErase the terminal contents/scrollback? (y/N): '
            if input(msg).lower().strip().startswith('y'):
                erase_display(EraseMethod.ALL_MOVE_ERASE)
    return 0


def parse_float_arg(s, default=None):
    """ Parse a string into a float.
        If s is falsey, `default` is returned.
        InvalidArg is raised on errors.
    """
    if not s:
        return default
    try:
        val = float(s)
    except ValueError:
        raise InvalidArg('not a float: {}'.format(val))
    return val


def run_animatedprogress(delay=0.1):
    """ This is a rough test of the AnimatedProgress class. """
    print(C('Testing AnimatedProgress class...', 'cyan'))
    maxtypes = 10
    print(C(' ').join(
        C('Testing', 'cyan'),
        C(maxtypes, 'blue', style='bright'),
        C().join(C('random frame types', 'cyan'), ':')
    ))
    # print('    {}\n'.format('\n    '.join(Frames.names)))

    def run_frame_type(frames, framename):
        s = 'Testing frame type: {}'.format(framename)
        p = AnimatedProgress(
            s,
            frames=frames,
            delay=delay,
            char_delay=None,
            fmt=None,
            show_time=True,
        )
        p.start()
        sleepsecs = (delay * len(frames)) * 2
        # Should be enough time to see the animation play through once.
        sleep(sleepsecs)
        p.text = 'Almost through with: {}'.format(framename)
        sleep(sleepsecs)
        p.stop()

    frametypes = set()
    while len(frametypes) < maxtypes:
        frametypes.add(Frames.get_by_name(random.choice(Frames.names)))

    for framesobj in sorted(frametypes):
        run_frame_type(framesobj, framesobj.name)
    print('\nFinished with animated progress functions.\n')


def run_move(delay=0.025):
    """ This is a rough test of the move_* functions. """
    width = 48
    width_half = width // 2
    height = 24
    # Draw a block of Xs.
    Control(
        C('\n'.join(('X' * width) for _ in range(height))).rainbow()
    ).move_up(height - 1).write()

    # Draw a line down the middle.
    Control().move_column(width_half).write()
    for _ in range(height):
        Control(C('|', 'blue')).move_back().move_down().write().delay(delay)

    # Draw a line at the top left half.
    Control().move_up(height - 1).move_column().write()
    for _ in range(width_half):
        Control(C('-', 'blue')).write().delay(delay)
    # Draw a line at the bottom right half.
    Control().move_down(height - 1).move_back().write()
    for _ in range(width_half + 1):
        Control(C('-', 'blue')).write().delay(delay)

    # Erase the right half.
    Control().move_column(width_half + 1).erase_line(EraseMethod.END).write()
    for _ in range(height - 1):
        Control().move_up().erase_line(EraseMethod.END).write().delay(delay)

    # Erase the left half.
    (
        Control().move_column(width_half - 1).erase_line(EraseMethod.START)
        .write()
    )
    for _ in range(height - 1):
        (
            Control().move_down().erase_line(EraseMethod.START)
            .write()
            .delay(delay)
        )

    # Widen the "stick".
    start_colr = 255 - width_half
    for colrval in range(start_colr + width_half, start_colr, -1):
        (
            Control().move_up(height - 1)
            .move_column(width + (start_colr - colrval))
            .text(C('-', colrval))
            .write()
        )
        for _ in range(height - 2):
            Control().move_down().move_back().text(C('|', colrval)).write()
        (
            Control().move_down().move_back().text(C('-', colrval))
            .write()
            .delay(delay)
        )

    # Shrink the "sticks".
    Control().move_up(height - 1).write()
    chardelay = delay / 3
    for _ in range(height // 2):
        Control().move_column(width).write()
        for _ in range(width_half + 2):
            (
                Control().erase_line(EraseMethod.END).move_back()
                .write()
                .delay(chardelay)
            )
        Control().move_down().move_column(width_half).write()
        for _ in range(width_half):
            Control(' ').write().delay(chardelay)
            sleep(chardelay)
        Control().move_down().write()

    # Move to the end.
    Control().move_down(height + 1).move_column(width).write()
    print('\nFinished with move functions.\n')


def run_print(delay=0.05):
    """ This is a test of the print_* functions. """
    Control(
        C('This is a test of colr.control.print_* functions.\n').rainbow()
    ).write()
    sleep(0.5)
    print_overwrite(
        '...but you get to see some text animations.',
        delay=delay,
    )
    Control(C('\nI\'m just gonna put this: ', 'cyan')).write(delay=delay)
    for val in (C('here', 'red'), C('there', 'green'), C('nowhere', 'blue')):
        sleep(delay)
        print_inplace(val, delay=delay)
    Control().move_column(1).write()
    for col in range(len('I\'m just gonna put this: nowhere')):
        Control(C('X', randint(0, 255))).write().delay(delay)

    print(Control().erase_line())
    print('\nFinished with print functions.\n')


def run_process(delay=None):
    """ This is a rough test of the WriterProcess class. """
    print(C('Testing WriterProcess class...', 'cyan'))

    p = WriterProcess(
        '.',
        file=sys.stdout,
    )
    p.start()
    sleep(1)
    p.text = '!'
    sleep(1)
    p.text = '?'
    sleep(1)
    p.stop()
    # Test elapsed time changes.
    assert p.elapsed > 1
    print()
    for attr in ('stopped', 'started', 'elapsed'):
        val = getattr(p, attr)
        print('{:>16}: {}'.format(attr, val))

    print('\nFinished with WriterProcess functions.\n')


def run_processbase(delay=None):
    """ This is a rough test of the WriterProcessBase class. """
    print(C('Testing WriterProcessBase class...', 'cyan'))
    write_lock = Lock()
    queue = Queue()
    stopped = Value(c_bool, True)
    time_started = Value(c_double, 0)
    time_elapsed = Value(c_double, 0)

    def change_text(s):
        queue.put_nowait(s)

    p = WriterProcessBase(
        queue,
        write_lock,
        stopped,
        time_started,
        time_elapsed,
        file=sys.stdout,
    )
    change_text('.')
    p.start()
    sleep(1)
    change_text('!')
    sleep(1)
    change_text('?')
    sleep(1)
    p.stop()
    print()
    for attr in ('stop_flag', 'time_started', 'time_elapsed'):
        val = getattr(p, attr).value
        print('{:>16}: {}'.format(attr, val))

    print('\nFinished with WriterProcessBase functions.\n')


def run_scroll(delay=0.05):
    """ This is a rough test of the scroll_* functions. """
    linedelay = delay * 6
    height = 6
    height_dbl = height * 2
    start_colr = 255 - height_dbl
    for i in range(height):
        Control(
            C('Scrolled to {} lines.'.format((i * 2) + 1), start_colr + i)
        ).scroll_up(2).move_column(1).write()
        sleep(linedelay)
    sleep(0.5)
    Control().scroll_down(1).repeat(height_dbl).write()
    for i in range(height_dbl):
        Control(
            C('Scrolled down, overwriting {}.'.format(i + 1), start_colr + i)
        ).write(end='\n')
        sleep(linedelay)

    print('\nFinished with scroll functions.\n')


def run_staticprogress(delay=0.1):
    """ This is a rough test of the StaticProgress class. """
    print(C('Testing StaticProgress class...', 'cyan'))

    s = 'Testing StaticProgress.'
    msgs = (
        'Further testing in progress.',
        'Switching the messages up a little bit.',
        'Another message for you.',
        'Just ran out of messages.',
    )
    p = StaticProgress(
        s,
        delay=delay,
        fmt=None,
        show_time=True,
    )
    p.start()
    for i, msg in enumerate(msgs):
        if i % 2 == 0:
            p.char_delay = 0.1
        else:
            p.char_delay = None
        p.text = '{}: {}'.format(i + 1, msg)
        sleep(1)
    p.stop()

    print('\nFinished with static progress functions.\n')


def print_err(*args, **kwargs):
    """ A wrapper for print() that uses stderr by default. """
    if kwargs.get('file', None) is None:
        kwargs['file'] = sys.stderr
    print(*args, **kwargs)


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
