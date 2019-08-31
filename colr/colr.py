#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" colr.py
    A terminal color library for python, inspired by 'clor' (javascript lib).

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
from contextlib import suppress  # type: ignore
from functools import partial
import ctypes
import math
import os
import struct
import sys

from types import GeneratorType
from typing import (  # noqa
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Set,  # Set is used as a 'type: Set' comment in `get_known_codes()`.
    Tuple,
    Union,
    cast,
)
from typing.io import IO

from .base import (
    ChainedBase,
    CodePart,
    TextPart,
    closing_code,
    get_codes,
    strip_codes,
)

from .codes import (
    _stylemap,
    _stylenums,
    basic_names,
    codeformat,
    code_nums,
    code_nums_reverse,
    codes,
    codes_reverse,
    extbackformat,
    extforeformat,
    rgbbackformat,
    rgbforeformat,
)
from .trans import (
    ColorCode,
    hex2rgb,
    hex2term,
    hex2termhex,
)
from .name_data import names as name_data

# Acceptable fore/back args.
ColorArg = Union[str, int, Tuple[int, int, int]]
# Acceptable format_* function args.
FormatArg = Union[int, Tuple[int, int, int]]
# (ColrCodePart/ColrTextPart).code_info() return type.
ColrChainedPartInfo = Tuple[
    Optional[str],
    Optional[
        Union[str, int, Tuple[int, int, int]]
    ]
]

__all__ = [
    '_disabled',
    'auto_disable',
    'closing_code',
    'codeformat',
    'code_nums',
    'code_nums_reverse',
    'codes',
    'codes_reverse',
    'color',
    'Colr',
    'disable',
    'enable',
    'extbackformat',
    'extforeformat',
    'format_back',
    'format_fore',
    'get_all_names',
    'get_code_num',
    'get_code_num_rgb',
    'get_codes',
    'get_known_codes',
    'get_known_name',
    'get_terminal_size',
    'InvalidArg',
    'InvalidColr',
    'InvalidFormatArg',
    'InvalidFormatColr',
    'InvalidEscapeCode',
    'InvalidRgbEscapeCode',
    'InvalidStyle',
    'name_data',
    'parse_colr_arg',
    'rgbbackformat',
    'rgbforeformat',
    'strip_codes',
]
# Set with the enable/disable functions.
_disabled = False

# Windows support relies on SetConsoleMode
# These boolean flags are for debugging.
has_windll = False
has_setconsolemode = False
try:
    _kernel32 = ctypes.windll.kernel32  # noqa (attribute error during development)
    has_windll = True
    try:
        _kernel32.SetConsoleMode(_kernel32.GetStdHandle(-11), 7)
        has_setconsolemode = True
    except Exception:
        # Windows, but the new ansi code api is not supported.
        # Library user will need to call colr.disable() to keep from spewing
        # junk characters all over the screen.
        pass
    del _kernel32
except AttributeError:
    # No windll, probably linux. If the system doesn't support ansi escape
    # codes the library user will need to call colr.disable().
    pass


def auto_disable(
        enabled: Optional[bool] = True,
        fds: Optional[Sequence[IO]] = (sys.stdout, sys.stderr)) -> None:
    """ Automatically decide whether to disable color codes if stdout or
        stderr are not ttys.

        Arguments:
            enabled  : Whether to automatically disable color codes.
                       When set to True, the fds will be checked for ttys.
                       When set to False, enable() is called.
            fds      : Open file descriptors to check for ttys.
                       If any non-ttys are found, colors will be disabled.
                       Objects must have a isatty() method.
    """
    if enabled:
        allttys = all(
            getattr(f, 'isatty', lambda: False)()
            for f in cast(Sequence[IO], fds)
        )
        if not allttys:
            disable()
    else:
        enable()


def disable() -> None:
    """ Disable color codes for Colr and the convenience color() function.
        Created to be used by auto_disable(), for piping output to file or
        other commands.
    """
    global _disabled
    _disabled = True


def disabled() -> bool:
    """ Public access to _disabled. """
    return _disabled


def enable() -> None:
    """ Enable color codes for Colr and the convenience color() function.
        This only needs to be called if disable() was called previously.
    """
    global _disabled
    _disabled = False


def enabled() -> bool:
    """ Public access to _disabled. """
    return not _disabled


def _format_code(
        number: FormatArg,
        backcolor: Optional[bool] = False,
        light: Optional[bool] = False,
        extended: Optional[bool] = False) -> str:
    """ Return an escape code for a fore/back color, by number.
        This is a convenience method for handling the different code types
        all in one shot.
        It also handles some validation.
        format_fore/format_back wrap this function to reduce code duplication.

        Arguments:
            number    : Integer or RGB tuple to format into an escape code.
            backcolor : Whether this is for a back color, otherwise it's fore.
            light     : Whether this should be a 'light' color.
            extended  : Whether this should be an extended (256) color.

        If `light` and `extended` are both given, only `light` is used.
    """
    if backcolor:
        codetype = 'back'
        # A dict of codeformat funcs. These funcs return an escape code str.
        formatters = {
            'code': lambda n: codeformat(40 + n),
            'lightcode': lambda n: codeformat(100 + n),
            'ext': lambda n: extbackformat(n),
            'rgb': lambda r, g, b: rgbbackformat(r, g, b),
        }  # type: Dict[str, Callable[..., str]]
    else:
        codetype = 'fore'
        formatters = {
            'code': lambda n: codeformat(30 + n),
            'lightcode': lambda n: codeformat(90 + n),
            'ext': lambda n: extforeformat(n),
            'rgb': lambda r, g, b: rgbforeformat(r, g, b),
        }
    try:
        r, g, b = (int(x) for x in number)  # type: ignore
    except (TypeError, ValueError):
        # Not an rgb code.
        # This variable, and it's cast is only to satisfy the type checks.
        try:
            n = int(cast(int, number))
        except ValueError:
            # Not an rgb code, or a valid code number.
            raise InvalidColr(
                number,
                'Expecting RGB or 0-255 for {} code.'.format(codetype)
            )
        if light:
            if not in_range(n, 0, 9):
                raise InvalidColr(
                    n,
                    'Expecting 0-9 for light {} code.'.format(codetype)
                )
            return formatters['lightcode'](n)
        elif extended:
            if not in_range(n, 0, 255):
                raise InvalidColr(
                    n,
                    'Expecting 0-255 for ext. {} code.'.format(codetype)
                )
            return formatters['ext'](n)

        if not in_range(n, 0, 9):
            raise InvalidColr(
                n,
                'Expecting 0-9 for {} code.'.format(codetype)
            )
        return formatters['code'](n)

    # Rgb code.
    try:
        if not all(in_range(x, 0, 255) for x in (r, g, b)):
            raise InvalidColr(
                (r, g, b),
                'RGB value for {} not in range 0-255.'.format(codetype)
            )
    except TypeError:
        # Was probably a 3-char string. Not an rgb code though.
        raise InvalidColr(
            (r, g, b),
            'RGB value for {} contains invalid number.'.format(codetype)
        )
    return formatters['rgb'](r, g, b)


def format_back(
        number: FormatArg,
        light: Optional[bool] = False,
        extended: Optional[bool] = False) -> str:
    """ Return an escape code for a back color, by number.
        This is a convenience method for handling the different code types
        all in one shot.
        It also handles some validation.
    """
    return _format_code(
        number,
        backcolor=True,
        light=light,
        extended=extended
    )


