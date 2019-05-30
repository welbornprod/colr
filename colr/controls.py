#!/usr/bin/env python3
""" Colr - Controls
    Functions to deal with cursor movement, advanced printing, or overwriting
    text in the terminal.

    Some of this documentation comes from:
        http://ascii-table.com/ansi-escape-sequences.php
        and
        https://en.wikipedia.org/wiki/ANSI_escape_code

    -Christopher Welborn 3-6-17

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

import sys
from contextlib import suppress
from time import sleep

from .base import (
    ChainedBase,
)
from .control_codes import (
    EraseMethod,
    cursor,
    erase,
    escape_sequence,
    move,
    position,
    scroll,
)


def cursor_hide(file=sys.stdout):
    """ Hide the cursor. """
    cursor.hide().write(file=file)


def cursor_show(file=sys.stdout):
    """ Show the cursor. """
    cursor.show().write(file=file)


def ensure_tty(file=sys.stdout):
    """ Ensure a file object is a tty. It must have an `isatty` method that
        returns True.
        TypeError is raised if the method doesn't exist, or returns False.
    """
    isatty = getattr(file, 'isatty', None)
    if isatty is None:
        raise TypeError(
            'Cannot detect tty, file has no `isatty` method: {}'.format(
                getattr(file, 'name', type(file).__name__)
            )
        )
    if not isatty():
        raise TypeError(
            'This will not work, file object is not a tty: {}'.format(
                getattr(file, 'name', type(file).__name__)
            )
        )
    return True


def erase_display(method=EraseMethod.ALL_MOVE, file=sys.stdout):
    """ Clear the screen or part of the screen, and possibly moves the cursor
        to the "home" position (1, 1). See `method` argument below.

        Esc[<method>J

        Arguments:
            method: One of these possible values:
                        EraseMethod.END or 0:
                            Clear from cursor to the end of the screen.
                        EraseMethod.START or 1:
                            Clear from cursor to the start of the screen.
                        EraseMethod.ALL_MOVE or 2:
                            Clear all, and move home.
                        EraseMethod.ALL_ERASE or 3:
                            Clear all, and erase scrollback buffer.
                        EraseMethod.ALL_MOVE_ERASE or 4:
                            Like doing 2 and 3 in succession.
                            This is a feature of Colr. It is not standard.
                    Default: EraseMethod.ALL_MOVE (2)
    """
    erase.display(method).write(file=file)


def erase_line(method=EraseMethod.ALL, file=sys.stdout):
    """ Erase a line, or part of a line. See `method` argument below.
        Cursor position does not change.

        Esc[<method>K

        Arguments:
            method : One of these possible values:
                        EraseMethod.END or 0:
                            Clear from cursor to the end of the line.
                        EraseMethod.START or 1:
                            Clear from cursor to the start of the line.
                        EraseMethod.ALL or 2:
                            Clear the entire line.
                     Default: EraseMethod.ALL (2)
    """
    erase.line(method).write(file=file)


def move_back(columns=1, file=sys.stdout):
    """ Move the cursor back a number of columns.

        Esc[<columns>D:
        Moves the cursor back by the specified number of columns without
        changing lines. If the cursor is already in the leftmost column,
        ANSI.SYS ignores this sequence.
    """
    move.back(columns).write(file=file)


def move_column(column=1, file=sys.stdout):
    """ Move the cursor to the specified column, default 1.

        Esc[<column>G
    """
    move.column(column).write(file=file)


def move_down(lines=1, file=sys.stdout):
    """ Move the cursor down a number of lines.

        Esc[<lines>B:
        Moves the cursor down by the specified number of lines without
        changing columns. If the cursor is already on the bottom line,
        ANSI.SYS ignores this sequence.
    """
    move.down(lines).write(file=file)


def move_forward(columns=1, file=sys.stdout):
    """ Move the cursor forward a number of columns.

        Esc[<columns>C:
        Moves the cursor forward by the specified number of columns without
        changing lines. If the cursor is already in the rightmost column,
        ANSI.SYS ignores this sequence.
    """
    move.forward(columns).write(file=file)


def move_next(lines=1, file=sys.stdout):
    """ Move the cursor to the beginning of the line, a number of lines down.
        Default: 1

        Esc[<lines>E
    """
    move.next(lines).write(file=file)


def move_pos(line=1, column=1, file=sys.stdout):
    """ Move the cursor to a new position. Values are 1-based, and default
        to 1.

        Esc[<line>;<column>H
        or
        Esc[<line>;<column>f
    """
    move.pos(line=line, column=column).write(file=file)


def move_prev(lines=1, file=sys.stdout):
    """ Move the cursor to the beginning of the line, a number of lines up.
        Default: 1

        Esc[<lines>F
    """
    move.prev(lines).write(file=file)


def move_return(file=sys.stdout):
    """ Move the cursor to the beginning of the line, using \r.
        This should act just like `move_column(1)`.
    """
    move.carriage_return().write(file=file)


move_carriage_return = move_ret = move_return


def move_up(lines=1, file=sys.stdout):
    """ Move the cursor up a number of lines.

        Esc[ValueA:
        Moves the cursor up by the specified number of lines without changing
        columns. If the cursor is already on the top line, ANSI.SYS ignores
        this sequence.
    """
    move.up(lines).write(file=file)


def pos_restore(file=sys.stdout):
    """ Restore cursor position saved with `pos_save()`.

        Esc[u:
        Returns the cursor to the position stored by the
        'save cursor position' sequence (`pos_restore()`).
    """
    position.restore().write(file=file)


def pos_save(file=sys.stdout):
    """ Save current cursor position.

        Esc[s:
        Saves the current cursor position. You can move the cursor to the
        saved cursor position by using the 'restore cursor position' sequence
        (`pos_restore()`).
    """
    position.save().write(file=file)


# Alias for move_pos, since both deal with moving/positions.
pos_set = move_pos


def print_inplace(*args, **kwargs):
    """ Save cursor position, write some text, and then restore the position.
        Arguments:
            Same as `print()`.

        Keyword Arguments:
            Same as `print()`, except `end` defaults to '' (empty str),
            and these:
                delay : Time in seconds between character writes.
    """
    kwargs.setdefault('file', sys.stdout)
    kwargs.setdefault('end', '')
    pos_save(file=kwargs['file'])
    delay = None
    with suppress(KeyError):
        delay = kwargs.pop('delay')
    if delay is None:
        print(*args, **kwargs)
    else:
        for c in kwargs.get('sep', ' ').join(str(a) for a in args):
            kwargs['file'].write(c)
            kwargs['file'].flush()
            sleep(delay)
        if kwargs['end']:
            kwargs['file'].write(kwargs['end'])
    pos_restore(file=kwargs['file'])
    # Must flush to see changes.
    kwargs['file'].flush()


def print_flush(*args, **kwargs):
    """ Like `print()`, except the file is `.flush()`ed afterwards. """
    kwargs.setdefault('file', sys.stdout)
    print(*args, **kwargs)
    kwargs['file'].flush()


def print_overwrite(*args, **kwargs):
    """ Move to the beginning of the current line, and print some text.
        Arguments:
            Same as `print()`.

        Keyword Arguments:
            Same as `print()`, except `end` defaults to '' (empty str),
            and these:
                delay : Time in seconds between character writes.
    """
    kwargs.setdefault('file', sys.stdout)
    kwargs.setdefault('end', '')
    delay = None
    with suppress(KeyError):
        delay = kwargs.pop('delay')
    erase_line(file=kwargs['file'])
    # Move to the beginning of the line.
    move_column(1, file=kwargs['file'])
    if delay is None:
        print(*args, **kwargs)
    else:
        for c in kwargs.get('sep', ' ').join(str(a) for a in args):
            kwargs['file'].write(c)
            kwargs['file'].flush()
            sleep(delay)
        if kwargs['end']:
            kwargs['file'].write(kwargs['end'])
    kwargs['file'].flush()


def scroll_down(lines=1, file=sys.stdout):
    """ Scroll the whole page down a number of lines, new lines are added to
        the top.

        Esc[<lines>T
    """
    scroll.down(lines).write(file=file)


def scroll_up(lines=1, file=sys.stdout):
    """ Scroll the whole page up a number of lines, new lines are added to
        the bottom.

        Esc[<lines>S
    """
    scroll.up(lines).write(file=file)


class Control(ChainedBase):
    """ Like Colr, but for control codes. It allows method chaining to build
        up control sequences.
    """

    def __init__(self, data=None):
        """ Initialize a new Control str. """
        self.data = str(data or '')

    def cursor_hide(self):
        """ Hide the cursor. """
        return self.chained(cursor.hide())

    def cursor_show(self):
        """ Show the cursor. """
        return self.chained(cursor.show())

    def delay(self, seconds):
        """ `time.sleep(seconds)`, and return self. """
        sleep(seconds)
        return self

    def erase_display(self, method=EraseMethod.ALL_MOVE):
        """ Clear the screen or part of the screen.
            Arguments:
                method: One of these possible values:
                            EraseMethod.END or 0:
                                Clear from cursor to the end of the screen.
                            EraseMethod.START or 1:
                                Clear from cursor to the start of the screen.
                            EraseMethod.ALL_MOVE or 2:
                                Clear all, and move home.
                            EraseMethod.ALL_ERASE or 3:
                                Clear all, and erase scrollback buffer.
                            EraseMethod.ALL_MOVE_ERASE or 4:
                                Like doing 2 and 3 in succession.
                                This is a feature of Colr. It is not standard.
                        Default: EraseMethod.ALL_MOVE (2)
        """
        return self.chained(erase.display(method))

    def erase_line(self, method=EraseMethod.ALL):
        """ Erase a line, or part of a line.
            Arguments:
                method : One of these possible values:
                            EraseMethod.END or 0:
                                Clear from cursor to the end of the line.
                            EraseMethod.START or 1:
                                Clear from cursor to the start of the line.
                            EraseMethod.ALL or 2:
                                Clear the entire line.
                         Default: EraseMethod.ALL (2)
        """
        return self.chained(erase.line(method=method))

    def last_code(self):
        """ Return the last escape code in `self.data`.
            If no escape codes are found, '' is returned.
        """
        if escape_sequence not in self.data:
            return ''
        codes = self.data.split(escape_sequence)
        lastcode = codes[-1]
        return ''.join((escape_sequence, lastcode)) if lastcode else ''

    def move_back(self, columns=1):
        """ Move the cursor back a number of columns.
            Default: 1
        """
        return self.chained(move.back(columns))

    def move_carriage_return(self):
        """ Move the cursor to the beginning of the line, using \\r.
            This is the same as `self.move_column(1)`.
        """
        return self.chained(move.carriage_return())

    def move_column(self, column=1):
        """ Move the cursor to a specific column.
            Default: 1
        """
        return self.chained(move.column(column))

    def move_down(self, lines=1):
        """ Move the cursor down a number of lines.
            Default: 1
        """
        return self.chained(move.down(lines))

    def move_forward(self, columns=1):
        """ Move the cursor forward a number of columns.
            Default: 1
        """
        return self.chained(move.forward(columns))

    def move_next(self, lines=1):
        """ Move the cursor to the beginning of the line, a number of lines
            down.
            Default: 1
        """
        return self.chained(move.next(lines))

    def move_pos(self, line=1, column=1):
        """ Move the cursor to a new position.
            Default: line 1, column 1
        """
        return self.chained(move.pos(line=line, column=column))

    def move_prev(self, lines=1):
        """ Move the cursor to the beginning of the line, a number of lines
            up.
            Default: 1
        """
        return self.chained(move.prev(lines))

    def move_up(self, lines=1):
        """ Move the cursor up a number of lines.
            Default: 1
        """
        return self.chained(move.up(lines))

    def pos_restore(self):
        """ Restore the cursor position saved with `self.pos_save()`.
        """
        return self.chained(position.restore())

    def pos_save(self):
        """ Save current cursor position. Can be restored with
            `self.pos_restore()`.
        """
        return self.chained(position.save())

    def repeat(self, count=2):
        """ Repeat the last control code a number of times.
            Returns a new Control with this one's data and the repeated code.
        """
        # Subtracting one from the count means the code mentioned is
        # truly repeated exactly `count` times.
        # Control().move_up().repeat(3) ==
        # Control().move_up().move_up().move_up()
        try:
            return self.__class__(''.join((
                str(self),
                self.last_code() * (count - 1),
            )))
        except TypeError as ex:
            raise TypeError(
                '`count` must be an integer. Got: {!r}'.format(count)
            ) from ex

    def repeat_all(self, count=2):
        """ Repeat this entire Control code a number of times.
            Returns a new Control with this one's data repeated.
        """
        try:
            return self.__class__(''.join(str(self) * count))
        except TypeError:
            raise TypeError(
                '`count` must be an integer. Got: {!r}'.format(count)
            )

    def scroll_down(self, lines=1):
        """ Scroll the whole page down a number of lines, new lines are added
            to the top.
        """
        return self.chained(scroll.down(lines))

    def scroll_up(self, lines=1):
        """ Scroll the whole page up a number of lines, new lines are added
            to the bottom.
        """
        return self.chained(scroll.up(lines))

    def text(self, text):
        """ Add some text to this Control sequence. """
        return self.chained(text)


# Method aliases
# Alias for move_pos, because they both deal with cursor positions.
Control.pos_set = Control.move_pos  # type: ignore
# Shorter aliases for some move methods.
Control.move_fwd = Control.move_forward
Control.move_return = Control.move_carriage_return
Control.move_ret = Control.move_carriage_return


if __name__ == '__main__':
    # There are no tests for these two statements, but they have been tested
    # manually for a basic sanity-check.
    print(
        '\n'.join((
            'This file is not meant to run from the command line.',
            'If you\'ve cloned the repo you can run:',
            '    ./test/run_controls.py',
            'It will show some examples for Colr.controls.',
        )),
        file=sys.stderr
    )
    sys.exit(1)
