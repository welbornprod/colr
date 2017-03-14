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
        erase_display,
        EraseMethod,
    )
    from colr.progress import (
        AnimatedProgress,
        Frames,
        StaticProgress,
        WriterProcess,
        WriterProcessBase,
        sleep,
    )
except ImportError as ex:
    print('\nUnable to import colr modules: {}\n'.format(ex), file=sys.stderr)
    sys.exit(1)

NAME = 'Progress Test Run'
VERSION = '0.0.1'
VERSIONSTR = '{} v. {}'.format(NAME, VERSION)
SCRIPT = os.path.split(os.path.abspath(sys.argv[0]))[1]
SCRIPTDIR = os.path.abspath(sys.path[0])

USAGESTR = """{versionstr}

    Run tests/examples from colr.progress.

    Usage:
        {script} -e | -h | -v
        {script} [-d secs] [-D secs] [-a] [-f name...] [-b] [-c] [-s]

    Options:
        -f name,--frames name     : Run a specific animated FrameSet test.
                                    More than one flag can be given.
        -a,--animatedprogress     : Run animated progress tests.
        -b,--processbase          : Run processbase tests.
        -c,--process              : Run progress process tests.
        -D secs,--chardelay secs  : Time in seconds for character delay.
                                    Default: None
        -d secs,--delay secs      : Time in seconds for delay.
                                    Default: 0.05
        -e,--erase                : Erase display/scrollback.
        -h,--help                 : Show this help message.
        -s,--staticprogress       : Run static progress tests.
        -v,--version              : Show version.

    The default action is to run all the tests.
""".format(script=SCRIPT, versionstr=VERSIONSTR)


def main(argd):
    """ Main entry point, expects doctopt arg dict as argd. """

    if argd['--erase']:
        erase_display(EraseMethod.ALL_MOVE_ERASE)
        return 0

    delay = parse_float_arg(argd['--delay'], default=None)
    char_delay = parse_float_arg(argd['--chardelay'], default=None)
    test_flags = (
        '--frames',
        '--animatedprogress',
        '--process',
        '--processbase',
        '--staticprogress',
    )
    do_all = not any(argd[f] for f in test_flags)

    errs = 0
    try:
        if argd['--frames']:
            errs += run_test_func(
                run_frame_names,
                argd['--frames'],
                delay=delay,
                char_delay=char_delay,
            )
        if do_all or argd['--animatedprogress']:
            errs += run_test_func(
                run_animatedprogress,
                delay=delay,
                char_delay=char_delay,
            )
        if do_all or argd['--process']:
            errs += run_test_func(run_process, delay=delay)
        if do_all or argd['--processbase']:
            errs += run_test_func(run_processbase, delay=delay)
        if do_all or argd['--staticprogress']:
            errs += run_test_func(
                run_staticprogress,
                delay=delay,
                char_delay=char_delay,
            )
    finally:
        if sys.stdout.isatty() and (not any(sys.exc_info())):
            msg = '\nErase the terminal contents/scrollback? (y/N): '
            if input(msg).lower().strip().startswith('y'):
                erase_display(EraseMethod.ALL_MOVE_ERASE)
    return errs


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


def run_animatedprogress(delay=None, char_delay=None):
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
            char_delay=char_delay,
            fmt=None,
            show_time=True,
        )
        p.start()
        sleepsecs = (p.delay * len(frames)) * 2
        # Should be enough time to see the animation play through once.
        sleep(sleepsecs)
        p.text = 'Almost through with: {}'.format(framename)
        sleep(sleepsecs)
        p.stop()

    frametypes = set()
    framenames = Frames.names()
    while len(frametypes) < maxtypes:
        frametypes.add(Frames.get_by_name(random.choice(framenames)))

    for framesobj in sorted(frametypes):
        run_frame_type(framesobj, framesobj.name)
    print('\nFinished with animated progress functions.\n')
    return 0


def run_frame_name(name, delay=None, char_delay=None):
    """ Run a single animated progress FrameSet by name. """
    try:
        frames = Frames.get_by_name(name)
    except ValueError as ex:
        print_err(ex)
        return 1
    p = AnimatedProgress(
        'Testing animated progress: {}'.format(frames.name),
        frames=frames,
        delay=delay,
        char_delay=char_delay,
        show_time=True,
    )
    p.start()
    framelen = len(frames)
    minruntime = 2
    runtime = max((p.delay * framelen) * 2, minruntime)
    sleep(runtime)
    p.stop()

    return 0


def run_frame_names(names, delay=None, char_delay=None):
    """ Run a list of progress animation FrameSets by name. """
    return sum(
        run_frame_name(n, delay=delay, char_delay=char_delay)
        for n in names
    )


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
    return 0


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
    return 0


def run_staticprogress(delay=None, char_delay=None):
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
        char_delay=char_delay,
        fmt=None,
        show_time=True,
    )
    p.start()
    for i, msg in enumerate(msgs):
        p.text = '{}: {}'.format(i + 1, msg)
        sleep(1)
    p.stop()

    print('\nFinished with static progress functions.\n')
    return 0


def run_test_func(func, *args, **kwargs):
    """ Wrap a test function call in a try block, to handle KeyboardInterrupt
        and exceptions.
    """
    try:
        ret = func(*args, **kwargs)
    except KeyboardInterrupt:
        print('\nUser cancelled.\n', file=sys.stderr)
        return 2

    return ret


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
