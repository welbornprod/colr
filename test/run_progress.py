#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" run_controls.py
    ...
    -Christopher Welborn 03-06-2017
"""

import os
import random
import re
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
        Bars,
        Frames,
        ProgressBar,
        ProgressTimedOut,
        StaticProgress,
        WriterProcess,
        WriterProcessBase,
        sleep,
    )
except ImportError as ex:
    print('\nUnable to import colr modules: {}\n'.format(ex), file=sys.stderr)
    sys.exit(1)

NAME = 'Progress Test Run'
VERSION = '0.3.0'
VERSIONSTR = '{} v. {}'.format(NAME, VERSION)
SCRIPT = os.path.split(os.path.abspath(sys.argv[0]))[1]
SCRIPTDIR = os.path.abspath(sys.path[0])

USAGESTR = """{versionstr}

    Run tests/examples from colr.progress.

    Usage:
        {script} -B | -e | -F | -h | -v
        {script} [-d secs] [-D secs] [-E] [-p] [-P] [-c] [-s]
        {script} [-d secs] [-D secs] [-E] [-t secs] -b name...
        {script} [-d secs] [-D secs] [-E] [-t secs] -f name...
        {script} [-d secs] [-D secs] [-E] -a [-r pattern]
        {script} [-d secs] [-D secs] [-E] -p [-r pattern]


    Options:
        -B,--barnames             : List progress bar names.
        -b name,--bars name       : Run a specific BarSet test.
        -F,--framenames           : List animated frame names.
        -f name,--frames name     : Run a specific animated FrameSet test.
                                    More than one flag can be given.
        -a,--animatedprogress     : Run animated progress tests.
        -c,--process              : Run progress process tests.
        -D secs,--chardelay secs  : Time in seconds for character delay.
                                    Default: None
        -d secs,--delay secs      : Time in seconds for delay.
                                    Default: 0.05
        -E,--stderr               : Use stderr instead of stdout.
        -e,--erase                : Erase display/scrollback.
        -h,--help                 : Show this help message.
        -P,--processbase          : Run processbase tests.
        -p,--progressbar          : Run progress bar tests.
        -r pat,--regex pat        : Choose only FrameSets/BarSets matching
                                    this pattern.
        -s,--staticprogress       : Run static progress tests.
        -t secs,--timeout secs    : Seconds for animated/progress-bar
                                    timeout.
        -v,--version              : Show version.

    The default action is to run all the tests.
