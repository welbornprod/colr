#!/usr/bin/env python3
""" Colr - Progress
    Functions and classes to deal with progress bars or spinners.

    User friendly classes:
    ----------------------
        StaticProgress   - plain text updates with optional elapsed time.
        AnimatedProgress - animated frames, text updates, and optional time.
        ProgressBar      - percentage-based progress updates, text updates,
                           and optional time.

    Base classes:
    -------------
        WriterProcessBase - dumb subprocess that prints in a loop,
                            and receives text updates.
                            manages elapsed time and shares it with the
                            parent process.
        WriterProcess     - sets up communication between the parent/child
                            process for text and time updates.
        ProgressBarBase   - sets up communication between the parent/child
                            process for percentage and message updates.

    Relationships:
    --------------
        WriterProcessBase
            WriterProcess
                StaticProgress
                    AnimatedProgress
                    ProgressBarBase
                        ProgressBar

    -Christopher Welborn 3-12-17

    The MIT License (MIT)

    Copyright (c) 2015-2017 Christopher Welborn

    Permission is hereby granted, free of charge, to any person obtaining a
    copy of this software and associated documentation files (the "Software"),
    to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense,
    and/or sell copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.
"""

import traceback
import sys
from ctypes import (
    c_bool,
    c_double,
)
from io import UnsupportedOperation
from multiprocessing import (
    Lock,
    Process,
    Queue,
    Value,
)

from multiprocessing.queues import Empty
from os import fdopen

from time import (
    sleep,
    time,
)

from typing import (
    Tuple,
)

from .colr import Colr as C
from .controls import Control
from .progress_frames import (  # noqa
    Bars,
    BarSet,
    Frames,
    FrameSet,
)


def try_unbuffered_file(file, _alreadyopen={}):
    """ Try re-opening a file in an unbuffered mode and return it.
        If that fails, just return the original file.
        This function remembers the file descriptors it opens, so it
        never opens the same one twice.

        This is meant for files like sys.stdout or sys.stderr.
    """
    try:
        fileno = file.fileno()
    except (AttributeError, UnsupportedOperation):
        # Unable to use fileno to re-open unbuffered. Oh well.
        # The output may be line buffered, which isn't that great for
        # repeatedly drawing and erasing text, or hiding/showing the cursor.
        return file
    filedesc = _alreadyopen.get(fileno, None)
    if filedesc is not None:
        return filedesc

    filedesc = fdopen(fileno, 'wb', 0)
    _alreadyopen[fileno] = filedesc
    # TODO: sys.stdout/stderr don't need to be closed.
    #       But would it be worth it to try and close these opened files?
    return filedesc


