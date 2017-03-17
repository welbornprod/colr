#!/usr/bin/env python3
""" Colr - Progress
    Functions and classes to deal with progress bars or spinners.
    -Christopher Welborn 3-12-17
"""

import sys
from ctypes import (
    c_bool,
    c_double,
)

from multiprocessing import (
    Lock,
    Process,
    Queue,
    Value,
)

from multiprocessing.queues import Empty

from time import (
    sleep,
    time,
)

from .colr import Colr as C
from .controls import Control
from .progress_frames import Frames, FrameSet  # noqa


class WriterProcessBase(Process):
    """ A low level subprocess that only does basic print loops.
        Shared state is managed through multiprocessing.Values/Pipes.
        This is used by WriterProcess to print and handle text updates.
    """
    nice_delay = 0.001

    def __init__(
            self, queue, lock, stopped, time_started,
            time_elapsed, file=None):
        self.file = file or sys.stdout
        self.lock = lock
        self.text_queue = queue
        self._text = None
        self.stop_flag = stopped
        self.time_started = time_started
        self.time_elapsed = time_elapsed
        self.update()
        super().__init__(name=self.__class__.__qualname__)

    @property
    def elapsed(self):
        with self.time_elapsed.get_lock():
            return self.time_elapsed.value

    def run(self):
        self.stop_flag.value = False
        self.time_started.value = time()
        self.time_elapsed.value = 0

        while True:
            if self.stop_flag.value:
                break
            self.update()
            sleep(self.nice_delay)
            with self.time_started.get_lock():
                start = self.time_started.value
                with self.time_elapsed.get_lock():
                    self.time_elapsed.value = time() - start

    @property
    def started(self):
        return self.time_started.value

    def stop(self):
        self.stop_flag.value = True

    @property
    def stopped(self):
        return self.stop_flag.value

    def update(self):
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
                self.file.write(str(self._text))
                self.file.flush()


class WriterProcess(WriterProcessBase):
    """ A subprocess that handles printing and updating the text for a
        WriterProcessBase.
        The text is updated by setting `self.text`.
    """
    nice_delay = 0.001
    lock = Lock()

    def __init__(self, text=None, file=None):
        self.text_queue = Queue(maxsize=1)
        stop_flag = Value(c_bool, True)
        time_started = Value(c_double, 0)
        time_elapsed = Value(c_double, 0)
        # This will set self._text, and send it through the pipe initially.
        self._text = None
        self.text = text or ''
        super().__init__(
            self.text_queue,
            self.lock,
            stop_flag,
            time_started,
            time_elapsed,
            file=file,
        )

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.text_queue.put(value)


class StaticProgress(WriterProcess):
    """ A subprocess that writes status updates the terminal.
        Text is only written if it changes (by setting `self.text`),
        and is overwritten by the next text change.
    """
    default_delay = 0.1
    default_format = ('{text}', )
    default_format_time = ('{elapsed:>2.0f}s', '{text}')
    join_str = ' '

    def __init__(
            self, text=None, delay=None, fmt=None,
            show_time=False, char_delay=None, file=None):
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
            Use `self.start` to start a Progress.
        """
        try:
            Control().cursor_hide().write(file=self.file)
            super().run()
        except KeyboardInterrupt:
            self.stop()
        finally:
            Control().cursor_show().write(file=self.file)

    def stop(self):
        """ Stop this progress if it has been started. Otherwise, do nothing.
        """
        if not self.stopped:
            with self.lock:
                (
                    Control().text(C(' ', style='reset_all'))
                    .pos_restore().move_column(1).erase_line()
                    .write(self.file)
                )
        super().stop()

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
            fmt=None, show_time=False, char_delay=None, file=None):
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

        # Initialize the basic ProgressProcess.
        super().__init__(
            text=text,
            fmt=fmt or default_fmt,
            file=file,
            char_delay=char_delay,
            delay=self._get_delay(delay, frames),
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
