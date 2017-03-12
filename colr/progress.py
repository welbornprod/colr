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
    Pipe,
    Process,
    Value,
)
from time import (
    sleep,
    time,
)

from .colr import Colr as C
from .controls import Control
from .progress_frames import Frames, FrameList  # noqa


class ProcessWriterBase(Process):
    """ A low level subprocess that only does basic print loops.
        Shared state is managed through multiprocessing.Values/Pipes.
        This is used by ProcessWriter to print and handle text updates.
    """
    nice_delay = 0.001

    def __init__(
            self, pipe, lock, stopped, time_started, time_elapsed, file=None):
        self.file = file or sys.stdout
        self.lock = lock
        self.pipe = pipe
        self.text = ''
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
        newtext = None
        if self.pipe.poll():
            newtext = self.pipe.recv()
        if (newtext is not None) and (newtext != self.text):
            self.text = newtext

    def write(self):
        """ Write the current text to self.file, and flush it.
            This can be overridden to handle custom writes.
        """
        if self.text is not None:
            with self.lock:
                self.file.write(str(self.text))
                self.file.flush()


class ProcessWriter(ProcessWriterBase):
    """ A subprocess that handles printing in another process.
        The text is updated by setting `self.text`.
    """
    nice_delay = 0.001
    lock = Lock()

    def __init__(self, text=None, file=None):
        self.file = file or sys.stdout
        self.piperecv, self.pipesend = Pipe()
        stop_flag = Value(c_bool, True)
        time_started = Value(c_double, 0)
        time_elapsed = Value(c_double, 0)
        super().__init__(
            self.piperecv,
            self.lock,
            stop_flag,
            time_started,
            time_elapsed,
            file=self.file,
        )
        # This will set self._text, and send it through the pipe initially.
        self.text = text or ''

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        if self.pipesend.writable:
            try:
                self.pipesend.send(self._text)
            except BrokenPipeError:
                # Something is very wrong.
                self.file.write('\nBroken pipe in ProgressProcess.\n')


class Progress(ProcessWriter):
    """ A subprocess that writes FrameLists and handles advancing frames.
        The text is updated by setting `self.text` or overriding
        `self.write()`.
    """
    join_str = ' '
    default_interval = 0.08
    default_format = '{frame} {text}'
    default_format_time = '{frame} {elapsed:>2.0f}s {text}'

    def __init__(
            self, text=None, frames=None, interval=0.08,
            fmt=None, show_time=False, char_delay=None, file=None):
        self.file = file or sys.stdout
        self.frames = frames or Frames.default

        if not self.frames:
            raise ValueError('Must have at least one frame. Got: {!r}'.format(
                self.frames
            ))

        # Delay in seconds between frame renders.
        self.interval = (interval or self.default_interval) - self.nice_delay
        # Format for the progress frame, optional time, and text.
        if show_time:
            default_fmt = self.default_format_time
        else:
            default_fmt = self.default_format
        self.fmt = fmt or default_fmt
        # Length of frames, used for setting the current frame.
        self.frame_len = len(self.frames)
        self.current_frame = 0
        # Time in seconds to delay between character writes.
        self.char_delay = char_delay or None
        # Keep track of the last message displayed, for char_delay animations.
        self._last_text = None
        # Initialize the basic ProgressProcess.
        super().__init__(
            text=text,
            file=self.file,
        )

    def __str__(self):
        """ String representation of a Progress is it's current frame string.
        """
        return self.fmt.format(
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

    def run(self):
        """ Overrides ProcessWriter.run, to handle KeyboardInterrupts better.
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
        """ Stop this progress, if it has been started. Otherwise, do nothing.
        """
        with self.lock:
            (
                Control().text(C(' ', style='reset_all'))
                .pos_restore().move_column(1).erase_line()
                .write(self.file)
            )
        super().stop()

    def write(self):
        """ Returns a single frame of the progress spinner to the terminal.
            This function updates the current frame after returning.
        """
        if self._last_text == self._text:
            char_delay = None
        else:
            char_delay = self.char_delay
            self._last_text = self._text
        with self.lock:
            (
                Control().move_column(1).pos_save().erase_line()
                .text(str(self))
                .write(file=self.file, delay=char_delay)
                .delay(self.interval)
            )
        self._advance_frame()
        return self.current_frame