class WriterProcessBase(Process):
    """ A low level subprocess that only does basic print loops.
        Shared state is managed through multiprocessing.Values/Queues.
        This is used by WriterProcess to print and handle text updates.

        This class may be a little confusing to use directly, because of the
        shared state/communication needed to make it work. It has to accept
        values from the main process, and report back values from the
        subprocess, so all of the state should be created from the main
        process and handed off to this subprocess. The properties are just
        wrappers for `multiprocessing.Value`s, that make it easier to set
        the values with normal Python primitives. Text updates are handled
        with a Queue, which this subprocess reads from and the main process
        writes to. WriterProcess will send a text value through the Queue
        when it's `text` property is changed.

        Exceptions are sent through a Queue to be checked at anytime by
        the parent process.

        Just use a WriterProcess, instead of this WriterProcessBase.
        Or better yet, use a StaticProgress, AnimatedProgress, or
        ProgressBar.
    """
    nice_delay = 0.005

    def __init__(
            self, text_queue, exc_queue, lock, stopped, time_started,
            time_elapsed, timeout, name=None, file=None):
        self.file = try_unbuffered_file(file or sys.stdout)
        self.text_queue = text_queue
        self.exc_queue = exc_queue
        self.lock = lock
        self.stop_flag = stopped
        self.time_started = time_started
        self.time_elapsed = time_elapsed
        self.timeout = timeout
        self.name = name or self.__class__.__qualname__
        self._text = None
        self.update_text()
        super().__init__(name=self.name)

    @property
    def elapsed(self):
        with self.time_elapsed.get_lock():
            return self.time_elapsed.value

    def _loop(self):
        """ This is the loop that runs in the subproces. It is called from
            `run` and is responsible for all printing, text updates, and time
            management.
        """
        self.stop_flag.value = False
        self.time_started.value = time()
        self.time_elapsed.value = 0

        while True:
            if self.stop_flag.value:
                break
            self.update_text()
            with self.time_started.get_lock():
                start = self.time_started.value
                with self.time_elapsed.get_lock():
                    self.time_elapsed.value = time() - start
                    if (
                            self.timeout.value and
                            (self.time_elapsed.value > self.timeout.value)):
                        self.stop()
                        raise ProgressTimedOut(
                            self.name,
                            self.time_elapsed.value,
                        )

    def run(self):
        """ Runs the printer loop in a subprocess. This is called by
            multiprocessing.
        """
        try:
            self._loop()
        except Exception:
            # Send the exception through the exc_queue, so the parent
            # process can check it.
            typ, val, tb = sys.exc_info()
            tb_lines = traceback.format_exception(typ, val, tb)
            self.exc_queue.put((val, tb_lines))

    @property
    def started(self):
        return self.time_started.value

    def stop(self):
        """ Stop this WriterProcessBase, and reset the cursor. """
        self.stop_flag.value = True
        with self.lock:
            (
                Control().text(C(' ', style='reset_all'))
                .pos_restore().move_column(1).erase_line()
                .write(self.file)
            )

    @property
    def stopped(self):
        return self.stop_flag.value

    def update_text(self):
        """ Write the current text, and check for any new text changes.
            This also updates the elapsed time.
        """
        self.write()
        try:
            newtext = self.text_queue.get_nowait()
            self._text = newtext
        except Empty:
            pass

    def write(self):
        """ Write the current text to self.file, and flush it.
            This can be overridden to handle custom writes.
        """
        if self._text is not None:
            with self.lock:
                self.file.write(str(self._text).encode())
                self.file.flush()
        sleep(self.nice_delay)


class WriterProcess(WriterProcessBase):
    """ A subprocess that handles printing and updating the text for a
        WriterProcessBase.
        The text is updated by setting `self.text`.
        Subprocess exceptions are checked with `self.exception`,
        if an exception occurred while running it will be automatically
        raised when `self.stop` is called. If you need to know before `stop`
        whether an exception was raised, just check `self.exception` for
        a non-`None` value.

    """
    nice_delay = 0.001
    lock = Lock()

    def __init__(self, text=None, timeout=None, name=None, file=None):
        self.text_queue = Queue(maxsize=1)
        self.exc_queue = Queue(maxsize=1)
        stop_flag = Value(c_bool, True)
        time_started = Value(c_double, 0)
        time_elapsed = Value(c_double, 0)
        timeout = Value(c_double, timeout or 0)
        # This will set self._text, and send it through the pipe initially.
        self._text = None
        self.text = text or ''
        # Any exceptions raised in the subprocess are sent through `exc_queue`
        # and can be retrieved using the `self.exception` property.
        # These values will be set if an exception is raised.
        self._exception = None
        self.tb_lines = None

        super().__init__(
            self.text_queue,
            self.exc_queue,
            self.lock,
            stop_flag,
            time_started,
            time_elapsed,
            timeout,
            name=name or self.__class__.__qualname__,
            file=file,
        )

    @property
    def exception(self):
        """ Try retrieving the last subprocess exception.
            If set, the exception is returned. Otherwise None is returned.
        """
        if self._exception is not None:
            return self._exception
        try:
            exc, tblines = self.exc_queue.get_nowait()
        except Empty:
            self._exception, self.tb_lines = None, None
        else:
            # Raise any exception that the subprocess encountered and sent.
            self._exception, self.tb_lines = exc, tblines
        return self._exception

    @exception.setter
    def exception(self, exc):
        """ Manually set the exception property. """
        self._exception = exc

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.text_queue.put(value)
        if (not getattr(self, 'started', 0)):
            # Either the WriterProcessBase has not been initialized,
            # or this WriterProcess has not started yet.
            # It's probably just setting the initial text.
            # Either way, it's possible that the main thread will end before
            # the Queue finished what it's doing (especially during testing).
            # This will allow this Queue to finish it's operation.
            sleep(0.1)


