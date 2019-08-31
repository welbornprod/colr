#!/usr/bin/env python3

""" colr/base.py

    Classes/functions to support the chained string classes that Colr uses,
    like Colr and Control.

    -Christopher Welborn 08-12-2015

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
import re
import sys
from collections.abc import Sequence
from contextlib import suppress
from functools import total_ordering
from time import sleep
from types import GeneratorType
from typing import (
    Dict,
    List,
    Union,
)

__version__ = '0.9.1'

_codepats = (
    # Colors.
    r'(([\d;]+)?m{1})',
    # Cursor show/hide.
    r'(\?25l)',
    r'(\?25h)',
    # Move position.
    r'(([\d]+[;])?([\d]+[Hf]))',
    # Save/restore position.
    r'([su])',
    # Others (move, erase).
    r'([\d]+[ABCDEFGHJKST])',
)

closing_code = '\033[0m'

# Used to strip escape codes from a string.
codepat = re.compile(
    r'\033\[({})'.format('|'.join(_codepats))
)
# Used to grab codes from a string.
codegrabpat = re.compile(r'\033\[[\d;]+?m{1}')


def get_codes(s: Union[str, 'ChainedBase']) -> List[str]:
    """ Grab all escape codes from a string.
        Returns a list of all escape codes.
    """
    return codegrabpat.findall(str(s))


def get_code_indices(s: Union[str, 'ChainedBase']) -> Dict[int, str]:
    """ Retrieve a dict of {index: escape_code} for a given string.
        If no escape codes are found, an empty dict is returned.
    """
    indices = {}
    i = 0
    for code in get_codes(s):
        codeindex = s.index(code)
        realindex = i + codeindex
        indices[realindex] = code
        codelen = len(code)
        i = realindex + codelen
        s = s[codeindex + codelen:]
    return indices


def get_indices(s: Union[str, 'ChainedBase']) -> Dict[int, str]:
    """ Retrieve a dict of characters and escape codes with their real index
        into the string as the key.
    """
    codeindices = get_code_indices(s)
    if not codeindices:
        # This function is not for non-escape-code stuff, but okay.
        return {i: c for i, c in enumerate(s)}

    indices = {}
    for codeindex in sorted(codeindices):
        code = codeindices[codeindex]
        if codeindex == 0:
            indices[codeindex] = code
            continue
        # Grab characters before codeindex.
        start = max(indices or {0: ''}, key=int)
        startcode = indices.get(start, '')
        startlen = start + len(startcode)
        indices.update({i: s[i] for i in range(startlen, codeindex)})
        indices[codeindex] = code

    lastindex = max(indices, key=int)
    lastitem = indices[lastindex]
    start = lastindex + len(lastitem)
    textlen = len(s)
    if start < (textlen - 1):
        # Grab chars after last code.
        indices.update({i: s[i] for i in range(start, textlen)})
    return indices


def get_indices_list(s: Union[str, 'ChainedBase']) -> List[str]:
    """ Retrieve a list of characters and escape codes where each escape
        code uses only one index. The indexes will not match up with the
        indexes in the original string.
    """
    indices = get_indices(s)
    return [
        indices[i] for i in sorted(indices, key=int)
    ]


def is_escape_code(s: Union[str, 'ChainedBase']) -> bool:
    """ Returns True if `s` appears to be any kind of escape code. """
    return codepat.match(str(s)) is not None


def strip_codes(s: Union[str, 'ChainedBase']) -> str:
    """ Strip all color codes from a string.
        Returns empty string for "falsey" inputs (except 0).
    """
    return codepat.sub('', str(s) if (s or (s == 0)) else '')


@total_ordering
class ChainedBase(Sequence):
    """ Base object for Colr and Control. Handles basic string-manipulation
        methods.
    """

    def __init__(self, text=None):
        self.data = str('' if text is None else text)

    def __add__(self, other):
        """ Allow the old string concat methods through addition. """
        if hasattr(other, 'data') and isinstance(other.data, str):
            return self.__class__(''.join((self.data, other.data)))
        elif isinstance(other, str):
            return self.__class__(''.join((self.data, other)))
        raise TypeError(
            '{name} cannot be added to non {name}, or str: {other}'.format(
                name=type(self).__name__,
                other=type(other).__name__,
            )
        )

    def __bool__(self):
        """ A ChainedBase is truthy if it has some .data. """
        return bool(self.data)

    def __bytes__(self):
        """ A ChainedBase's bytes() value is just str(self.data).encode().
            For other encodings, you can use self.data.encode('ascii') or
            whatever encoding you want to use.
        """
        return str(self.data or '').encode()

    def __call__(self, text):
        """ Append text to this ChainedBase object. """
        self.data = ''.join((
            self.data,
            str(text),
        ))
        return self

    def __eq__(self, other):
        """ ChainedBases are equal if their .data is the same. """
        return isinstance(other, self.__class__) and other.data == self.data

    def __format__(self, fmt):
        """ Allow format specs to apply to self.data.
            Note, if any conversion is done on the object beforehand
            (using !s, !a, !r, and friends) this method is never called.
            It only deals with the `format_spec` described in
            `help('FORMATTING')`.
        """
        if not fmt:
            # TODO: Is this even possible?
            return str(self)
        methodmap = {
            '<': self.ljust,
            '>': self.rjust,
            '^': self.center,
        }
        for align in methodmap:
            char, sign, width = fmt.partition(align)
            if not sign:
                continue
            if not char:
                char = ' '
            try:
                widthval = int(width)
            except ValueError:
                raise ValueError(
                    'Invalid width for format specifier: {}'.format(width)
                )
            return str(methodmap[align](widthval, fillchar=char))
        # No alignment char, default to ljust ('<').
        try:
            width = int(fmt)
        except ValueError:
            raise ValueError(
                'Expecting standard str format spec, got: {!r}'.format(fmt)
            )
        else:
            return str(methodmap['<'](width, fillchar=' '))

    def __getitem__(self, key):
        """ Allow subscripting self.data. This will ignore any escape codes,
            because otherwise it would be just about useless.
            Returns another ChainedBase instance.
        """
        length = len(self.stripped())
        lastindex = length - 1
        if isinstance(key, slice):
            # Get slice values for non-escape code data.
            # Adjusts actual start/stop for actual length.
            start, stop, step = key.indices(length)
        elif isinstance(key, int):
            if key > lastindex:
                raise IndexError(
                    'Index out of bounds for plain text, too large.'
                )
            elif key < 0:
                # Negative index (length + key).
                key = length + key
                if key < 0:
                    raise IndexError(
                        'Index out of bounds for plain text, too small.'
                    )
            # Single element slice.
            start, stop, step = key, key + 1, 1
        else:
            raise TypeError('Indices must be integers/slices.')

        if (start == lastindex) and (stop == lastindex):
            # A slice like [::n]
            if step < 0:
                # A negative step of everything.
                start += 1
                stop = 0
            else:
                # A positive step of everything.
                start = 0
                stop += 1

        if step > 0:
            pos = -1
        else:
            pos = start + 1
        codeparts = []
        parts = []

        def is_out_of_bounds():
            """ Tracks string position and returns True if it has went past
                the bounds.
            """
            if (start <= stop) and (pos >= stop):
                # Positive step.
                return True
            elif (start >= stop) and (pos <= stop):
                # Negative step.
                return True
            return False

        for part in self.iter_parts():
            if is_out_of_bounds():
                break
            if part.is_code():
                codeparts.append(part)
                continue
            chars = []
            for char in str(part)[::step]:
                pos += step
                if (step > 0) and (pos < start):
                    # Started negative on a positive step, but it's okay.
                    continue
                if pos == stop:
                    break
                parts.extend(codeparts)
                codeparts = []
                chars.append(char)

            parts.append(''.join(chars))

        s = ''.join(str(x) for x in parts)
        # It's okay to return an empty ChainedBase,
        # str() does it for slices like 'test'[45:].
        return self.__class__(s)

    def __hash__(self):
        """ A ChainedBase's hash value is based on self.data. """
        return hash(str(self.data or ''))

    def __iter__(self):
        """ Iterating over a ChainedBase means iterating over self.data. """
        return self.data.__iter__()

    def __len__(self):
        """ Return len() for any built up string data. This will count color
            codes, so it's not that useful.
        """
        return len(self.data)

    def __lt__(self, other):
        """ ChainedBase is less another if self.data < other.data, or
            if self.data is < str.
        """
        if hasattr(other, 'data') and isinstance(other.data, str):
            return self.data < other.data
        elif isinstance(other, str):
            return self.data < other

        raise TypeError(
            'Cannot compare. Expected: {} or str, got: ({}) {!r}.'.format(
                type(self).__name__,
                type(other).__name__,
                other,
            )
        )

    def __mul__(self, n):
        """ Allow the same multiplication operator as str,
            except return a ChainedBase.
        """
        if not isinstance(n, int):
            raise TypeError(
                'Cannot multiply {} by non-int type: {}'.format(
                    type(self).__name__,
                    type(n).__name__,
                )
            )

        return self.__class__(self.data * n)

    def __radd__(self, other):
        """ Allow a ChainedBase to be added to a str. """
        return self.__add__(other)

    def __rmul__(self, n):
        """ Allow a ChainedBase to multiply an int (though it's reversed). """
        return self.__mul__(n)

    def __repr__(self):
        return repr(self.data)

    def __str__(self):
        return str(self.data)

    def _str_just(
            self, methodname, width, fillchar=' ', squeeze=False,
            **colorkwargs):
        """ Perform a str justify method on the text arg, or self.data, before
            applying color codes.
            Arguments:
                methodname  : Name of str justification method to apply.
                methodargs  : Arguments for the str method.

            Keyword Arguments:
                text, fore, back, style  : see color().
        """
        try:
            width = int(width)
        except ValueError as exint:
            raise ValueError('Expecting a number for width.') from exint

        newtext = ''
        with suppress(KeyError):
            # text argument overrides self.data
            newtext = str(colorkwargs.pop('text'))

        strfunc = getattr(str, methodname)
        if newtext:
            # Operating on text argument, self.data is left alone.
            strippedtxt = strip_codes(newtext)
            codelen = len(newtext) - len(strippedtxt)
            width = width + codelen
            if squeeze:
                realoldlen = len(self.stripped())
                width -= realoldlen
            return self.__class__().join(
                self,
                self.__class__(
                    strfunc(newtext, width, fillchar),
                    **colorkwargs
                )
            )

        # Operating on self.data.
        strippedtxt = self.stripped()
        codelen = len(self.data) - len(strippedtxt)
        width = width + codelen
        return self.__class__(
            strfunc(self.data, width, fillchar),
            **colorkwargs
        )

    def _str_strip(self, methodname, chars=None):
        """ Run a `str.*strip` function on self.data, and return a ChainedBase
            instance.
            `chars` can be an iterable of characters, or an escape code to
            strip.
        """
        if not chars:
            chars = ' \t\n'
        strip_code = is_escape_code(chars)
        stripping_codes = (
            strip_code or
            any(is_escape_code(s) for s in chars)
        )
        parts = self.parts()

        def strip_parts(method, indexes):
            for i in indexes:
                partstr = str(parts[i])
                if is_escape_code(partstr):
                    if not stripping_codes:
                        continue
                    if strip_code:
                        if partstr == chars:
                            parts[i] = ''
                        else:
                            # Trying to strip a code, and can't find it.
                            break

                stripped = method(partstr, chars)
                if stripped == partstr:
                    # Nothing was stripped.
                    break
                parts[i] = stripped

        partslen = len(parts)
        if methodname in ('lstrip', 'strip'):
            strip_parts(str.lstrip, range(0, partslen))

        if methodname in ('rstrip', 'strip'):
            strip_parts(str.rstrip, range(partslen - 1, -1, -1))

        return ''.join(str(x) for x in parts)

    def append(self, char, length=1):
        """ Append a char or str (`char`) a number of times (`length`). """
        self.data = ''.join((self.data, (str(char) * length)))
        return self

    def center(self, width, fillchar=' ', squeeze=False, **kwargs):
        """ s.center() doesn't work well on strings with color codes.
            This method will use .center() before colorizing the text.
            Returns a ChainedBase() object.
            Arguments:
                width    : The width for the resulting string (before colors)
                fillchar : The character to pad with. Default: ' '
                squeeze  : Width applies to existing data and new data.
                           (self.data and the text arg)
            Keyword Arguments:
                text     : The string to center, otherwise self.data is used.
                fore, back, style : see color().
        """
        return self._str_just(
            'center',
            width,
            fillchar,
            squeeze=squeeze,
            **kwargs)

    def chained(self, data):
        """ Called by the various ChainedBase methods to build a single string

            Arguments:
                data  : str data to add to this ChainedBase.
        """
        self.data = ''.join((
            self.data,
            str(data),
        ))
        return self

    def copy(self):
        """ Return a copy of this instance, with the same data. """
        return self.__class__(self.data)

    def indent(self, length, char=' '):
        """ Prepend `length` spaces (or `char`) to this instance. """
        return self.prepend(char or ' ', length)

    def index(self, sub, start=None, end=None):
        """ A shortcut to self.data.index(). """
        return self.data.index(sub, start, end)

    def iter_parts(self, text=None):
        """ Iterate over CodeParts and TextParts, in the order
            they are discovered from `self.data`.
        """
        s = str(self if text is None else text)
        length = len(s)
        scanner = codepat.scanner(s)
        m = scanner.search()
        pos = 0
        while (m is not None):
            start, stop = m.span()
            if start > pos:
                yield TextPart(s, start=pos, stop=start)
            yield CodePart(s, start=start, stop=stop)
            pos = stop
            m = scanner.search()
            if (m is None) and (stop < length):
                yield TextPart(s, start=stop)
        if pos == 0:
            # No codes to separate. All text.
            yield TextPart(s, start=0, stop=length)

    def join(self, *args, **colorkwargs):
        """ Like str.join, except it returns a ChainedBase.
            Arguments:
                args  : One or more ChainedBase or str objects.
                        If a list or tuple is given it will be flattened.
        """
        flat = []
        for clr in args:
            if isinstance(clr, (list, tuple, GeneratorType)):
                # Flatten any lists, at least once.
                flat.extend(str(c) for c in clr)
            else:
                flat.append(str(clr))
        return self.__class__(self.data.join(flat))

    def ljust(self, width, fillchar=' ', squeeze=False, **kwargs):
        """ s.ljust() doesn't work well on strings with color codes.
            This method will use .ljust() before colorizing the text.
            Returns a ChainedBase() object.
            Arguments:
                width    : The width for the resulting string (before colors)
                fillchar : The character to pad with. Default: ' '
                squeeze  : Width applies to existing data and new data.
                           (self.data and the text arg)
            Keyword Arguments:
                text     : The string to left-justify, otherwise self.data.
                fore, back, style : see color().
        """
        return self._str_just(
            'ljust',
            width,
            fillchar,
            squeeze=squeeze,
            **kwargs
        )

    def lstrip(self, chars=None):
        """ Like str.lstrip, except it returns the ChainedBase instance. """
        return self.__class__(self._str_strip('lstrip', chars))

    def parts(self, text=None):
        """ Return a list of CodeParts and TextParts, in the order
            they are discovered from `self.data`.
        """
        return list(self.iter_parts(text=text))

    def prepend(self, char, length=1):
        """ Prepend a char or str (`char`) a number of times (`length`). """
        self.data = ''.join((str(char) * length, self.data))
        return self

    def rjust(self, width, fillchar=' ', squeeze=False, **kwargs):
        """ s.rjust() doesn't work well on strings with color codes.
            This method will use .rjust() before colorizing the text.
            Returns a ChainedBase() object.
            Arguments:
                width    : The width for the resulting string (before colors)
                fillchar : The character to pad with. Default: ' '
                squeeze  : Width applies to existing data and new data.
                           (self.data and the text arg)
            Keyword Arguments:
                text     : The string to right-justify, otherwise self.data.
                fore, back, style : see color().
        """
        return self._str_just(
            'rjust',
            width,
            fillchar,
            squeeze=squeeze,
            **kwargs,
        )

    def rstrip(self, chars=None):
        """ Like str.rstrip, except it returns the ChainedBase instance. """
        return self.__class__(self._str_strip('rstrip', chars))

    def str(self):
        """ Alias for self.__str__ """
        return str(self)

    def strip(self, chars=None):
        """ Like str.strip, except it returns the ChainedBase instance. """
        return self.__class__(self._str_strip('strip', chars))

    def stripped(self):
        """ Return str(strip_codes(self.data)) """
        return strip_codes(self.data)

    def write(self, file=sys.stdout, end='', delay=None):
        """ Write this control code str to a file, clear self.data, and
            return self.
            Arguments:
                file  : File object to write to.
                        self.data is encoded using the default .encode()
                        call before writing.
                        Default: sys.stdout
                end   : Line ending character/string.
                        Default: '' (Nothing/Empty-String)
                delay : Seconds to delay between calls to `write()`.
                        Used in text animations.
                        `delay` recalculated to accommodate whitespace chars
                        and escape codes, and is passed to `time.sleep()`.
                        Default: None
        """
        s = str(self)
        filebuf = getattr(file, 'buffer', file)
        if s:
            if delay is None:
                filebuf.write(s.encode())
            else:
                # Refactor the delay time for Control/Colr instances.
                # Escape codes and whitespace should not count for the delay.
                strippedtime = len(self.stripped()) * delay
                whitespacecnt = sum(s.count(char) for char in ' \n\t')
                newdelay = strippedtime / (len(s) - whitespacecnt)
                for c in str(self):
                    filebuf.write(c.encode())
                    file.flush()
                    if c not in ' \n\t':
                        sleep(newdelay)
        if end:
            filebuf.write(end.encode())
        file.flush()
        self.data = ''
        return self


