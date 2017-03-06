#!/usr/bin/env python3
""" Colr - Controls
    Functions to deal with cursor movement, advanced printing, or overwriting
    text in the terminal.

    Some of this documentation comes from:
        http://ascii-table.com/ansi-escape-sequences.php
        and
        https://en.wikipedia.org/wiki/ANSI_escape_code

    -Christopher Welborn 3-6-17
"""
import sys
from time import sleep
from contextlib import suppress


def cursor_hide(file=sys.stdout):
    """ Hide the cursor. """
    file.write('\033[?25l')
    file.flush()


def cursor_show(file=sys.stdout):
    """ Show the cursor. """
    file.write('\033[?25h')
    file.flush()


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


def erase_display(method=2, file=sys.stdout):
    """ Clear the screen or part of the screen, and possibly moves the cursor
        to the "home" position (0, 0). See `method` argument below.

        Esc[<method>J

        Arguments:
            method: One of these possible values:
                        0 : Clear from cursor to the end of the screen.
                        1 : Clear from cursor to the beginning of the screen.
                        2 : Clear all, and move home.
                        3 : Clear all, and erase scrollback buffer.
                        4 : Like doing 2 and 3 in succession.
                            This is a feature of Colr, and is not standard.
                    Default: 2
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
    for m in methods:
        file.write('\033[{}J'.format(m))
        file.flush()


def erase_line(method=2, file=sys.stdout):
    """ Erase a line, or part of a line. See `method` argument below.
        Cursor position does not change.

        Esc[<method>K

        Arguments:
            method : One of these possible values:
                        0 : Clear from cursor to the end of the line.
                        1 : Clear from cursor to the beginning of the line.
                        2 : Clear the entire line.
                     Default: 2
    """
    methods = ('0', '1', '2')
    if str(method) not in methods:
        raise ValueError('Invalid method, expected {}. Got: {!r}'.format(
            ', '.join(methods),
            method,
        ))
    file.write('\033[{}K'.format(method))
    file.flush()


def move_back(columns=1, file=sys.stdout):
    """ Move the cursor back a number of columns.

        Esc[<columns>D:
        Moves the cursor back by the specified number of columns without
        changing lines. If the cursor is already in the leftmost column,
        ANSI.SYS ignores this sequence.
    """
    file.write('\033[{}D'.format(columns))
    file.flush()


def move_column(column=1, file=sys.stdout):
    """ Move the cursor to a certain column, default 1.

        Esc[<column>G
    """
    file.write('\033[{}G'.format(column))
    file.flush()


def move_down(lines=1, file=sys.stdout):
    """ Move the cursor down a number of lines.

        Esc[<lines>B:
        Moves the cursor down by the specified number of lines without
        changing columns. If the cursor is already on the bottom line,
        ANSI.SYS ignores this sequence.
    """
    file.write('\033[{}B'.format(lines))
    file.flush()


def move_forward(columns=1, file=sys.stdout):
    """ Move the cursor forward a number of columns.

        Esc[<columns>C:
        Moves the cursor forward by the specified number of columns without
        changing lines. If the cursor is already in the rightmost column,
        ANSI.SYS ignores this sequence.
    """
    file.write('\033[{}C'.format(columns))
    file.flush()


def move_next(lines=1, file=sys.stdout):
    """ Move the cursor to the beginning of the line, a number of lines down.
        Default: 1

        Esc[<lines>E
    """
    file.write('\033[{}E'.format(lines))
    file.flush()


def move_pos(line=1, column=1, file=sys.stdout):
    """ Move the cursor to a new position. Values are 1-based, and default
        to 1.

        Esc[<line>;<column>H
        or
        Esc[<line>;<column>f
    """
    file.write('\033[{line};{col}H'.format(line=line, col=column))
    file.flush()


def move_prev(lines=1, file=sys.stdout):
    """ Move the cursor to the beginning of the line, a number of lines up.
        Default: 1

        Esc[<lines>F
    """
    file.write('\033[{}F'.format(lines))
    file.flush()


def move_return(file=sys.stdout):
    """ Move the cursor to the beginning of the line, using \r.
        This should act just like `move_column(1)`.
    """
    file.write('\r')
    file.flush()


def move_up(lines=1, file=sys.stdout):
    """ Move the cursor up a number of lines.

        Esc[ValueA:
        Moves the cursor up by the specified number of lines without changing
        columns. If the cursor is already on the top line, ANSI.SYS ignores
        this sequence.
    """
    file.write('\033[{}A'.format(lines))
    file.flush()


def pos_restore(file=sys.stdout):
    """ Restore cursor position saved with `pos_save()`.

        Esc[u:
        Returns the cursor to the position stored by the
        'save cursor position' sequence (`pos_restore()`).
    """
    file.write('\033[u')
    file.flush()


def pos_save(file=sys.stdout):
    """ Save current cursor position.

        Esc[s:
        Saves the current cursor position. You can move the cursor to the
        saved cursor position by using the 'restore cursor position' sequence
        (`pos_restore()`).
    """
    file.write('\033[s')
    file.flush()


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
    erase_line()
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
    file.write('\033[{}T'.format(lines))


def scroll_up(lines=1, file=sys.stdout):
    """ Scroll the whole page up a number of lines, new lines are added to
        the bottom.

        Esc[<lines>S
    """
    file.write('\033[{}S'.format(lines))


def _example(delay=0.05):
    """ This is a test of the print_* functions. """
    from random import randint
    print(C(
        'This file is not meant to be executed from the command line.\n',
        'red'
    ))
    sleep(0.5)
    # This is just a rough estimate, based on my machine.
    multiplier = 440
    print(
        C(
            'This will probably take about {:0.0f} seconds.\n'.format(
                delay * multiplier
            )
        ).rainbow()
    )
    sleep(0.5)
    print_overwrite(
        '...but you get to see some text animations.',
        delay=delay,
    )
    print(C('\nI\'m just gonna put this: ', 'cyan'), end='')
    for val in (C('here', 'red'), C('there', 'green'), C('nowhere', 'blue')):
        sleep(delay)
        print_inplace(val, delay=delay)

    move_column(1)
    for col in range(len('I\'m just gonna put this: nowhere')):
        print_flush(C('X', randint(0, 255)), end='')
        sleep(delay)
    erase_line()
    print('\nFinished with print functions.\n')


def _example2(delay=0.05):
    """ This is a rough test of the scroll_* functions. """
    linedelay = delay * 6
    height = 6
    height_dbl = height * 2
    start_colr = 255 - height_dbl
    for i in range(height):
        print_flush(
            C('Scrolled to {} lines.'.format((i * 2) + 1), start_colr + i),
            end='',
        )
        scroll_up(2)
        move_column(1)
        sleep(linedelay)
    sleep(0.5)
    for _ in range(height_dbl):
        # Scroll down to start writing again.
        scroll_down()
    for i in range(height_dbl):
        print_flush(
            C('Scrolled down, overwriting {}.'.format(i + 1), start_colr + i)
        )
        sleep(linedelay)

    print('\nFinished with scroll functions.\n')


def _example3(delay=0.025):
    """ This is a rough test of the move_* functions. """
    width = 48
    height = 24
    # Draw a block of Xs.
    print_flush(C('\n'.join(('X' * width) for _ in range(height))).rainbow())
    move_up(height)
    width_half = width // 2

    # Draw a line down the middle.
    move_column(width_half)
    for _ in range(height - 1):
        print_flush(C('|', 'blue'), end='')
        sleep(delay)
        move_back(1)
        move_down()

    # Draw a line at the top left half.
    move_up(height - 1)
    move_column(1)
    for _ in range(width_half):
        print_flush(C('-', 'blue'), end='')
        sleep(delay)
    # Draw a line at the bottom right half.
    move_down(height - 1)
    move_back(1)
    for _ in range(width_half + 1):
        print_flush(C('-', 'blue'), end='')
        sleep(delay)

    # Erase the right half.
    move_column(width_half + 1)
    erase_line(0)
    for _ in range(height - 1):
        move_up()
        erase_line(0)
        sleep(delay)

    # Erase the left half.
    move_column(width_half - 1)
    erase_line(1)
    for _ in range(height - 1):
        move_down()
        erase_line(1)
        sleep(delay)

    # Widen the "stick".
    start_colr = 255 - width_half
    for colrval in range(start_colr + width_half, start_colr, -1):
        move_up(height - 1)
        move_column(width + (start_colr - colrval))
        print_flush(C('-', colrval), end='')
        for _ in range(height - 2):
            move_down()
            move_back()
            print_flush(C('|', colrval), end='')
        move_down()
        move_back()
        print_flush(C('-', colrval), end='')
        sleep(delay)

    # Shrink the "sticks".
    move_up(height - 1)
    chardelay = delay / 3
    for _ in range(height // 2):
        move_column(width)
        for _ in range(width_half + 2):
            erase_line(0)
            move_back()
            sleep(chardelay)
        move_down()
        move_column(width_half)
        for _ in range(width_half):
            print_flush(' ', end='')
            sleep(chardelay)
        move_down()

    # Move to the end.
    move_down(height + 1)
    move_column(width)
    print('\nFinished with move functions.\n')


if __name__ == '__main__':
    import os
    sys.path.insert(0, os.path.abspath('../'))
    from colr import Colr as C
    delay = 0.05
    cursor_hide()
    try:
        _example(delay=delay)
        _example2(delay=delay)
        _example3(delay=delay / 2)
        cursor_show()
        msg = 'Erase the terminal contents/scrollback? (y/N): '
        if input(msg).lower().strip().startswith('y'):
            erase_display(4)
    except KeyboardInterrupt:
        print('\nUser cancelled.\n', file=sys.stderr)
    finally:
        cursor_show()