def format_fore(
        number: FormatArg,
        light: Optional[bool] = False,
        extended: Optional[bool] = False) -> str:
    """ Return an escape code for a fore color, by number.
        This is a convenience method for handling the different code types
        all in one shot.
        It also handles some validation.
    """
    return _format_code(
        number,
        backcolor=False,
        light=light,
        extended=extended
    )


def format_style(number: int) -> str:
    """ Return an escape code for a style, by number.
        This handles invalid style numbers.
    """
    if str(number) not in _stylenums:
        raise InvalidStyle(number)
    return codeformat(number)


def get_all_names() -> Tuple[str, ...]:
    """ Retrieve a tuple of all known color names, basic and 'known names'.
    """
    names = list(basic_names)
    names.extend(name_data)
    return tuple(sorted(set(names)))


def get_code_num(s: str) -> Optional[int]:
    """ Get code number from an escape code.
        Raises InvalidEscapeCode if an invalid number is found.
    """
    if ';' in s:
        # Extended fore/back codes.
        numberstr = s.rpartition(';')[-1][:-1]
    else:
        # Fore, back, style, codes.
        numberstr = s.rpartition('[')[-1][:-1]

    num = try_parse_int(
        numberstr,
        default=None,
        minimum=0,
        maximum=255
    )
    if num is None:
        raise InvalidEscapeCode(numberstr)
    return num


def get_code_num_rgb(s: str) -> Optional[Tuple[int, int, int]]:
    """ Get rgb code numbers from an RGB escape code.
        Raises InvalidRgbEscapeCode if an invalid number is found.
    """
    parts = s.split(';')
    if len(parts) != 5:
        raise InvalidRgbEscapeCode(s, reason='Count is off.')
    rgbparts = parts[-3:]
    if not rgbparts[2].endswith('m'):
        raise InvalidRgbEscapeCode(s, reason='Missing \'m\' on the end.')

    rgbparts[2] = rgbparts[2].rstrip('m')
    try:
        r, g, b = [int(x) for x in rgbparts]
    except ValueError as ex:
        raise InvalidRgbEscapeCode(s) from ex

    if not all(in_range(x, 0, 255) for x in (r, g, b)):
        raise InvalidRgbEscapeCode(s, reason='Not in range 0-255.')
    return r, g, b


def get_known_codes(
        s: Union[str, 'Colr'],
        unique: Optional[bool] = True,
        rgb_mode: Optional[bool] = False):
    """ Get all known escape codes from a string, and yield the explanations.
    """

    isdisabled = disabled()
    orderedcodes = tuple((c, get_known_name(c)) for c in get_codes(s))
    codesdone = set()  # type: Set[str]

    for code, codeinfo in orderedcodes:
        # Do the codes in order, but don't do the same code twice.

        if unique:
            if code in codesdone:
                continue
            codesdone.add(code)

        if codeinfo is None:
            continue
        codetype, name = codeinfo

        typedesc = '{:>13}: {!r:<23}'.format(codetype.title(), code)
        if codetype.startswith(('extended', 'rgb')):
            if isdisabled:
                codedesc = str(ColorCode(name, rgb_mode=rgb_mode))
            else:
                codedesc = ColorCode(name, rgb_mode=rgb_mode).example()
        else:
            codedesc = ''.join((
                code,
                str(name).lstrip('(').rstrip(')'),
                codes['style']['reset_all']
            ))

        yield ' '.join((
            typedesc,
            codedesc
        ))


def get_known_name(s: str) -> Optional[Tuple[str, ColorArg]]:
    """ Reverse translate a terminal code to a known color name, if possible.
        Returns a tuple of (codetype, knownname) on success.
        Returns None on failure.
    """

    if not s.endswith('m'):
        # All codes end with 'm', so...
        return None
    if s.startswith('\033[38;5;'):
        # Extended fore.
        name = codes_reverse['fore'].get(s, None)
        if name is None:
            num = cast(int, get_code_num(s))
            return ('extended fore', num)
        else:
            return ('extended fore', name)
    elif s.startswith('\033[48;5;'):
        # Extended back.
        name = codes_reverse['back'].get(s, None)
        if name is None:
            num = cast(int, get_code_num(s))
            return ('extended back', num)
        else:
            return ('extended back', name)
    elif s.startswith('\033[38;2'):
        # RGB fore.
        vals = get_code_num_rgb(s)
        if vals is not None:
            return ('rgb fore', vals)
    elif s.startswith('\033[48;2'):
        # RGB back.
        vals = get_code_num_rgb(s)
        if vals is not None:
            return ('rgb back', vals)
    elif s.startswith('\033['):
        # Fore, back, style.
        number = cast(int, get_code_num(s))
        # Get code type based on number.
        if (number <= 7) or (number == 22):
            codetype = 'style'
        elif (((number >= 30) and (number < 40)) or
                ((number >= 90) and (number < 100))):
            codetype = 'fore'
        elif (((number >= 40) and (number < 50)) or
                ((number >= 100) and (number < 110))):
            codetype = 'back'
        else:
            raise InvalidEscapeCode(
                number,
                'Expecting 0-7, 22, 30-39, or 40-49 for escape code',
            )

        name = codes_reverse[codetype].get(s, None)
        if name is not None:
            return (codetype, name)

    # Not a known escape code.
    return None


def get_terminal_size(default=(80, 35)):
    """ Return terminal (width, height) """
    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            cr = struct.unpack(
                'hh',
                fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234')
            )
            return cr
        except (ImportError, EnvironmentError):
            pass
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except EnvironmentError:
            pass
    if not cr:
        try:
            cr = os.environ['LINES'], os.environ['COLUMNS']
        except KeyError:
            return default
    return int(cr[1]), int(cr[0])


def in_range(x: int, minimum: int, maximum: int) -> bool:
    """ Return True if x is >= minimum and <= maximum. """
    return (x >= minimum and x <= maximum)


def parse_colr_arg(
        s: str,
        default: Optional[Any] = None,
        rgb_mode: Optional[bool] = False) -> ColorArg:
    """ Parse a user argument into a usable fore/back color value for Colr.
        If a falsey value is passed, default is returned.
        Raises InvalidColr if the argument is unusable.
        Returns: A usable value for Colr(fore/back).

        This validates basic/extended color names.
        This validates the range for basic/extended values (0-255).
        This validates the length/range for rgb values (0-255, 0-255, 0-255).

        Arguments:
            s  : User's color value argument.
                 Example: "1", "255", "black", "25,25,25"
    """
    if not s:
        return cast(ColorArg, default)

    val = s.strip().lower()
    try:
        # Try as int.
        intval = int(val)
    except ValueError:
        # Try as rgb.
        try:
            r, g, b = (int(x.strip()) for x in val.split(','))
        except ValueError:
            if ',' in val:
                # User tried rgb value and failed.
                raise InvalidColr(val)

            # Try as name (fore/back have the same names)
            code = codes['fore'].get(val, None)
            if code:
                # Valid basic code from fore, bask, or style.
                return val

            # Not a basic code, try known names.
            named_data = name_data.get(val, None)
            if named_data is not None:
                # A known named color.
                return val

            # Not a basic/extended/known name, try as hex.
            try:
                if rgb_mode:
                    return hex2rgb(val, allow_short=True)
                return hex2termhex(val, allow_short=True)
            except ValueError:
                raise InvalidColr(val)
        else:
            # Got rgb. Do some validation.
            if not all((in_range(x, 0, 255) for x in (r, g, b))):
                raise InvalidColr(val)
            # Valid rgb.
            return r, g, b
    else:
        # Int value.
        if not in_range(intval, 0, 255):
            # May have been a hex value confused as an int.
            if len(val) in (3, 6):
                try:
                    if rgb_mode:
                        return hex2rgb(val, allow_short=True)
                    return hex2termhex(val, allow_short=True)
                except ValueError:
                    raise InvalidColr(val)
            raise InvalidColr(intval)
        # Valid int value.
        return intval