""".format(script=SCRIPT, versionstr=VERSIONSTR)


def main(argd):
    """ Main entry point, expects doctopt arg dict as argd. """

    if argd['--erase']:
        erase_display(EraseMethod.ALL_MOVE_ERASE)
        return 0
    elif argd['--barnames']:
        return list_set_names(Bars)
    elif argd['--framenames']:
        return list_set_names(Frames)

    delay = parse_float_arg(argd['--delay'], default=None)
    char_delay = parse_float_arg(argd['--chardelay'], default=None)
    timeout = parse_float_arg(argd['--timeout'], default=None)
    test_flags = (
        '--bars',
        '--frames',
        '--animatedprogress',
        '--process',
        '--processbase',
        '--progressbar',
        '--staticprogress',
    )
    do_all = not any(argd[f] for f in test_flags)

    errs = 0
    try:
        if argd['--bars']:
            errs += run_test_func(
                run_bar_names,
                argd['--bars'],
                delay=delay,
                timeout=timeout,
                file=sys.stderr if argd['--stderr'] else sys.stdout,
            )
        if argd['--frames']:
            errs += run_test_func(
                run_frame_names,
                argd['--frames'],
                delay=delay,
                char_delay=char_delay,
                timeout=timeout,
                file=sys.stderr if argd['--stderr'] else sys.stdout,
            )
        if do_all or argd['--animatedprogress']:
            errs += run_test_func(
                run_animatedprogress,
                delay=delay,
                char_delay=char_delay,
                file=sys.stderr if argd['--stderr'] else sys.stdout,
                pattern=try_re_pat(argd['--regex'], default=None),
            )
        if do_all or argd['--progressbar']:
            errs += run_test_func(
                run_progressbar,
                delay=delay,
                char_delay=char_delay,
                file=sys.stderr if argd['--stderr'] else sys.stdout,
                pattern=try_re_pat(argd['--regex'], default=None),
            )
        if do_all or argd['--process']:
            errs += run_test_func(
                run_process,
                delay=delay,
                file=sys.stderr if argd['--stderr'] else sys.stdout,
            )
        if do_all or argd['--processbase']:
            errs += run_test_func(
                run_processbase,
                delay=delay,
                file=sys.stderr if argd['--stderr'] else sys.stdout,
            )
        if do_all or argd['--staticprogress']:
            errs += run_test_func(
                run_staticprogress,
                delay=delay,
                char_delay=char_delay,
                file=sys.stderr if argd['--stderr'] else sys.stdout,
            )
    finally:
        if sys.stdout.isatty() and (not any(sys.exc_info())):
            msg = '\nErase the terminal contents/scrollback? (y/N): '
            if input(msg).lower().strip().startswith('y'):
                erase_display(EraseMethod.ALL_MOVE_ERASE)
    return errs


def get_framesets(cls, maximum=10, pattern=None):
    """ Gather FrameSet objects from either Frames or Bars.
        If `pattern` is set to a compiled regex pattern,
        return all FrameSets matching the pattern.
        Otherwise, return up to `maximum` random FrameSets.
    """
    frametypes = set()
    framenames = cls.names()
    if pattern is None:
        while len(frametypes) < maximum:
            frametypes.add(cls.get_by_name(random.choice(framenames)))
    else:
        frametypes.update(
            cls.get_by_name(s)
            for s in framenames
            if pattern.search(s) is not None
        )
    return frametypes


def list_set_names(cls):
    """ List all names from a Frames/Bars class, where `cls` is the target
        class to get names from.
    """
    clsname = cls.__name__
    names = cls.names()
    if not names:
        print_err('\nNo names found for: {}'.format(clsname))
        return 1
    print('Names for {} ({}):'.format(clsname, len(names)))
    print('    {}'.format('\n    '.join(names)))
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


def run_animatedprogress(
        delay=None, char_delay=None, file=sys.stdout, pattern=None):
    """ This is a rough test of the AnimatedProgress class. """
    print(C('Testing AnimatedProgress class...', 'cyan'))
    maxtypes = 10
    frametype = 'random frame types'
    if pattern is not None:
        frametype = 'frames matching `{}`'.format(pattern.pattern)
    print(C(' ').join(
        C('Testing', 'cyan'),
        C(maxtypes if pattern is None else 'all', 'blue', style='bright'),
        C().join(C(frametype, 'cyan'), ':')
    ))
    # print('    {}\n'.format('\n    '.join(Frames.names)))
    frameindex = 0

    def run_frame_type(frames, framename):
        nonlocal frameindex
        frameindex += 1

        p = AnimatedProgress(
            '({}/{}) Testing frame type: {}'.format(
                frameindex,
                frameslen,
                framename,
            ),
            frames=frames,
            delay=delay,
            char_delay=char_delay,
            fmt=None,
            show_time=True,
            file=file,
        )
        p.start()
        sleepsecs = (p.delay * len(frames)) * 2
        # Should be enough time to see the animation play through once.
        sleep(min((sleepsecs, 2)))
        p.text = '({}/{}) Almost through with: {}'.format(
            frameindex,
            frameslen,
            framename,
        )
        sleep(min((sleepsecs, 2)))
        p.stop()

    frametypes = get_framesets(Frames, maximum=maxtypes, pattern=pattern)

    frameslen = len(frametypes)
    for framesobj in sorted(frametypes):
        run_frame_type(framesobj, framesobj.name)
    print('\nFinished with animated progress functions.\n')
    return 0


def run_bar_name(
        name, delay=None, char_delay=None, file=sys.stdout,
        min_run_time=5, timeout=None):
    """ Run a single animated progress BarSet by name. """
    try:
        bars = Bars.get_by_name(name)
    except ValueError as ex:
        print_err(ex)
        return 1
    delay = delay or (min_run_time / 20)
    p = ProgressBar(
        'Testing progress bar: {}'.format(bars.name),
        bars=bars,
        show_time=True,
        timeout=timeout,
        file=file,
    )
    try:
        with p:
            for x in range(0, 55, 5):
                p.update(x)
                sleep(delay)
            p.message = 'Almost through with: {}'.format(bars.name)
            for x in range(50, 105, 5):
                p.update(x)
                sleep(delay)
        p.stop()
    except ProgressTimedOut as ex:
        print_err('\n{}'.format(ex))
        return 1
    return 0


def run_bar_names(
        names, delay=None, char_delay=None, timeout=None, file=sys.stdout):
    """ Run a list of progress animation BarSets by name. """
    return sum(
        run_bar_name(
            n,
            delay=delay,
            char_delay=char_delay,
            min_run_time=5,
            timeout=timeout,
            file=file,
        )
        for n in names
    )


def run_frame_name(
        name, delay=None, char_delay=None, timeout=None, file=sys.stdout):
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
        timeout=timeout,
        file=file,
    )
    try:
        p.start()
        framelen = len(frames)
        minruntime = 2
        runtime = max((p.delay * framelen) * 2, minruntime)
        sleep(runtime)
        p.stop()
    except ProgressTimedOut as ex:
        print_err('\n{}'.format(ex))
        return 1
    return 0


def run_frame_names(
        names, delay=None, char_delay=None, timeout=None, file=sys.stdout):
    """ Run a list of progress animation FrameSets by name. """
    return sum(
        run_frame_name(
            n,
            delay=delay,
            char_delay=char_delay,
            timeout=timeout,
            file=file,
        )
        for n in names
    )


def run_process(delay=None, file=sys.stdout):
    """ This is a rough test of the WriterProcess class. """
    print(C('Testing WriterProcess class...', 'cyan'))

    p = WriterProcess(
        '.',
        file=file,
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


def run_processbase(delay=None, file=sys.stdout):
    """ This is a rough test of the WriterProcessBase class. """
    print(C('Testing WriterProcessBase class...', 'cyan'))
    write_lock = Lock()
    text_queue = Queue(maxsize=1)
    err_queue = Queue(maxsize=1)
    stopped = Value(c_bool, True)
    time_started = Value(c_double, 0)
    time_elapsed = Value(c_double, 0)
    timeout = Value(c_double, 0)

    def change_text(s):
        text_queue.put_nowait(s)

    p = WriterProcessBase(
        text_queue,
        err_queue,
        write_lock,
        stopped,
        time_started,
        time_elapsed,
        timeout,
        file=file,
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


def run_progressbar(
        delay=None, char_delay=None, file=sys.stdout, pattern=None):
    """ This is a rough test of the ProgressBar class. """
    print(C('Testing ProgressBar class...', 'cyan'))
    maxtypes = 10
    bartype = 'random bar types'
    if pattern is not None:
        bartype = 'frames matching `{}`'.format(pattern.pattern)
    print(C(' ').join(
        C('Testing', 'cyan'),
        C(maxtypes if pattern is None else 'all', 'blue', style='bright'),
        C().join(C(bartype, 'cyan'), ':')
    ))
    delay = delay or 0.25
    frameindex = 0

    def run_bar_type(bars, barsname):
        nonlocal frameindex
        frameindex += 1

        p = ProgressBar(
            '({}/{}) Testing frame type: {}'.format(
                frameindex,
                barslen,
                barsname,
            ),
            bars=bars,
            show_time=True,
            file=file,
        )
        with p:
            for x in range(0, 50, 5):
                p.update(x)
                sleep(delay)
            p.message = '({}/{}) Almost through with: {}'.format(
                frameindex,
                barslen,
                barsname,
            )
            for x in range(50, 100, 5):
                p.update(x)
                sleep(delay)
            p.update(100)
            sleep(delay)
        p = ProgressBar(
            '({}/{}) Testing percent {}: {}'.format(
                frameindex,
                barslen,
                0,
                barsname,
            ),
            bars=bars,
            show_time=False,
            file=file,
        )
        with p:
            for x in range(0, 160, 10):
                p.message = '({}/{}) Testing percent {}: {}'.format(
                    frameindex,
                    barslen,
                    x,
                    barsname,
                )
                p.update(x)
                sleep(delay * 0.9)

    bartypes = get_framesets(Bars, maximum=maxtypes, pattern=pattern)

    barslen = len(bartypes)
    for barsobj in sorted(bartypes):
        run_bar_type(barsobj, barsobj.name)
    print('\nFinished with progress bar functions.\n')


def run_staticprogress(delay=None, char_delay=None, file=sys.stdout):
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
        file=file,
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

    return ret or 0


def print_err(*args, **kwargs):
    """ A wrapper for print() that uses stderr by default. """
    if kwargs.get('file', None) is None:
        kwargs['file'] = sys.stderr
    print(*args, **kwargs)


def try_re_pat(s, default=None):
    """ Try compiling a regex pattern. Raise InvalidArg on errors.
        If a falsey value is given then `default` is returned.
    """
    if not s:
        return default
    try:
        pat = re.compile(s)
    except re.error as ex:
        raise InvalidArg('invalid pattern: {}\n  {}'.format(s, ex))
    return pat


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