class StaticProgress(WriterProcess):
    """ A subprocess that writes status updates the terminal.
        Text is only written if it changes (by setting `self.text`),
        and is overwritten by the next text change.
    """
    default_delay = 0.1
    default_format = ('{text}', )
    default_format_time = ('{elapsed:>2.0f}s', '{text}')  # type: Tuple[str, ...]
    join_str = ' '

    def __init__(
            self, text=None, delay=None, fmt=None,
            show_time=False, char_delay=None, timeout=None,
            name=None, file=None):
        # Delay in seconds between frame renders.
        self.delay = (delay or self.default_delay) - self.nice_delay
        # Format for the progress frame, optional time, and text.
        if show_time:
            default_fmt = self.default_format_time
        else:
            default_fmt = self.default_format
        # This is updated when `self.fmt` is set.
        self._fmt = default_fmt
        self.fmt = fmt or default_fmt
        self.fmt_len = len(self.fmt)

        # Time in seconds to delay between character writes.
        self._char_delay = Value(c_double, char_delay or 0.0)

        # Keep track of the last message displayed, for char_delay animations.
        self._last_text = None
        # Initialize the basic ProgressProcess.
        super().__init__(
            text=text,
            timeout=timeout,
            name=name or self.__class__.__qualname__,
            file=file,
        )

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc, exctype, tb):
        self.stop()
        return False

    def __str__(self):
        """ Basic string representation of a Progress is it's current frame
            string. No character delay can be used when using this to write
            to terminal. `self.write()` can write custom codes/formats and
            handle `self.char_delay`.
        """
        return self.join_str.join(self.fmt).format(
            elapsed=self.elapsed,
            text=self.text,
        )

    @property
    def char_delay(self):
        """ Wrapper for multiprocessing Value, `self._char_delay`.
            Allows using normal python values when setting/retrieving.
        """
        with self._char_delay.get_lock():
            return self._char_delay.value

    @char_delay.setter
    def char_delay(self, value):
        with self._char_delay.get_lock():
            self._char_delay.value = value or 0

    @property
    def fmt(self):
        return self._fmt

    @fmt.setter
    def fmt(self, value):
        """ Sets self.fmt, with some extra help for plain format strings. """
        if isinstance(value, str):
            value = value.split(self.join_str)
        if not (value and isinstance(value, (list, tuple))):
            raise TypeError(
                ' '.join((
                    'Expecting str or list/tuple of formats {!r}.',
                    'Got: ({}) {!r}'
                )).format(
                    self.default_format,
                    type(value).__name__,
                    value,
                ))
        self._fmt = value

    def run(self):
        """ Overrides WriterProcess.run, to handle KeyboardInterrupts better.
            This should not be called by any user. `multiprocessing` calls
            this in a subprocess.
            Use `self.start` to start this instance.
        """
        try:
            Control().cursor_hide().write(file=self.file)
            super().run()
        except KeyboardInterrupt:
            self.stop()
        finally:
            Control().cursor_show().write(file=self.file)

    def stop(self):
        """ Stop this animated progress, and block until it is finished. """
        super().stop()
        while not self.stopped:
            # stop() should block, so printing afterwards isn't interrupted.
            sleep(0.001)
        # Retrieve the latest exception, if any.
        exc = self.exception
        if exc is not None:
            raise exc

    def write(self):
        """ Writes a single frame of the progress spinner to the terminal.
            This function updates the current frame before returning.
        """
        if self.text is None:
            # Text has not been sent through the pipe yet.
            # Do not write anything until it is set to non-None value.
            return None
        if self._last_text == self.text:
            char_delay = 0
        else:
            char_delay = self.char_delay
            self._last_text = self.text
        with self.lock:
            ctl = Control().move_column(1).pos_save().erase_line()
            if char_delay == 0:
                ctl.text(str(self)).write(file=self.file)
            else:
                self.write_char_delay(ctl, char_delay)
            ctl.delay(self.delay)
        return None

    def write_char_delay(self, ctl, delay):
        """ Write the formatted format pieces in order, applying a delay
            between characters for the text only.
        """
        for i, fmt in enumerate(self.fmt):
            if '{text' in fmt:
                # The text will use a write delay.
                ctl.text(fmt.format(text=self.text))
                if i != (self.fmt_len - 1):
                    ctl.text(self.join_str)
                ctl.write(
                    file=self.file,
                    delay=delay
                )
            else:
                # Anything else is written with no delay.
                ctl.text(fmt.format(elapsed=self.elapsed))
                if i != (self.fmt_len - 1):
                    # Add the join_str to pieces, except the last piece.
                    ctl.text(self.join_str)
                ctl.write(file=self.file)
        return ctl