def try_parse_int(
        s: str,
        default: Optional[Any] = None,
        minimum: Optional[int] = None,
        maximum: Optional[int] = None) -> Optional[Any]:
    """ Try parsing a string into an integer.
        On failure, return `default`.
        If the number is less then `minimum` or greater than `maximum`,
        return `default`.
        Returns an integer on success.
    """
    try:
        n = int(s)
    except ValueError:
        return default
    if (minimum is not None) and (n < minimum):
        return default
    elif (maximum is not None) and (n > maximum):
        return default
    return n


class Colr(ChainedBase):

    """ This class colorizes text for an ansi terminal. """
    # Known offsets for `Colr.rainbow` that will start with a certain color.
    gradient_names = {
        'green': 0,
        'orange': 9,
        'lightred': 15,
        'magenta': 20,
        'red': 80,
        'yellow': 62,
        'blue': 34,
        'cyan': 48,
    }

    def __init__(
            self,
            text: Optional[str] = None,
            fore: Optional[ColorArg] = None,
            back: Optional[ColorArg] = None,
            style: Optional[str] = None,
            no_closing: Optional[bool] = False) -> None:
        """ Initialize a Colr object with text and color options. """
        # Can be initialized with colored text, not required though.
        self.data = self.color(
            text,
            fore=fore,
            back=back,
            style=style,
            no_closing=no_closing,
        )

    def __call__(self, text=None, fore=None, back=None, style=None):
        """ Append text to this Colr object. """
        self.data = ''.join((
            self.data,
            self.color(text=text, fore=fore, back=back, style=style)
        ))
        return self

    def __dir__(self):
        """ Compute the fake method names, and include them in a listing
            of attributes for autocompletion/inspection.
        """

        def fmtcode(s):
            try:
                int(s)
                return 'f_{}'.format(s)
            except ValueError:
                return s

        def fmtbgcode(s):
            try:
                int(s)
                return 'b_{}'.format(s)
            except ValueError:
                return 'bg{}'.format(s)

        attrs = [fmtcode(k) for k in codes['fore']]
        attrs.extend(fmtbgcode(k) for k in codes['back'])
        attrs.extend(k for k in codes['style'])
        attrs.extend((
            'center',
            'chained',
            'color_code',
            'color',
            'data',
            'format',
            'gradient',
            'join',
            'ljust',
            'print',
            'rjust',
            'str'
        ))
        return attrs

    def __format__(self, fmt):
        """ Allow format specs to apply to self.data, such as <, >, and ^.
            This adds a few color-specific features to the format_spec,
            not found in the `ChainedBase` class.
            Colr format spec example:
                '{:[fore=COLOR, back=COLOR, style=STYLE]}'
                ..where COLOR is a stringified version of a valid color arg,
                such as a known name, number, hex code, or RGB value (R;G;B).
                RGB values should be separated with a semicolon, like:
                    '{x:[fore=255;255;255]}'.format(x=Colr('test'))
                Also, `f`,`b`, and `s` are accepted for `fore`, `back`,
                and `style`.

            Example:
                'Hello {x:[fore=red, back=white, style=bright]}'.format(
                    x=Colr('Test')
                )
            Note, if any conversion is done on the object beforehand
            (using !s, !a, !r, and friends) this method is never called.
            It only deals with the `format_spec` described in
            `help('FORMATTING')`.
        """
        if not fmt:
            return str(self)
        if not (('[' in fmt) and (']' in fmt)):
            # No color specs found in the format.
            return super().__format__(fmt)

        # Has color specifications. Parse them out.
        normalspec, _, spec = fmt.partition('[')
        spec = spec.rstrip(']').strip().lower()
        specargs = self._parse_colr_spec(spec)

        try:
            clr = Colr(str(self), **specargs)
        except InvalidColr as ex:
            raise InvalidFormatColr(spec, ex.value) from None
        if normalspec:
            # Apply non-color-specific format specs from ChainedBase.
            return super(self.__class__, clr).__format__(normalspec)
        return str(clr)

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

    def _attr_to_method(self, attr):
        """ Return the correct color function by method name.
            Uses `partial` to build kwargs on the `chained` func.
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
            name = attr[2:].lstrip('_')
            if name in codes['back']:
                return partial(self.chained, back=name)
        elif attr.startswith(('b256_', 'b_')):
            # Back 256 method
            # Remove the b256_ portion.
            name = attr.partition('_')[2]
            return self._ext_attr_to_partial(name, 'back')
        elif attr.startswith(('f256_', 'f_')):
            # Fore 256 method
            name = attr.partition('_')[2]
            return self._ext_attr_to_partial(name, 'fore')

        return None

    @classmethod
    def _call_dunder_colr(cls, obj):
        """ Call __colr__ on an object, after some checks.
            If color is disabled, the object itself is returned.
            If __colr__ doesn't return a Colr instance, TypeError is raised.
            On success, a Colr instance is returned from obj.__colr__().
        """
        if _disabled:
            # No colorization when disabled. Just use str.
            return obj
        clr = obj.__colr__()
        if not isinstance(clr, cls):
            # __colr__ should always return a Colr.
            # Future development may assume a Colr was returned.
            raise TypeError(
                ' '.join((
                    '__colr__ methods should return a {} instance.',
                    'Got: {}',
                )).format(
                    cls.__name__,
                    type(clr).__name__,
                )
            )
        return clr

    def _ext_attr_to_partial(self, name, kwarg_key):
        """ Convert a string like '233' or 'aliceblue' into partial for
            self.chained.
        """
        try:
            intval = int(name)
        except ValueError:
            # Try as an extended name_data name.
            info = name_data.get(name, None)
            if info is None:
                # Not an int value or name_data name.
                return None
            kws = {kwarg_key: info['code']}
            return partial(self.chained, **kws)
        # Integer str passed, use the int value.
        kws = {kwarg_key: intval}
        return partial(self.chained, **kws)

    def _gradient_black_line(
            self, text, start, step=1,
            fore=None, back=None, style=None, reverse=False, rgb_mode=False):
        """ Yield colorized characters,
            within the 24-length black gradient.
        """
        if start < 232:
            start = 232
        elif start > 255:
            start = 255
        if reverse:
            codes = list(range(start, 231, -1))
        else:
            codes = list(range(start, 256))
        return ''.join((
            self._iter_text_wave(
                text,
                codes,
                step=step,
                fore=fore,
                back=back,
                style=style,
                rgb_mode=rgb_mode
            )
        ))

    def _gradient_black_lines(
            self, text, start, step=1,
            fore=None, back=None, style=None, reverse=False,
            movefactor=2, rgb_mode=False):
        """ Yield colorized characters,
            within the 24-length black gradient,
            treating each line separately.
        """
        if not movefactor:
            def factor(i):
                return start
        else:
            # Increase the start for each line.
            def factor(i):
                return start + (i * movefactor)
        return '\n'.join((
            self._gradient_black_line(
                line,
                start=factor(i),
                step=step,
                fore=fore,
                back=back,
                style=style,
                reverse=reverse,
                rgb_mode=rgb_mode,
            )
            for i, line in enumerate(text.splitlines())
        ))

    def _gradient_rgb_line(
            self, text, start, stop, step=1,
            fore=None, back=None, style=None):
        """ Yield colorized characters, morphing from one rgb value to
            another.
        """
        return self._gradient_rgb_line_from_morph(
            text,
            list(self._morph_rgb(start, stop, step=step)),
            fore=fore,
            back=back,
            style=style
        )

    def _gradient_rgb_line_from_morph(
            self, text, morphlist, fore=None, back=None, style=None):
        """ Yield colorized characters, morphing from one rgb value to
            another.
        """
        try:
            listlen = len(morphlist)
        except TypeError:
            morphlist = list(morphlist)
            listlen = len(morphlist)
        neededsteps = listlen // len(text)
        iterstep = 1
        if neededsteps > iterstep:
            # Skip some members of morphlist, to be sure to reach the end.
            iterstep = neededsteps
        usevals = morphlist
        if iterstep > 1:
            # Rebuild the morphlist, skipping some.
            usevals = [usevals[i] for i in range(0, listlen, iterstep)]
        return ''.join((
            self._iter_text_wave(
                text,
                usevals,
                fore=fore,
                back=back,
                style=style,
                rgb_mode=False,
            )
        ))

    def _gradient_rgb_lines(
            self, text, start, stop, step=1,
            fore=None, back=None, style=None, movefactor=None):
        """ Yield colorized characters, morphing from one rgb value to
            another. This treats each line separately.
        """
        morphlist = list(self._morph_rgb(start, stop, step=step))
        if movefactor:
            # Moving means we need the morph to wrap around.
            morphlist.extend(self._morph_rgb(stop, start, step=step))
            if movefactor < 0:
                # Increase the start for each line.
                def move():
                    popped = []
                    for _ in range(abs(movefactor)):
                        try:
                            popped.append(morphlist.pop(0))
                        except IndexError:
                            pass
                    morphlist.extend(popped)
                    return morphlist
            else:
                # Decrease start for each line.
                def move():
                    for _ in range(movefactor):
                        try:
                            val = morphlist.pop(-1)
                        except IndexError:
                            pass
                        else:
                            morphlist.insert(0, val)
                    return morphlist

        return '\n'.join((
            self._gradient_rgb_line_from_morph(
                line,
                move() if movefactor else morphlist,
                fore=fore,
                back=back,
                style=style,
            )
            for i, line in enumerate(text.splitlines())
        ))

    def _iter_text_wave(
            self, text, numbers, step=1,
            fore=None, back=None, style=None, rgb_mode=False):
        """ Yield colorized characters from `text`, using a wave of `numbers`.
            Arguments:
                text      : String to be colorized.
                numbers   : A list/tuple of numbers (256 colors).
                step      : Number of characters to colorize per color.
                fore      : Fore color to use (name or number).
                            (Back will be gradient)
                back      : Background color to use (name or number).
                            (Fore will be gradient)
                style     : Style name to use.
                rgb_mode  : Use number for rgb value.
                            This should never be used when the numbers
                            are rgb values themselves.
        """
        if fore and back:
            raise ValueError('Both fore and back colors cannot be specified.')

        pos = 0
        end = len(text)
        numbergen = self._iter_wave(numbers)

        def make_color(n):
            try:
                r, g, b = n
            except TypeError:
                if rgb_mode:
                    return n, n, n
                return n
            return r, g, b

        for value in numbergen:
            lastchar = pos + step
            yield self.color(
                text[pos:lastchar],
                fore=make_color(value) if fore is None else fore,
                back=make_color(value) if fore is not None else back,
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
            You can stop it by sending a Truthy value into the generator:
                gen = self._iter_wave('test')
                for c in gen:
                    if c == 's':
                        # Stop the generator early.
                        gen.send(True)
                    print(c)
        """
        up = True
        pos = 0
        i = 0
        try:
            end = len(iterable)
        except TypeError:
            iterable = list(iterable)
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

    def _morph_rgb(self, rgb1, rgb2, step=1):
        """ Morph an rgb value into another, yielding each step along the way.
        """
        pos1, pos2 = list(rgb1), list(rgb2)
        indexes = [i for i, _ in enumerate(pos1)]

        def step_value(a, b):
            """ Returns the amount to add to `a` to make it closer to `b`,
                multiplied by `step`.
            """
            if a < b:
                return step
            if a > b:
                return -step
            return 0

        steps = [step_value(pos1[x], pos2[x]) for x in indexes]
        stepcnt = 0
        while (pos1 != pos2):
            stepcnt += 1
            stop = yield tuple(pos1)
            if stop:
                break
            for x in indexes:
                if pos1[x] != pos2[x]:
                    pos1[x] += steps[x]
                    if (steps[x] < 0) and (pos1[x] < pos2[x]):
                        # Over stepped, negative.
                        pos1[x] = pos2[x]
                    if (steps[x] > 0) and (pos1[x] > pos2[x]):
                        # Over stepped, positive.
                        pos1[x] = pos2[x]
        yield tuple(pos1)

    def _parse_colr_spec(self, spec):
        """ Parse a Colr spec such as 'fore=red, back=blue, style=bold' into
            useable Colr keyword arguments.
            Raises InvalidColrFormat on error.
            Returns a dict of {'fore': name, 'back': name, 'style': name} on
            success.
            Arguments:
                spec  : The format spec.
        """
        # Parsed fore,back, and style args if successfully parsed.
        specargs = {}
        # Valid key names.
        validkeys = ('fore', 'back', 'style')
        # Shorter aliases to use with the spec keys.
        aliases = {s[0]: s for s in validkeys}
        # Stack of keys (in order of position) when not using spec-keys.
        # They will be popped off as the values are parsed.
        unused_keys = list(validkeys)
        for kvpairstr in spec.split(','):
            kvpairstr = kvpairstr.strip()
            if not kvpairstr:
                continue
            try:
                # Key=value style.
                k, v = kvpairstr.split('=')
            except ValueError:
                # Keyless?
                try:
                    k = unused_keys[0]
                except IndexError:
                    # Too many commas/values.
                    raise InvalidFormatArg(
                        spec,
                        kvpairstr,
                        msg='Too many arguments/values.',
                    ) from None
                # Just a value was given, use the positional key for it.
                v = kvpairstr

            # Handle any aliases that were used.
            k = aliases.get(k, k)
            # Handle RGB values.
            if v.count(';') in (2, 3):
                try:
                    rgb = tuple(int(x) for x in v.split(';'))
                except ValueError:
                    raise InvalidFormatColr(spec, v) from None
                specargs[k] = rgb
            else:
                specargs[k] = v
            try:
                # Remove from possible keyless keys.
                unused_keys.remove(k)
            except ValueError:
                # Already have all the args we need.
                raise InvalidFormatArg(
                    spec,
                    k,
                    msg='Too many arguments/values.',
                )
        return specargs

    def _rainbow_color(self, freq, i):
        """ Calculate a single hexcode value for a piece of a rainbow.
            Arguments:
                freq  : "Tightness" of colors (see self.rainbow())
                i     : Index of character in string to colorize.
        """
        return '{:02x}{:02x}{:02x}'.format(*self._rainbow_rgb(freq, i))

    def _rainbow_hex_chars(self, s, freq=0.1, spread=3.0, offset=0):
        """ Iterate over characters in a string to build data needed for a
            rainbow effect.
            Yields tuples of (char, hexcode).
            Arguments:
                s      : String to colorize.
                freq   : Frequency/"tightness" of colors in the rainbow.
                         Best results when in the range 0.0-1.0.
                         Default: 0.1
                spread : Spread/width of colors.
                         Default: 3.0
                offset : Offset for start of rainbow.
                         Default: 0
        """
        return (
            (c, self._rainbow_color(freq, offset + i / spread))
            for i, c in enumerate(s)
        )

    def _rainbow_line(
            self, text, freq=0.1, spread=3.0, offset=0,
            rgb_mode=False, **colorargs):
        """ Create rainbow using the same offset for all text.
            Arguments:
                text       : String to colorize.
                freq       : Frequency/"tightness" of colors in the rainbow.
                             Best results when in the range 0.0-1.0.
                             Default: 0.1
                spread     : Spread/width of colors.
                             Default: 3.0
                offset     : Offset for start of rainbow.
                             Default: 0
                rgb_mode   : If truthy, use RGB escape codes instead of
                             extended 256 and approximate hex match.
            Keyword Arguments:
                colorargs  : Any extra arguments for the color function,
                             such as fore, back, style.
                             These need to be treated carefully to not
                            'overwrite' the rainbow codes.
        """
        fore = colorargs.get('fore', None)
        back = colorargs.get('back', None)
        style = colorargs.get('style', None)
        if fore:
            color_args = (lambda value: {
                'back': value if rgb_mode else hex2term(value),
                'style': style,
                'fore': fore
            })
        else:
            color_args = (lambda value: {
                'fore': value if rgb_mode else hex2term(value),
                'style': style,
                'back': back
            })

        if rgb_mode:
            method = self._rainbow_rgb_chars
        else:
            method = self._rainbow_hex_chars
        return ''.join(
            self.color(c, **color_args(hval))
            for c, hval in method(
                text,
                freq=freq,
                spread=spread,
                offset=offset)
        )

    def _rainbow_lines(
            self, text, freq=0.1, spread=3.0, offset=0, movefactor=0,
            rgb_mode=False, **colorargs):
        """ Create rainbow text, using the same offset for each line.
            Arguments:
                text       : String to colorize.
                freq       : Frequency/"tightness" of colors in the rainbow.
                             Best results when in the range 0.0-1.0.
                             Default: 0.1
                spread     : Spread/width of colors.
                             Default: 3.0
                offset     : Offset for start of rainbow.
                             Default: 0
                movefactor : Factor for offset increase on each new line.
                             Default: 0
                rgb_mode   : If truthy, use RGB escape codes instead of
                             extended 256 and approximate hex match.

            Keyword Arguments:
                fore, back, style  : Other args for the color() function.
        """
        if not movefactor:
            def factor(i):
                return offset
        else:
            # Increase the offset for each line.
            def factor(i):
                return offset + (i * movefactor)
        return '\n'.join(
            self._rainbow_line(
                line,
                freq=freq,
                spread=spread,
                offset=factor(i),
                rgb_mode=rgb_mode,
                **colorargs)
            for i, line in enumerate(text.splitlines()))

    def _rainbow_rgb(self, freq, i):
        """ Calculate a single rgb value for a piece of a rainbow.
            Arguments:
                freq  : "Tightness" of colors (see self.rainbow())
                i     : Index of character in string to colorize.
        """
        # Borrowed from lolcat, translated from ruby.
        red = math.sin(freq * i + 0) * 127 + 128
        green = math.sin(freq * i + 2 * math.pi / 3) * 127 + 128
        blue = math.sin(freq * i + 4 * math.pi / 3) * 127 + 128
        return int(red), int(green), int(blue)

    def _rainbow_rgb_chars(self, s, freq=0.1, spread=3.0, offset=0):
        """ Iterate over characters in a string to build data needed for a
            rainbow effect.
            Yields tuples of (char, (r, g, b)).
            Arguments:
                s      : String to colorize.
                freq   : Frequency/"tightness" of colors in the rainbow.
                         Best results when in the range 0.0-1.0.
                         Default: 0.1
                spread : Spread/width of colors.
                         Default: 3.0
                offset : Offset for start of rainbow.
                         Default: 0
        """
        return (
            (c, self._rainbow_rgb(freq, offset + i / spread))
            for i, c in enumerate(s)
        )

    def b_hex(self, value, text=None, fore=None, style=None, rgb_mode=False):
        """ A chained method that sets the back color to an hex value.
            Arguments:
                value    : Hex value to convert.
                text     : Text to style if not building up color codes.
                fore     : Fore color for the text.
                style    : Style for the text.
                rgb_mode : If False, the closest extended code is used,
                           otherwise true color (rgb) mode is used.

        """
        if rgb_mode:
            try:
                colrval = hex2rgb(value, allow_short=True)
            except ValueError:
                raise InvalidColr(value)
        else:
            try:
                colrval = hex2term(value, allow_short=True)
            except ValueError:
                raise InvalidColr(value)
        return self.chained(text=text, fore=fore, back=colrval, style=style)

    def b_rgb(self, r, g, b, text=None, fore=None, style=None):
        """ A chained method that sets the back color to an RGB value.
            Arguments:
                r     : Red value.
                g     : Green value.
                b     : Blue value.
                text  : Text to style if not building up color codes.
                fore  : Fore color for the text.
                style : Style for the text.
        """
        return self.chained(text=text, fore=fore, back=(r, g, b), style=style)

    def chained(self, text=None, fore=None, back=None, style=None):
        """ Called by the various 'color' methods to colorize a single string.
            The RESET_ALL code is appended to the string unless text is empty.
            Raises InvalidColr on invalid color names.

            Arguments:
                text  : String to colorize, or None for  BG/Style change.
                fore  : Name of fore color to use.
                back  : Name of back color to use.
                style : Name of style to use.
        """
        self.data = ''.join((
            self.data,
            self.color(text=text, fore=fore, back=back, style=style),
        ))
        return self

    def color(
            self, text=None, fore=None, back=None, style=None,
            no_closing=False):
        """ A method that colorizes strings, not Colr objects.
            Raises InvalidColr for invalid color names.
            The 'reset_all' code is appended if text is given.
        """
        has_args = (
            (fore is not None) or
            (back is not None) or
            (style is not None)
        )
        if hasattr(text, '__colr__') and not has_args:
            # Use custom __colr__ method in the absence of arguments.
            return str(self._call_dunder_colr(text))

        # Stringify everything before operating on it.
        text = str(text) if text is not None else ''
        if _disabled:
            return text

        # Considered to have unclosed codes if embedded codes exist and
        # the last code was not a color code.
        embedded_codes = get_codes(text)
        has_end_code = embedded_codes and embedded_codes[-1] == closing_code
        # Add closing code if not already added, there is text, and
        # some kind of color/style was used (whether from args, or
        # color codes were included in the text already).
        # If the last code embedded in the text was a closing code,
        # then it is not added.
        # This can be overriden with `no_closing`.
        needs_closing = (
            text and
            (not no_closing) and
            (not has_end_code) and
            (has_args or embedded_codes)
        )
        if needs_closing:
            end = closing_code
        else:
            end = ''
        return ''.join((
            self.color_code(fore=fore, back=back, style=style),
            text,
            end,
        ))

    def color_code(self, fore=None, back=None, style=None):
        """ Return the codes for this style/colors. """
        # Map from style type to raw code formatter function.
        colorcodes = []
        resetcodes = []
        userstyles = {'style': style, 'back': back, 'fore': fore}
        for stype in userstyles:
            stylearg = userstyles.get(stype, None)
            if not stylearg:
                # No value for this style name, don't use it.
                continue
            # Get escape code for this style.
            code = self.get_escape_code(stype, stylearg)
            stylename = str(stylearg).lower()
            if (stype == 'style') and (stylename in ('0', )):
                resetcodes.append(code)
            elif stylename.startswith('reset'):
                resetcodes.append(code)
            else:
                colorcodes.append(code)
        # Reset codes come first, to not override colors.
        return ''.join((''.join(resetcodes), ''.join(colorcodes)))

    def color_dummy(self, text=None, **kwargs):
        """ A wrapper for str() that matches self.color().
            For overriding when _auto_disable is used.
        """
        return str(text) if text is not None else ''

    def format(self, *args, **kwargs):
        """ Like str.format, except it returns a Colr. """
        return self.__class__(self.data.format(*args, **kwargs))

    def get_escape_code(self, codetype, value):
        """ Convert user arg to escape code. """
        valuefmt = str(value).lower()
        code = codes[codetype].get(valuefmt, None)
        if code:
            # Basic code from fore, back, or style.
            return code

        named_funcs = {
            'fore': format_fore,
            'back': format_back,
            'style': format_style,
        }

        # Not a basic code, try known names.
        converter = named_funcs.get(codetype, None)
        if converter is None:
            raise ValueError(
                'Invalid code type. Expecting {}, got: {!r}'.format(
                    ', '.join(named_funcs),
                    codetype
                )
            )
        # Try as hex.
        with suppress(ValueError):
            value = int(hex2term(value, allow_short=True))
            return converter(value, extended=True)

        named_data = name_data.get(valuefmt, None)
        if named_data is not None:
            # A known named color.
            try:
                return converter(named_data['code'], extended=True)
            except TypeError:
                # Passing a known name as a style?
                if codetype == 'style':
                    raise InvalidStyle(value)
                raise
        # Not a known color name/value, try rgb.
        try:
            r, g, b = (int(x) for x in value)
            # This does not mean we have a 3 int tuple. It could be '111'.
            # The converter should catch it though.
        except (TypeError, ValueError):
            # Not an rgb value.
            if codetype == 'style':
                raise InvalidStyle(value)
        try:
            escapecode = converter(value)
        except ValueError as ex:
            raise InvalidColr(value) from ex
        return escapecode

    def gradient(
            self, text=None, name=None, fore=None, back=None, style=None,
            freq=0.1, spread=None, linemode=True,
            movefactor=2, rgb_mode=False):
        """ Return a gradient by color name. Uses rainbow() underneath to
            build the gradients, starting at a known offset.
            Arguments:
                text       : Text to make gradient (self.data when not given).
                             The gradient text is joined to self.data when
                             this is used.
                name       : Color name for the gradient (same as fore names).
                             Default: black
                fore       : Fore color. Back will be gradient when used.
                             Default: None (fore is gradient)
                back       : Back color. Fore will be gradient when used.
                             Default: None (back=reset/normal)
                style      : Style for the gradient.
                             Default: None (reset/normal)
                freq       : Frequency of color change.
                             Higher means more colors.
                             Best when in the 0.0-1.0 range.
                             Default: 0.1
                spread     : Spread/width of each color (in characters).
                             Default: 3.0 for colors, 1 for black/white
                linemode   : Colorize each line in the input.
                             Default: True
                movefactor : Factor for offset increase on each line when
                             using linemode.
                             Minimum value: 0
                             Default: 2
                rgb_mode   : Use true color (rgb) codes.
        """
        try:
            # Try explicit offset (passed in with `name`).
            offset = int(name)
        except (TypeError, ValueError):
            name = name.lower().strip() if name else 'black'
            # Black and white are separate methods.
            if name == 'black':
                return self.gradient_black(
                    text=text,
                    fore=fore,
                    back=back,
                    style=style,
                    step=int(spread) if spread else 1,
                    linemode=linemode,
                    movefactor=movefactor,
                    rgb_mode=rgb_mode
                )
            elif name == 'white':
                return self.gradient_black(
                    text=text,
                    fore=fore,
                    back=back,
                    style=style,
                    step=int(spread) if spread else 1,
                    linemode=linemode,
                    movefactor=movefactor,
                    reverse=True,
                    rgb_mode=rgb_mode
                )
            try:
                # Get rainbow offset from known name.
                offset = self.gradient_names[name]
            except KeyError:
                raise ValueError('Unknown gradient name: {}'.format(name))

        return self.rainbow(
            text=text,
            fore=fore,
            back=back,
            style=style,
            offset=offset,
            freq=freq,
            spread=spread or 3.0,
            linemode=linemode,
            movefactor=movefactor,
            rgb_mode=rgb_mode,
        )

    def gradient_black(
            self, text=None, fore=None, back=None, style=None,
            start=None, step=1, reverse=False,
            linemode=True, movefactor=2, rgb_mode=False):
        """ Return a black and white gradient.
            Arguments:
                text       : String to colorize.
                             This will always be greater than 0.
                fore       : Foreground color, background will be gradient.
                back       : Background color, foreground will be gradient.
                style      : Name of style to use for the gradient.
                start      : Starting 256-color number.
                             The `start` will be adjusted if it is not within
                             bounds.
                             This will always be > 15.
                             This will be adjusted to fit within a 6-length
                             gradient, or the 24-length black/white gradient.
                step       : Number of characters to colorize per color.
                             This allows a "wider" gradient.
                linemode   : Colorize each line in the input.
                             Default: True
                movefactor : Factor for offset increase on each line when
                             using linemode.
                             Minimum value: 0
                             Default: 2
                rgb_mode   : Use true color (rgb) method and codes.
        """
        gradargs = {
            'step': step,
            'fore': fore,
            'back': back,
            'style': style,
            'reverse': reverse,
            'rgb_mode': rgb_mode,
        }

        if linemode:
            gradargs['movefactor'] = 2 if movefactor is None else movefactor
            method = self._gradient_black_lines
        else:
            method = self._gradient_black_line

        if text:
            return self.__class__(
                ''.join((
                    self.data or '',
                    method(
                        text,
                        start or (255 if reverse else 232),
                        **gradargs)
                ))
            )

        # Operating on self.data.
        return self.__class__(
            method(
                self.stripped(),
                start or (255 if reverse else 232),
                **gradargs)
        )

    def gradient_rgb(
            self, text=None, fore=None, back=None, style=None,
            start=None, stop=None, step=1, linemode=True, movefactor=0):
        """ Return a black and white gradient.
            Arguments:
                text       : String to colorize.
                fore       : Foreground color, background will be gradient.
                back       : Background color, foreground will be gradient.
                style      : Name of style to use for the gradient.
                start      : Starting rgb value.
                stop       : Stopping rgb value.
                step       : Number of characters to colorize per color.
                             This allows a "wider" gradient.
                             This will always be greater than 0.
                linemode   : Colorize each line in the input.
                             Default: True
                movefactor : Amount to shift gradient for each line when
                             `linemode` is set.

       """
        gradargs = {
            'step': step,
            'fore': fore,
            'back': back,
            'style': style,
        }
        start = start or (0, 0, 0)
        stop = stop or (255, 255, 255)
        if linemode:
            method = self._gradient_rgb_lines
            gradargs['movefactor'] = movefactor
        else:
            method = self._gradient_rgb_line

        if text:
            return self.__class__(
                ''.join((
                    self.data or '',
                    method(
                        text,
                        start,
                        stop,
                        **gradargs
                    ),
                ))
            )

        # Operating on self.data.
        return self.__class__(
            method(
                self.stripped(),
                start,
                stop,
                **gradargs
            )
        )

    def hex(self, value, text=None, back=None, style=None, rgb_mode=False):
        """ A chained method that sets the fore color to an hex value.
            Arguments:
                value    : Hex value to convert.
                text     : Text to style if not building up color codes.
                back     : Back color for the text.
                style    : Style for the text.
                rgb_mode : If False, the closest extended code is used,
                           otherwise true color (rgb) mode is used.

        """
        if rgb_mode:
            try:
                colrval = hex2rgb(value, allow_short=True)
            except ValueError:
                raise InvalidColr(value)
        else:
            try:
                colrval = hex2term(value, allow_short=True)
            except ValueError:
                raise InvalidColr(value)
        return self.chained(text=text, fore=colrval, back=back, style=style)

    def iter_parts(self, text=None):
        """ Iterate over ColrCodeParts and TextParts, in the order
            they are discovered from `self.data`.

            This overrides the `ChainedBase.iter_parts` to yield
            `ColrCodeParts` instead of `CodeParts`. They contain more info
            about the codes, like code type and color name/value.
        """
        for part in super().iter_parts(text=text):
            if isinstance(part, CodePart):
                # ColrCodePart will add some info about the code.
                yield ColrCodePart.from_codepart(part)
            else:
                # Compatible attributes with ColrCodePart.
                yield ColrTextPart.from_textpart(part)

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
                flat.extend(str(c) for c in clr)
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

    def lstrip(self, chars=None):
        """ Like str.lstrip, except it returns the Colr instance. """
        return self.__class__(
            self._str_strip('lstrip', chars),
            no_closing=chars and (closing_code in chars),
        )

    def print(self, *args, **kwargs):
        """ Chainable print method. Prints self.data and then clears it. """
        print(self, *args, **kwargs)
        self.data = ''
        return self

    def rainbow(
            self, text=None, fore=None, back=None, style=None,
            freq=0.1, offset=30, spread=3.0,
            linemode=True, movefactor=2, rgb_mode=False):
        """ Make rainbow gradient text.
            Arguments:
                text       : Text to make gradient.
                             Default: self.data
                fore       : Fore color to use (makes back the rainbow).
                             Default: None
                back       : Back color to use (makes fore the rainbow).
                             Default: None
                style      : Style for the rainbow.
                             Default: None
                freq       : Frequency of color change, a higher value means
                             more colors.
                             Best results when in the range 0.0-1.0.
                             Default: 0.1
                offset     : Offset for start of rainbow.
                             Default: 30
                spread     : Spread/width of each color.
                             Default: 3.0,
                linemode   : Colorize each line in the input.
                             Default: True
                movefactor : Factor for offset increase on each line when
                             using linemode.
                             Minimum value: 0
                             Default: 2
                rgb_mode   : Use RGB escape codes instead of extended 256 and
                             approximate hex matches.
        """
        if fore and back:
            raise ValueError('Cannot use both fore and back with rainbow()')

        rainbowargs = {
            'freq': freq,
            'spread': spread,
            'offset': offset,
            'fore': fore,
            'back': back,
            'style': style,
            'rgb_mode': rgb_mode,
        }
        if linemode:
            rainbowargs['movefactor'] = movefactor
            method = self._rainbow_lines
        else:
            method = self._rainbow_line

        if text:
            # Prepend existing self.data to the rainbow text.
            return self.__class__(
                ''.join((
                    self.data,
                    method(text, **rainbowargs)
                ))
            )

        # Operate on self.data.
        return self.__class__(
            method(self.stripped(), **rainbowargs)
        )

    def rgb(self, r, g, b, text=None, back=None, style=None):
        """ A chained method that sets the fore color to an RGB value.
            Arguments:
                r     : Red value.
                g     : Green value.
                b     : Blue value.
                text  : Text to style if not building up color codes.
                back  : Back color for the text.
                style : Style for the text.

        """
        return self.chained(text=text, fore=(r, g, b), back=back, style=style)

    def rstrip(self, chars=None):
        """ Like str.rstrip, except it returns the Colr instance. """
        return self.__class__(
            self._str_strip('rstrip', chars),
            no_closing=chars and (closing_code in chars),
        )

    def strip(self, chars=None):
        """ Like str.strip, except it returns the Colr instance. """
        return self.__class__(
            self._str_strip('strip', chars),
            no_closing=chars and (closing_code in chars),
        )


