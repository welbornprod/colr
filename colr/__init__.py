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
from .base import (
    __version__,
    ChainedBase,
    get_codes,
    strip_codes,
)
from .colr import (  # noqa
    Colr,
    InvalidArg,
    InvalidColr,
    InvalidFormatArg,
    InvalidFormatColr,
    InvalidEscapeCode,
    InvalidRgbEscapeCode,
    InvalidStyle,
    auto_disable,
    closing_code,
    codeformat,
    color,
    disable,
    disabled,
    enable,
    extbackformat,
    extforeformat,
    format_back,
    format_fore,
    get_all_names,
    get_code_num,
    get_known_codes,
    get_known_name,
    get_terminal_size,
    name_data,
    parse_colr_arg,
    rgbbackformat,
    rgbforeformat,
)

from .codes import (
    code_nums,
    code_nums_reverse,
    codes,
    codes_reverse,
)

from .controls import (  # noqa
    Control,
    EraseMethod,
)

from .colrcontrol import (
    ColrControl,
)

from .progress import (
    AnimatedProgress,
    ProgressBar,
    ProgressTimedOut,
    StaticProgress,
    WriterProcess,
)

from .progress_frames import (
    Bars,
    BarSet,
    Frames,
    FrameSet,
)

try:
    from .colr_docopt import (  # noqa
        docopt,
        docopt_file,
        docopt_version,
    )
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

from .preset import (
    Preset,
)

__all__ = [
    # base classes/functions made available.
    '__version__',
    'ChainedBase',
    'get_codes',
    'strip_codes',
    # colr classes/functions made available.
    'InvalidArg',
    'InvalidColr',
    'InvalidFormatArg',
    'InvalidFormatColr',
    'InvalidEscapeCode',
    'InvalidRgbEscapeCode',
    'InvalidStyle',
    'auto_disable',
    'closing_code',
    'code_nums',
    'code_nums_reverse',
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
    'get_all_names',
    'get_code_num',
    'get_known_codes',
    'get_known_name',
    'get_terminal_size',
    'name_data',
    'parse_colr_arg',
    'rgbbackformat',
    'rgbforeformat',
    # controls functions/classes made available.
    'Control',
    'EraseMethod',
    # colrcontrol classes made available.
    'ColrControl',
    # progress functions/classes made available.
    'AnimatedProgress',
    'ProgressBar',
    'ProgressTimedOut',
    'StaticProgress',
    'WriterProcess',
    # progress frame classes made available.
    'Bars',
    'BarSet',
    'Frames',
    'FrameSet',
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
    'term2rgb',
    # Preset stuff made available.
    'Preset',
]

if has_docopt:
    __all__.append('docopt')
    __all__.append('docopt_version')
    __all__.append('docopt_file')
