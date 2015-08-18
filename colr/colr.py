#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" colr.py
    A terminal color library for python, inspired by the javascript lib "clor".
    -Christopher Welborn 08-12-2015

    The MIT License (MIT)

    Copyright (c) 2015 Christopher Welborn

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
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.

"""
from functools import partial
from types import GeneratorType

__version__ = '0.0.3'

__all__ = [
    'Colr',
    'codes',
    'codeformat',
    'extbackformat',
    'extforeformat',
    'color',
]

# Names and corresponding base code number
_namemap = (
    ('black', 0),
    ('red', 1),
    ('green', 2),
    ('yellow', 3),
    ('blue', 4),
    ('magenta', 5),
    ('cyan', 6),
    ('white', 7)
)

# Build a module-level map of fore, back, and style names to escape code.
codeformat = '\033[{}m'.format
extforeformat = '\033[38;5;{}m'.format
extbackformat = '\033[48;5;{}m'.format


def _build_codes():
    """ Build code map, encapsulated to reduce module-level globals. """
    built = {
        'fore': {},
        'back': {},
        'style': {},
        'closing': '\033[m'
    }

    # Set codes for forecolors (30-37) and backcolors (40-47)
    for name, number in _namemap:
        built['fore'][name] = codeformat(30 + number)
        built['back'][name] = codeformat(40 + number)
        litename = 'light{}'.format(name)
        built['fore'][litename] = codeformat(90 + number)
        built['back'][litename] = codeformat(100 + number)

    # Set reset codes for fore/back.
    built['fore']['reset'] = codeformat(39)
    built['back']['reset'] = codeformat(49)

    # Map of code -> style name/alias.
    stylemap = (
        ('0', ['reset_all']),
        ('1', ['b', 'bright', 'bold']),
        ('2', ['d', 'dim']),
        ('3', ['i', 'italic']),
        ('4', ['u', 'underline', 'underlined']),
        ('5', ['f', 'flash']),
        ('7', ['h', 'highlight', 'hilight', 'hilite', 'reverse']),
        ('22', ['n', 'normal', 'none'])
    )
    # Set style codes.
    for code, names in stylemap:
        for alias in names:
            built['style'][alias] = codeformat(code)

    # Extended (256 color codes)
    for i in range(256):
        built['fore'][str(i)] = extforeformat(i)
        built['back'][str(i)] = extbackformat(i)

    return built

# Raw code map, available to users.
codes = _build_codes()


class Colr(object):

    """ This class colorizes text for an ansi terminal.

    """

    def __init__(self, text=None, fore=None, back=None, style=None):
        # Can be initialized with colored text, not required though.
        self.data = self.color(text or '', fore=fore, back=back, style=style)

    def __call__(self, text=None, fore=None, back=None, style=None):
        """ Append text to this Colr object. """
        self.data = ''.join((
            self.data,
            self.color(text=text, fore=fore, back=back, style=style)
        ))
        return self

    def __dir__(self):
        """ Compute the fake method names, and include them in a listing
            of this classes attributes.
        """

        def fmtcode(s):
            try:
                int(s)
                return 'f256_{}'.format(s)
            except ValueError:
                return s

        def fmtbgcode(s):
            try:
                int(s)
                return 'b256_{}'.format(s)
            except ValueError:
                return 'bg{}'.format(s)

        attrs = [fmtcode(k) for k in codes['fore']]
        attrs.extend(fmtbgcode(k) for k in codes['back'])
        attrs.extend(k for k in codes['style'])
        attrs.extend((
            'chained',
            'color_code',
            'color',
            'data',
            'format',
            'join',
            'print',
            'str'
        ))
        return attrs

    def __getattr__(self, attr):
        """ If the attribute matches a fore, back, or style name,
            return the color() function. Otherwise, return known
            attributes and raise AttributeError for others.
        """
        knownmethod = self._attr_to_method(attr)
        if knownmethod is not None:
            return knownmethod

        try:
            val = self.__getattribute__(attr)
        except AttributeError as ex:
            try:
                val = self.data.__getattribute__(attr)
            except AttributeError:
                raise AttributeError(ex)
        return val

    def __repr__(self):
        return repr(self.data)

    def __str__(self):
        return self.data

    def _attr_to_method(self, attr):
        """ Return the correct color function by method name.
            Uses `partial` to build kwargs on the `color` func.
            On failure/unknown name, returns None.
        """
        if attr in codes['fore']:
            # Fore method
            return partial(self.chained, fore=attr)
        elif attr in codes['style']:
            # Style method
            return partial(self.chained, style=attr)
        elif attr.startswith('bg'):
            # Back method
            name = attr[2:]
            if name in codes['back']:
                return partial(self.chained, back=name)
        elif attr.startswith('b256_'):
            # Back 256 method
            # Remove the b256_ portion.
            name = attr[5:]
            return partial(self.chained, back=name)
        elif attr.startswith('f256_'):
            # Fore 256 method
            name = attr[5:]
            return partial(self.chained, fore=name)
        return None

    def _iter_gradient(self, text, start, step=1, back=None, style=None):
        """ Yield colorized characters,
            using one of the 36-length gradients.
        """
        # Determine which 36-length gradient to start from.
        adj = divmod(start - 16, 36)[1]
        if adj > 0:
            start = start - adj

        # Build the color numbers needed to make a never-ending gradient.
        rows = []
        for c in range(0, 36, 6):
            rows.append([start + c + i for i in range(6)])
        numbers = []
        for i, r in enumerate(rows):
            if i % 2 != 0:
                numbers.extend(reversed(rows[i]))
            else:
                numbers.extend(rows[i])
        yield from self._iter_text_wave(
            text,
            numbers,
            step=step,
            back=back,
            style=style)

    def _iter_gradient_black(self, text, start, step=1, back=None, style=None):
        """ Yield colorized characters,
            within the 24-length black gradient.
        """
        if start < 232:
            start = 232
        elif start > 255:
            start = 255
        yield from self._iter_text_wave(
            text,
            list(range(start, 256)),
            step=step,
            back=back,
            style=style)

    def _iter_text_wave(self, text, numbers, step=1, back=None, style=None):
        """ Yield colorized characters from `text`, using a wave of `numbers`.
            Arguments:
                text     : String to be colorized.
                numbers  : A list/tuple of numbers (256 colors).
                step     : Number of characters to colorize per color.
                back     : Background color to use.
                style    : Style name to use.
        """
        pos = 0
        end = len(text)
        numbergen = self._iter_wave(numbers)
        for num in numbergen:
            lastchar = pos + step
            yield self.color(
                text[pos:lastchar],
                fore=num,
                back=back,
                style=style
            )
            if lastchar >= end:
                numbergen.send(True)
            pos = lastchar

    @staticmethod
    def _iter_wave(iterable, count=0):
        """ Move from beginning to end, and then end to beginning, a number of
            iterations through an iterable (must accept len(iterable)).
            Example:
                print(' -> '.join(_iter_wave('ABCD', count=8)))
                >> A -> B -> C -> D -> C -> B -> A -> B

            If `count` is less than 1, this will run forever.
            You can stop it by sending a Truthy value into the generator.
        """
        up = True
        pos = 0
        i = 0
        end = len(iterable)
        # Stop on count, or run forever.
        while (i < count) if count > 0 else True:
            try:
                stop = yield iterable[pos]
                # End of generator (user sent the stop signal)
                if stop:
                    break
            except IndexError:
                # End of iterable, when len(iterable) is < count.
                up = False

            # Change directions if needed, otherwise increment/decrement.
            if up:
                pos += 1
                if pos == end:
                    up = False
                    pos = end - 2
            else:
                pos -= 1
                if pos < 0:
                    up = True
                    pos = 1
            i += 1

    def chained(self, text=None, fore=None, back=None, style=None):
        """ Called by the various 'color' methods to colorize a single string.
            The RESET_ALL code is appended to the string unless text is empty.
            Raises ValueError on invalid color names.

            Arguments:
                text  : String to colorize, or None for  BG/Style change.
                fore  : Name of fore color to use.
                back  : Name of back color to use.
                style : Name of style to use.
        """
        self.data = ''.join((
            self.data,
            self.color(text=text, fore=fore, back=back, style=style)
        ))
        return self

    def color(self, text=None, fore=None, back=None, style=None):
        """ A method that colorizes strings, not Colr objects.
            Raises ValueError for invalid color names.
            The 'reset_all' code is appended if text is given.
        """
        return ''.join((
            self.color_code(fore=fore, back=back, style=style),
            text or '',
            codes['closing'] if text else ''
        ))

    def color_code(self, fore=None, back=None, style=None):
        """ Return the codes for this style/colors. """

        colorcodes = []
        resetcodes = []
        userstyles = {'style': style, 'back': back, 'fore': fore}
        for stype in userstyles:
            style = userstyles.get(stype, None)
            if not style:
                continue
            stylename = str(style).lower()
            # Get code number for this style.
            code = codes[stype].get(stylename, None)
            if not code:
                raise ValueError('Invalid color name/number: {}'.format(style))
            if stylename.startswith('reset'):
                resetcodes.append(code)
            else:
                colorcodes.append(code)
        # Reset codes come first, to not override colors.
        return ''.join((''.join(resetcodes), ''.join(colorcodes)))

    def format(self, *args, **kwargs):
        """ Like str.format, except it returns a Colr. """
        return self.__class__(self.data.format(*args, **kwargs))

    def gradient(self, text, start=0, step=1, back=None, style=None):
        """ Colorize a string gradient style, using 256 colors.
            Arguments:
                text  : String to colorize.
                start : Starting 256-color number.
                        The `start` will be adjusted if it is not within
                        bounds.
                        This will always be > 15.
                        This will be adjusted to fit within a 6-length
                        gradient, or the 24-length black/white gradient.
                step  : Number of characters to colorize per color.
                        This allows a "wider" gradient.
                        This will always be greater than 0.
                back  : Background color for this gradient (256 colors).
                style : Name of style to use for the gradient.

            Returns a Colr object with gradient text.
        """
        # The first 16 colors (0->15) are not allowed.
        if start < 16:
            start = 16

        step = abs(int(step))
        if step < 1:
            step = 1

        if start > 231:
            # Black gradient.
            method = self._iter_gradient_black
        else:
            method = self._iter_gradient

        return self.__class__(
            ''.join(
                method(text, start, step=step, back=back, style=style)
            )
        )

    def join(self, *colrs, **colorkwargs):
        """ Like str.join, except it returns a Colr.
            Arguments:
                colrs  : One or more Colrs. If a list or tuple is passed as an
                         argument it will be flattened.
            Keyword Arguments:
                fore, back, style...
                see color().
        """
        flat = []
        for clr in colrs:
            if isinstance(clr, (list, tuple, GeneratorType)):
                # Flatten any lists, at least once.
                flat.extend((str(c) for c in clr))
            else:
                flat.append(str(clr))

        if colorkwargs:
            fore = colorkwargs.get('fore', None)
            back = colorkwargs.get('back', None)
            style = colorkwargs.get('style', None)
            flat = (
                self.color(s, fore=fore, back=back, style=style)
                for s in flat
            )
        return self.__class__(self.data.join(flat))

    def print(self, *args):
        """ Chainable print method. Prints self.data and then clears it. """
        print(self, *args)
        self.data = ''
        return self

    def str(self):
        """ Alias for self.__str__ """
        return str(self)

# Shortcuts.
color = Colr().color

if __name__ == '__main__':
    print(
        Colr('warning', 'red')
        .join('[', ']', style='bright')(' ')
        .green('This module is meant to be imported.')
    )
    # 134
    print(Colr().gradient(
        'This is not a command-line tool, and should not be treated like one.',
        start=134,
        step=10,
        style='bright'
    ))