class ColrCodePart(CodePart):
    """ A CodePart(ChainedPart) from base.py that adds more info about the
        color code, like the code type (fore, back, style), and a known
        color name.
    """
    def __init__(self, originstr, start=None, stop=None):
        super().__init__(originstr, start=start, stop=stop)
        self.code_type, self.code_name = self.code_info()

    def code_info(self) -> ColrChainedPartInfo:
        """ Find the code type and color name/value from self.data. """
        if not self.data:
            return (None, None)
        known_info = get_known_name(self.data)
        if known_info is None:
            return (None, None)
        return known_info

    @classmethod
    def from_codepart(cls, part: CodePart) -> 'ColrCodePart':
        """ Copy the info from a CodePart, and return a new ColrCodePart. """
        colrpart = cls('', start=part.start, stop=part.stop)
        colrpart.data = part.data
        colrpart.code_type, colrpart.code_name = colrpart.code_info()
        return colrpart


class ColrTextPart(TextPart):
    """ A TextPart(ChainedPart) from base.py that is compatible with
        the ColrCodePart.
    """
    def __init__(self, originstr, start=None, stop=None):
        super().__init__(originstr, start=start, stop=stop)
        self.code_type = None
        self.code_name = None

    def code_info(self) -> ColrChainedPartInfo:
        return None, None

    @classmethod
    def from_textpart(cls, part: TextPart) -> 'ColrTextPart':
        """ Copy the info from a TextPart, and return a new ColrTextPart. """
        colrpart = cls('', start=part.start, stop=part.stop)
        colrpart.data = part.data
        return colrpart


