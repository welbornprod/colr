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


class Progress(object):
    """ A command-line progress spinner inspired by Node's `orb` and
        `cli-spinners` packages.
    """
    join_str = ' '
    default_interval = 0.08
    nice_delay = 0.01

    def __init__(
            self, text=None, frames=None, interval=0.08,
            show_time=False, char_delay=None, file=None):
        self.file = file or sys.stdout
        self.frames = frames or Frames.default

        if not self.frames:
            raise ValueError('Must have at least one frame. Got: {!r}'.format(
                self.frames
            ))
        # Delay in seconds between frame renders.
        self.interval = (interval or self.default_interval) - self.nice_delay
        # Length of frames, used for setting the current frame.
        self.frame_len = len(self.frames)
        # Last frame index, used for setting the current frame.
        self.last_frame = self.frame_len - 1
        self.current_frame = 0
        # Whether to include the elapsed time in the text.
        self.show_time = show_time
        # Time in seconds to delay between character writes.
        # (doesn't include the spinner)
        self.char_delay = char_delay or None
        # The subprocess that runs the progress updates.
        self.process = None
        # A write lock, to synchronize terminal output.
        self.lock = Lock()
        # When set to True after `start()` is called, the progress loop is
        # cancelled. This is shared with the progress subprocess.
        # It can be accessed and set with the `self.stopped` property.
        self._stopped = Value(c_bool, True)
        # Time in seconds that this progress is started.
        # This is shared with the progress subprocess.
        # It can be accessed and set with the `self.time_started`
        # property.
        self._time_started = Value(c_double, 0)
        # Time elapsed since `start()` was called. This is updated after
        # every rendered frame.
        # This is shared with the progress subprocess.
        # It can be accessed and set with the `self.elapsed` property.
        self._time_elapsed = Value(c_double, 0)

        # This is a Pipe to send text updates to the subprocess that handles
        # progress updates.
        self.text_pipe = None
        # Initial text to display after the progress spinner/frame.
        self._text = str(text or '')
        # Keep track of the last message displayed, for char_delay animations.
        self._last_text = None

    def __str__(self):
        """ String representation of a Progress is it's current frame string.
        """
        framechar = self.frames[self.current_frame]
        if self.show_time:
            s = '{:>2.0f}s {}'.format(self.elapsed, self.text)
        else:
            s = str(self.text)
        return self.join_str.join((str(framechar), s))

    def _advance_frame(self):
        """ Sets `self.current_frame` to the next frame, looping to the
            beginning if needed.
        """
        self.current_frame += 1
        if self.current_frame > self.last_frame:
            self.current_frame = 0

    def frame_control(self):
        """ Return the current frame and optional time, as a Control.
        """
        framechar = self.frames[self.current_frame]
        c = Control().text(str(framechar))
        if self.show_time:
            c = c.text('{:>2.0f}s'.format(self.elapsed))
        return c

    @property
    def elapsed(self):
        """ This is a wrapper for the shared state Value of
            `elapsed`.
        """
        return self._time_elapsed.value

    @elapsed.setter
    def elapsed(self, value):
        with self._time_elapsed.get_lock():
            self._time_elapsed.value = value

    def _loop(
            self, *,
            pipe=None, stopped_flag=None,
            time_started=None, time_elapsed=None, write_lock=None):
        """ A loop that only stops when the multiprocessing.Value, `flag`,
            is set to True.
        """
        with stopped_flag.get_lock():
            stopped_flag.value = False
        with time_elapsed.get_lock():
            time_elapsed.value = 0
        with time_started.get_lock():
            time_started.value = time()
        with write_lock:
            Control().cursor_hide().write(self.file)
        try:
            while not stopped_flag.value:
                if pipe.poll():
                    self._text = pipe.recv()
                with write_lock:
                    self._render_frame()
                with time_elapsed.get_lock():
                    time_elapsed.value = time() - time_started.value
                # Sleep to give the processor some freedom.
                sleep(self.nice_delay)
        except KeyboardInterrupt:
            self.stop()
        finally:
            Control().cursor_show().write(self.file)

    def _render_frame(self):
        """ Wrtite a single frame of the progress spinner to the terminal.
            This function updates the current frame after writing.
        """
        if self._last_text == self._text:
            char_delay = None
        else:
            char_delay = self.char_delay
            self._last_text = self._text
        (
            Control().move_column(1).pos_save().erase_line().chained(
                self.frame_control()
            )
            .write(file=self.file)
            .text(' {}'.format(self._text))
            .pos_restore()
            .write(file=self.file, delay=char_delay)
            .delay(self.interval)
        )

        self._advance_frame()
        return self.current_frame

    def start(self):
        """ Start the progress. It will not stop until `self.stop()` is
            called. However, it will not block either.
        """
        # Text is updated by sending it through a pipe to the subprocess.
        # The `self.text` property handles sending, while the `_loop`
        # receives.
        self.text_pipe, pipecli = Pipe(duplex=True)
        # This instance and the sub process instance must share the same
        # flags/values, so they are passed as keyword arguments.
        self.process = Process(
            target=self._loop,
            name='Progress.loop',
            kwargs={
                'pipe': pipecli,
                'stopped_flag': self._stopped,
                'time_started': self._time_started,
                'time_elapsed': self._time_elapsed,
                'write_lock': self.lock,
            }
        )
        self.process.start()

        return self.process

    def stop(self):
        """ Stop this progress, if it has been started. Otherwise, do nothing.
        """
        with self.lock:
            (
                Control().text(C(' ', style='reset_all'))
                .move_column(1).erase_line()
                .write(self.file)
            )
        self.stopped = True

    @property
    def stopped(self):
        """ This is a wrapper for the shared state Value of
            `stopped`.
        """
        return self._stopped.value

    @stopped.setter
    def stopped(self, value):
        with self._stopped.get_lock():
            self._stopped.value = value

    @property
    def text(self):
        """ This is a wrapper for the shared state Value of
            `text`.
        """
        return self._text

    @text.setter
    def text(self, value):
        self._text = str(value)
        # Setting the text property will send the value to the subprocess,
        # if it's available.
        if self.text_pipe is not None:
            try:
                self.text_pipe.send(self._text)
            except BrokenPipeError:
                # Something has gone horribly wrong.
                self.file.write('\nBroken pipe.\n')

    @property
    def time_started(self):
        """ This is a wrapper for the shared state Value of
            `time_started`.
        """
        return self._time_started.value

    @time_started.setter
    def time_started(self, value):
        with self._time_started.get_lock():
            self._time_started.value = value