class ChainedPart(object):
    """ Base for CodePart and TextPart. Holds shared methods.
    """
    def __init__(self, originstr, start=None, stop=None):
        s = str(originstr or '')
        self.start = start
        self.stop = stop
        self.data = s[self.get_slice()]

    def __eq__(self, other):
        try:
            otherdata = other.data
            otherstart = other.start
            otherstop = other.stop
        except AttributeError:
            raise TypeError('Cannot compare {} to {}.'.format(
                type(self).__name__,
                type(other).__name__,
            ))
        return (
            (self.data == otherdata) and
            (self.start == otherstart) and
            (self.stop == otherstop)
        )

    def __hash__(self):
        return hash('<{} {!r}:start={}:stop={}>'.format(
            type(self).__name__,
            self.data,
            self.start or 0,
            self.stop or 0,
        ))

    def __repr__(self):
        return '{}({!r})'.format(type(self).__name__, self.data)

    def __str__(self):
        return str(self.data)

    def get_slice(self):
        """ Return a `slice` object using this ChainedPart's `start` and
            `stop` attribute.
        """
        return slice(self.start, self.stop)

    def is_code(self):
        raise NotImplementedError('Not implemented, ambiguous part.')

    def is_text(self):
        raise NotImplementedError('Not implemented, ambiguous part.')


class CodePart(ChainedPart):
    """ Helper class for ChainedBase.parts().
        Marks a part of the string as an escape code.
    """
    def is_code(self):
        return True

    def is_text(self):
        return False


class TextPart(ChainedPart):
    """ Helper class for ChainedBase.parts().
        Marks a part of the string as text.
    """
    def is_code(self):
        return False

    def is_text(self):
        return True