class InvalidArg(ValueError):
    """ A ValueError for when the user uses invalid arguments. """
    default_label = 'Invalid argument'
    default_format = '{label}: {value}'

    def __init__(self, value, label=None):
        self.label = label or self.default_label
        self.value = value

    def __colr__(self):
        """ Allows Colr(InvalidArg()) with default styling. """
        return self.as_colr()

    def __str__(self):
        return self.default_format.format(
            label=self.label,
            value=repr(self.value)
        )

    def as_colr(self, label_args=None, value_args=None):
        """ Like __str__, except it returns a colorized Colr instance. """
        label_args = label_args or {'fore': 'red'}
        value_args = value_args or {'fore': 'blue', 'style': 'bright'}
        return Colr(self.default_format.format(
            label=Colr(self.label, **label_args),
            value=Colr(repr(self.value), **value_args),
        ))


# TODO: Remove all of this dynamic stuff, and hard-code the format strings
#       for each of the InvalidColr,InvalidFormatColr,InvalidFormatArg
#       exceptions. They can still be custom-colored. They're not using
#       inheritance very well anymore. They might as well be easier to read.
class InvalidColr(InvalidArg):
    """ A ValueError for when user passes an invalid colr name, value, rgb.
    """
    accepted_values = (
        ('hex', '[#]rgb/[#]rrggbb'),
        ('name', 'white/black/etc.'),
        ('rgb', '0-255, 0-255, 0-255'),
        ('value', '0-255'),
    )  # type: Tuple[Tuple[str, ...], ...]
    default_label = 'Expecting colr name/value:\n    {types}'.format(
        types=',\n    '.join(
            '{lbl:<5} ({val})'.format(lbl=l, val=v)
            for l, v in accepted_values
        )
    )
    default_format = '{label}\n    Got: {value}'

    def __colr__(self):
        """ Like __str__, except it returns a colorized Colr instance. """
        return self.as_colr()

    def as_colr(
            self, label_args=None, type_args=None, type_val_args=None,
            value_args=None):
        """ Like __str__, except it returns a colorized Colr instance. """
        label_args = label_args or {'fore': 'red'}
        type_args = type_args or {'fore': 'yellow'}
        type_val_args = type_val_args or {'fore': 'grey'}
        value_args = value_args or {'fore': 'blue', 'style': 'bright'}

        return Colr(self.default_format.format(
            label=Colr(':\n    ').join(
                Colr('Expecting color name/value', **label_args),
                ',\n    '.join(
                    '{lbl:<5} ({val})'.format(
                        lbl=Colr(l, **type_args),
                        val=Colr(v, **type_val_args),
                    )
                    for l, v in self.accepted_values
                )
            ),
            value=Colr(repr(self.value), **value_args)
        ))