class AnimatedProgress(StaticProgress):
    """ A subprocess that writes FrameSets and handles advancing frames.
        The text is updated by setting `self.text` or overriding
        `self.write()`.
        A frame in this context is a single element of a FrameSet.
        The frame, optional elapsed time, and text are written in place
        over and over until `self.stop()` is called. The animation is updated
        after every write. The delay between writes can be set using
        `delay`.

        Example:
            from colr import AnimatedProgress, Frames
            p = AnimatedProgress(
                text='Updating the thing.',
                frames=Frames.dots_orbit_blue,
            )
            p.start()
            # This line runs immediately.
            update_foo()
            # Text is set in the WriterProcess subprocess.
            p.text = 'Calibrating the frob...'
            calibrate_frob()
            # Calling `stop()` allows for a graceful exit/cleanup.
            p.stop()

        Context Manager Example:
            with AnimatedProgress('Testing this...') as p:
                update_foo()
                p.text = 'Calibrating the frob...'
                calibrate_frob()
    """
    join_str = ' '
    default_delay = 0.1
    default_format = ('{frame}', '{text}')
    default_format_time = ('{frame}', '{elapsed:>2.0f}s', '{text}')

    def __init__(
            self, text=None, frames=None, delay=None,
            fmt=None, show_time=False, char_delay=None,
            timeout=None, name=None, file=None):
        self.frames = frames or Frames.default

        if not self.frames:
            raise ValueError('Must have at least one frame. Got: {!r}'.format(
                self.frames
            ))

        # Length of frames, used for setting the current frame.
        self.frame_len = len(self.frames)
        self.current_frame = 0

        # Format for the progress frame, optional time, and text.
        if show_time:
            default_fmt = self.default_format_time
        else:
            default_fmt = self.default_format

        # Initialize the basic StaticProgress.
        defaultname = self.__class__.__qualname__
        if self.frames.name:
            defaultname = '{}: {}'.format(defaultname, self.frames.name)

        super().__init__(
            text=text,
            fmt=fmt or default_fmt,
            file=file,
            char_delay=char_delay,
            delay=self._get_delay(delay, frames),
            name=name or defaultname,
            timeout=timeout,
        )

    def __str__(self):
        """ Basic string representation of a Progress is it's current frame
            string. No character delay can be used when using this to write
            to terminal. `self.write()` can write custom codes/formats and
            handle `self.char_delay`.
        """
        return self.join_str.join(self.fmt).format(
            frame=self.frames[self.current_frame],
            elapsed=self.elapsed,
            text=self.text,
        )

    def _advance_frame(self):
        """ Sets `self.current_frame` to the next frame, looping to the
            beginning if needed.
        """
        self.current_frame += 1
        if self.current_frame == self.frame_len:
            self.current_frame = 0

    def _get_delay(self, userdelay, frameslist):
        """ Get the appropriate delay value to use, trying in this order:
                userdelay
                frameslist.delay
                default_delay

            The user can override the frameslist's delay by specifiying a
            value, and if neither are given the default is used.
        """
        # User frameslists might not be a FrameSet.
        delay = userdelay or getattr(frameslist, 'delay', None)
        delay = (delay or self.default_delay) - self.nice_delay
        if delay < 0:
            delay = 0
        return delay

    def write(self):
        """ Writes a single frame of the progress spinner to the terminal.
            This function updates the current frame before returning.
        """
        super().write()
        self._advance_frame()
        return self.current_frame

    def write_char_delay(self, ctl, delay):
        """ Write the formatted format pieces in order, applying a delay
            between characters for the text only.
        """
        for i, fmt in enumerate(self.fmt):
            if '{text' in fmt:
                # The text will use a write delay.
                ctl.text(fmt.format(text=self.text))
                if i != (self.fmt_len - 1):
                    ctl.text(self.join_str)
                ctl.write(
                    file=self.file,
                    delay=delay
                )
            else:
                # Anything else is written with no delay.
                ctl.text(fmt.format(
                    frame=self.frames[self.current_frame],
                    elapsed=self.elapsed
                ))
                if i != (self.fmt_len - 1):
                    # Add the join_str to pieces, except the last piece.
                    ctl.text(self.join_str)
                ctl.write(file=self.file)
        return ctl


