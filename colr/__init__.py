""" colr.py
    A terminal color library for python, inspired by the JS lib "clor".
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
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.

"""

from .colr import (  # noqa
    __version__,
    Colr,
    auto_disable,
    closing_code,
    codeformat,
    codes,
    codes_reverse,
    color,
    disable,
    disabled,
    enable,
    extbackformat,
    extforeformat,
    format_back,
    format_fore,
    get_codes,
    get_code_num,
    get_known_codes,
    get_known_name,
    get_terminal_size,
    InvalidArg,
    InvalidColr,
    InvalidEscapeCode,
    InvalidRgbEscapeCode,
    InvalidStyle,
    parse_colr_arg,
    name_data,
    rgbbackformat,
    rgbforeformat,
    strip_codes,
)

from .controls import (  # noqa
    Control,
    EraseMethod,
)

from .progress import (
    AnimatedProgress,
    StaticProgress,
    WriterProcess,
)

from .progress_frames import (
    FrameSet,
    Frames,
)

try:
    from .colr_docopt import docopt  # noqa
    has_docopt = True
except ImportError:
    has_docopt = False

from .trans import (
    ColorCode,
    fix_hex,
    hex2rgb,
    hex2term,
    hex2term_map,
    hex2termhex,
    rgb2hex,
    rgb2term,
    rgb2termhex,
    term2hex,
    term2hex_map,
    term2rgb
)

__all__ = [
    '__version__',
    'auto_disable',
    'closing_code',
    'codeformat',
    'codes',
    'codes_reverse',
    'color',
    'Colr',
    'disable',
    'disabled',
    'enable',
    'extbackformat',
    'extforeformat',
    'format_back',
    'format_fore',
    'get_codes',
    'get_code_num',
    'get_known_codes',
    'get_known_name',
    'get_terminal_size',
    'InvalidArg',
    'InvalidColr',
    'InvalidEscapeCode',
    'InvalidRgbEscapeCode',
    'InvalidStyle',
    'name_data',
    'parse_colr_arg',
    'rgbforeformat',
    'rgbbackformat',
    'strip_codes',
    # controls functions/classes made available.
    'Control',
    'EraseMethod',
    # progress functions/classes made available.
    'AnimatedProgress',
    'StaticProgress',
    'WriterProcess',
    # progress frame classes made available.
    'FrameSet',
    'Frames',
    # trans functions made available.
    'ColorCode',
    'fix_hex',
    'hex2rgb',
    'hex2term',
    'hex2term_map',
    'hex2termhex',
    'rgb2hex',
    'rgb2term',
    'rgb2termhex',
    'term2hex',
    'term2hex_map',
    'term2rgb'
]
if has_docopt:
    __all__.append('docopt')