class InvalidFormatColr(InvalidColr):
    """ A ValueError for when user passes an invalid colr name, value, rgb
        for a Colr.__format__ spec.
    """
    accepted_values = (
        ('hex', '[#]rgb/[#]rrggbb'),
        ('name', 'white/black/etc.'),
        ('rgb', '0-255; 0-255; 0-255'),
        ('value', '0-255'),
    )  # type: Tuple[Tuple[str, ...], ...]
    default_msg = 'Bad format spec. color name/value.'
    default_label = (
        '{{msg}} Expecting:\n    {types}'.format(
            types=',\n    '.join(
                '{lbl:<5} ({val})'.format(lbl=l, val=v)
                for l, v in accepted_values
            )
        )
    )
    default_format = '{label}\nGot: {value}\nIn spec: {spec}'

    def __init__(self, spec, value, msg=None):
        super().__init__(value)
        self.spec = spec
        self.msg = msg

    def __colr__(self):
        return self.as_colr()

    def __str__(self):
        return self.default_format.format(
            label=self.label.format(msg=self.msg or self.default_msg),
            value=repr(self.value),
            spec=repr(self.spec),
        )

    def as_colr(
            self, label_args=None, type_args=None, type_val_args=None,
            value_args=None, spec_args=None):
        """ Like __str__, except it returns a colorized Colr instance. """
        label_args = label_args or {'fore': 'red'}
        type_args = type_args or {'fore': 'yellow'}
        type_val_args = type_val_args or {'fore': 'grey'}
        value_args = value_args or {'fore': 'blue', 'style': 'bright'}
        spec_args = spec_args or {'fore': 'blue'}
        spec_repr = repr(self.spec)
        spec_quote = spec_repr[0]
        val_repr = repr(self.value)
        val_quote = val_repr[0]
        return Colr(self.default_format.format(
            label=Colr(':\n    ').join(
                Colr(
                    '{} Expecting'.format(self.msg or self.default_msg),
                    **label_args
                ),
                ',\n    '.join(
                    '{lbl:<5} ({val})'.format(
                        lbl=Colr(l, **type_args),
                        val=Colr(v, **type_val_args),
                    )
                    for l, v in self.accepted_values
                )
            ),
            spec=Colr('=').join(
                Colr(v, **spec_args)
                for v in spec_repr[1:-1].split('=')
            ).join((spec_quote, spec_quote)),
            value=Colr(
                val_repr[1:-1],
                **value_args
            ).join((val_quote, val_quote)),
        ))