class ProgressBarBase(StaticProgress):
    """ A subprocess that writes a progress bar, and handles message/percent
        updates coming from the parent process.
        StaticProgress can handle updating the overall text
        (message, bar, time), but the message part itself may need to be
        updated.
        Simply setting `mybar.message = 'foo'` will
        not work, because the `message` property was simply copied over to
        the subprocess, and cannot be updated from the parent process.
        This ProgressBarBase is initialized with a Queue passed in from the
        main process to handle message updates.

        This probably doesn't need to be subclassed. You are probably looking
        for the ProgressBar class.
    """
    join_str = ' '
    # ProgressBars need a smaller delay, to catch updates in time.
    default_delay = 0.025
    default_format = ('{bars}', '{text:<40}')
    default_format_time = ('{bars}', '{elapsed:>2.0f}s', '{text:<40}')

    def __init__(
            self, msg_queue, text=None, bars=None,
            fmt=None, show_time=False, timeout=None,
            name=None, file=None):
        self._msg = text or 'Progress'
        self.bars = bars or Bars.default

        if not self.bars:
            raise ValueError('Must have at least one frame. Got: {!r}'.format(
                self.bars
            ))

        # Length of bars, used for setting the current frame.
        self.bar_len = len(self.bars)
        self._percent = Value(c_double, 0)

        # Format for the progress frame, optional time, and text.
        if show_time:
            default_fmt = self.default_format_time
        else:
            default_fmt = self.default_format

        # A queue for sending/receiving message values.
        # This is created in the main process and received in the subprocess.
        # If initialized here, the queue would not be accessible in the
        # parent process.
        self.message_queue = msg_queue
        # Initialize the basic StaticProgress.
        defaultname = self.__class__.__qualname__
        if self.bars.name:
            defaultname = '{}: {}'.format(defaultname, self.bars.name)
        super().__init__(
            text=self._msg,
            fmt=fmt or default_fmt,
            char_delay=None,  # Not supported, not enough time to finish.
            delay=self.default_delay,
            timeout=timeout,
            name=name or defaultname,
            file=file,
        )

    def __str__(self):
        """ String representation of this ProgressBar in it's current state.
        """
        return self.join_str.join(self.fmt).format(
            bars=self.bars.as_percent(self.percent),
            elapsed=self.elapsed,
            text=self.msg,
        )

    @property
    def msg(self):
        try:
            newmessage = self.message_queue.get_nowait()
            self._msg = newmessage
        except Empty:
            pass

        return self._msg

    @property
    def percent(self):
        return self._percent.value

    @percent.setter
    def percent(self, value):
        self._percent.value = value

    def update(self):
        """ Redraw the progress bar, based on self._msg and self._percent. """
        if not self.stopped:
            self.text = str(self)


class ProgressBar(ProgressBarBase):
    """ A subprocess that writes a progress bar, and updates it's state
        through the `update()` method.
    """

    def __init__(
            self, text=None, bars=None,
            fmt=None, show_time=False, timeout=None, name=None, file=None):
        # This Queue will connect this ProgressBar to it's ProgressBarBase
        # for the message part updates.
        self.message_queue = Queue(maxsize=1)
        super().__init__(
            self.message_queue,
            text=text,
            bars=bars,
            fmt=fmt,
            show_time=show_time,
            timeout=timeout,
            name=name,
            file=file,
        )

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        if not self.stopped:
            self._message = value
            self.message_queue.put(value)

    def update(self, percent=None, text=None):
        """ Update the progress bar percentage and message. """
        if percent is not None:
            self.percent = percent
        if text is not None:
            self.message = text
        super().update()


class ProgressTimedOut(Exception):
    """ Raised when a WriterProcessBase times out (because `timeout` was set).
    """
    def __init__(self, msg, elapsed):
        self.msg = msg or ''
        self.elapsed = elapsed

    def __str__(self):
        return (
            'Progress timed out after {elapsed:1.1f} {plural}{msg}'.format(
                elapsed=self.elapsed,
                plural='sec.' if self.elapsed == 1 else 'secs.',
                msg=': {}'.format(self.msg) if self.msg else ''
            )
        )
