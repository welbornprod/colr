#!/usr/bin/env python3
""" Colr - Control Codes
    Codes to deal with cursor movement, advanced printing, or overwriting
    text in the terminal.

    Some of this documentation comes from:
        http://ascii-table.com/ansi-escape-sequences.php
        and
        https://en.wikipedia.org/wiki/ANSI_escape_code

    -Christopher Welborn 3-6-17
"""

import sys
from enum import Enum

__all__ = [
    'cursor',
    'erase',
    'move',
    'pos',
    'position',
    'scroll',
]

escape_sequence = '\033['


class EraseMethod(Enum):
    END = 0
    START = 1
    ALL = ALL_MOVE = 2
    ALL_ERASE = 3
    ALL_MOVE_ERASE = 4

    def __str__(self):
        return str(self.value)


class CursorCodes(object):
    """ Escape codes that deal with the cursor itself. """
    @staticmethod
    def hide():
        """ Hide the cursor.

            Esc[?25l
        """
        return EscapeCode('?25l')

    @staticmethod
    def show():
        """ Show the cursor.

            Esc[?25h
        """
        return EscapeCode('?25h')


class EraseCodes(object):
    """ Escape codes that erase. """

    @staticmethod
    def display(method=EraseMethod.ALL_MOVE):
        """ Clear the screen or part of the screen, and possibly moves the cursor
            to the "home" position (0, 0). See `method` argument below.

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
        accepted_methods = ('0', '1', '2', '3', '4')
        methodstr = str(method)
        if methodstr not in accepted_methods:
            raise ValueError('Invalid method, expected {}. Got: {!r}'.format(
                ', '.join(accepted_methods),
                method,
            ))
        if methodstr == '4':
            methods = (2, 3)
        else:
            methods = (method, )
        return EscapeCode(
            ''.join(str(EscapeCode('{}J'.format(m))) for m in methods)
        )

    @staticmethod
    def line(method=EraseMethod.ALL):
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
        methods = ('0', '1', '2')
        if str(method) not in methods:
            raise ValueError('Invalid method, expected {}. Got: {!r}'.format(
                ', '.join(methods),
                method,
            ))
        return EscapeCode('{}K'.format(method))


class EscapeCode(object):
    """ Responsible for creating a full escape code sequence, with helper
        methods for the resulting string.
    """
    def __init__(self, code):
        """ Initialize an escape code. """
        if not code:
            raise ValueError(
                'Empty/falsey code is not allowed. Got: {!r}'.format(code)
            )
        codestr = str(code)
        if codestr.startswith(escape_sequence):
            # Already an escape sequence.
            self.code = codestr
        else:
            # Shorter form used.
            self.code = ''.join((escape_sequence, codestr))

    def __repr__(self):
        return repr(self.code)

    def __str__(self):
        return str(self.code)

    def repeat(self, count=1):
        """ Return an EscapeCode containing this escape code repeated `count`
            times, joined by ';'.
            If `count` is less than 1, '' is returned.
        """
        # Not using for-loop, because the id doesn't matter.
        # This multiplication method is faster than [s for _ in range(count)].
        return self.__class__(';'.join([str(self)] * count))

    def write(self, file=sys.stdout):
        file.write(str(self))
        file.flush()


class MoveCodes(object):
    """ Escape codes that move the cursor. """

    @staticmethod
    def back(columns=1):
        """ Move the cursor back a number of columns.

            Esc[<columns>D:
            Moves the cursor back by the specified number of columns without
            changing lines. If the cursor is already in the leftmost column,
            ANSI.SYS ignores this sequence.
        """
        return EscapeCode('{}D'.format(columns))

    @staticmethod
    def carriage_return():
        """ Move the cursor to the beginning of the line, using \\r.
            This should act just like `move_column(1)`.
        """
        return '\r'

    @staticmethod
    def column(column=1):
        """ Move the cursor to a specific column, default 1.

            Esc[<column>G
        """
        return EscapeCode('{}G'.format(column))

    @staticmethod
    def down(lines=1):
        """ Move the cursor down a number of lines.

            Esc[<lines>B:
            Moves the cursor down by the specified number of lines without
            changing columns. If the cursor is already on the bottom line,
            ANSI.SYS ignores this sequence.
        """
        return EscapeCode('{}B'.format(lines))

    @staticmethod
    def forward(columns=1):
        """ Move the cursor forward a number of columns.

            Esc[<columns>C:
            Moves the cursor forward by the specified number of columns
            without changing lines. If the cursor is already in the rightmost
            column, ANSI.SYS ignores this sequence.
        """
        return EscapeCode('{}C'.format(columns))

    @staticmethod
    def next(lines=1):
        """ Move the cursor to the beginning of the line, a number of lines down.
            Default: 1

            Esc[<lines>E
        """
        return EscapeCode('{}E'.format(lines))

    @staticmethod
    def pos(line=1, column=1):
        """ Move the cursor to a new position. Values are 1-based, and default
            to 1.

            Esc[<line>;<column>H
            or
            Esc[<line>;<column>f
        """
        return EscapeCode('{line};{col}H'.format(line=line, col=column))

    @staticmethod
    def prev(lines=1):
        """ Move the cursor to the beginning of the line, a number of lines up.
            Default: 1

            Esc[<lines>F
        """
        return EscapeCode('{}F'.format(lines))

    @staticmethod
    def up(lines=1):
        """ Move the cursor up a number of lines.

            Esc[ValueA:
            Moves the cursor up by the specified number of lines without
            changing columns. If the cursor is already on the top line,
            ANSI.SYS ignores this sequence.
        """
        return EscapeCode('{}A'.format(lines))


# Alias for move.carriage_return, since 'return' is a keyword.
MoveCodes.ret = MoveCodes.carriage_return


class PositionCodes(object):
    """ Escape codes that deal with the current cursor position. """

    @staticmethod
    def restore():
        """ Restore cursor position saved with `save()`.

            Esc[u:
            Returns the cursor to the position stored by the
            'save cursor position' sequence (`restore()`).
        """
        return EscapeCode('u')

    @staticmethod
    def save():
        """ Save current cursor position. Can be restored with `restore()`.

            Esc[s:
            Saves the current cursor position. You can move the cursor to the
            saved cursor position by using the 'restore cursor position'
            sequence (`restore()`).
        """
        return EscapeCode('s')


# Alias for move.pos, since both deal with moving/positions.
PositionCodes.set = MoveCodes.pos


class ScrollCodes(object):
    """ Escape codes for scrolling the window. """

    @staticmethod
    def down(lines=1):
        """ Scroll the whole page down a number of lines, new lines are added
            to the top.

            Esc[<lines>T
        """
        return EscapeCode('{}T'.format(lines))

    @staticmethod
    def up(lines=1):
        """ Scroll the whole page up a number of lines, new lines are added
            to the bottom.

            Esc[<lines>S
        """
        return EscapeCode('{}S'.format(lines))


cursor = CursorCodes()
erase = EraseCodes()
move = MoveCodes()
position = pos = PositionCodes()
scroll = ScrollCodes()