class InvalidFormatArg(InvalidFormatColr):
    """ A ValueError for when user passes an invalid key/value
        for a Colr.__format__ spec.
    """
    accepted_keys = ('fore', 'back', 'style')
    example_values = {s: '{}_arg'.format(s) for s in accepted_keys}
    accepted_values = (
        (
            'keyed',
            ', '.join('{}={}'.format(k, v) for k, v in example_values.items())
        ),
        ('keyless', ', '.join('{}_arg'.format(s) for s in accepted_keys)),
    )
    default_msg = 'Bad format spec. argument.'
    default_label = (
        '{{msg}} Expecting:\n    {types}'.format(
            types=',\n    '.join(
                '{lbl:<8} [{val}]'.format(lbl=l, val=v)
                for l, v in accepted_values
            )
        )
    )

    def as_colr(
            self, label_args=None, type_args=None, type_val_args=None,
            value_args=None, spec_args=None):
        """ Like __str__, except it returns a colorized Colr instance. """
        label_args = label_args or {'fore': 'red'}
        type_args = type_args or {'fore': 'yellow'}
        type_val_args = type_val_args or {'fore': 'dimgrey'}
        value_args = value_args or {'fore': 'blue', 'style': 'bright'}
        spec_args = spec_args or {'fore': 'blue'}
        key_args = {'fore': 'blue'}
        spec_repr = repr(self.spec)
        spec_quote = spec_repr[0]
        val_repr = repr(self.value)
        val_quote = val_repr[0]
        colr_vals = (
            (
                'keyed',
                ', '.join(
                    '{}={}'.format(
                        Colr(k, **key_args),
                        Colr(v, **type_val_args)
                    )
                    for k, v in self.example_values.items())
            ),
            (
                'keyless',
                ', '.join(
                    str(Colr('{}_arg'.format(s), **type_val_args))
                    for s in self.accepted_keys
                )
            ),
        )
        return Colr(self.default_format.format(
            label=Colr(':\n    ').join(
                Colr(
                    '{} Expecting'.format(self.msg or self.default_msg),
                    **label_args
                ),
                ',\n    '.join(
                    '{lbl:<8} [{val}]'.format(
                        lbl=Colr(l, **type_args),
                        val=v,
                    )
                    for l, v in colr_vals
                )
            ),
            spec=Colr('=').join(
                Colr(v, **spec_args)
                for v in spec_repr[1:-1].split('=')
            ).join((spec_quote, spec_quote)),
            value=Colr(
                val_repr[1:-1],
                **value_args
            ).join((val_quote, val_quote)),
        ))


class InvalidEscapeCode(InvalidArg):
    """ A ValueError for when an invalid escape code is given. """
    default_label = 'Expecting 0-255 for escape code value'


class InvalidRgbEscapeCode(InvalidEscapeCode):
    """ A ValueError for when an invalid rgb escape code is given. """
    default_label = 'Expecting 0-255;0-255;0-255 for RGB escape code value'

    def __init__(self, value, label=None, reason=None):
        super().__init__(value, label=label)
        self.reason = reason

    def __str__(self):
        s = super().__str__(self)
        if self.reason:
            s = '\n   '.join((s, str(self.reason)))
        return s


class InvalidStyle(InvalidColr):
    default_label = 'Expecting style value:\n    {styles}'.format(
        styles='\n    '.join(
            ', '.join(t[1])
            for t in _stylemap
        )
    )

    def as_colr(
            self, label_args=None, type_args=None, value_args=None):
        """ Like __str__, except it returns a colorized Colr instance. """
        label_args = label_args or {'fore': 'red'}
        type_args = type_args or {'fore': 'yellow'}
        value_args = value_args or {'fore': 'blue', 'style': 'bright'}

        return Colr(self.default_format.format(
            label=Colr(':\n    ').join(
                Colr('Expecting style value', **label_args),
                Colr(',\n    ').join(
                    Colr(', ').join(
                        Colr(v, **type_args)
                        for v in t[1]
                    )
                    for t in _stylemap
                )
            ),
            value=Colr(repr(self.value), **value_args)
        ))


# Shortcuts.
color = Colr().color

if __name__ == '__main__':
    if ('--auto-disable' in sys.argv) or ('-a' in sys.argv):
        auto_disable()

    print(
        Colr('warning', 'red')
        .join('[', ']', style='bright')(' ')
        .green('This module is meant to be ran with `python -m colr`.')
    )
