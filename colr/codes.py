#!/usr/bin/env python3

""" colr/codes.py
    A dict of fore, back, and style names to escape code.
    -Christopher Welborn 05-23-2019
"""

from typing import (
    Callable,
    Dict,
    Tuple,
    Union,
)
# Types for the type checker.
CodeFormatArg = Union[str, int]
CodeFormatFunc = Callable[[CodeFormatArg], str]
CodeFormatRgbFunc = Callable[[int, int, int], str]

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
)  # type: Tuple[Tuple[str, int], ...]

# Public list of names.
basic_names = tuple(
    t[0] for t in _namemap
)  # type: Tuple[str, ...]

# Map of base code -> style name/alias.
_stylemap = (
    (0, ('0', 'reset_all',)),
    (1, ('1', 'b', 'bright', 'bold')),
    (2, ('2', 'd', 'dim')),
    (3, ('3', 'i', 'italic')),
    (4, ('4', 'u', 'underline', 'underlined')),
    (5, ('5', 'f', 'flash')),
    (7, ('7', 'h', 'highlight', 'hilight', 'hilite', 'reverse')),
    (22, ('22', 'n', 'normal', 'none'))
)  # type: Tuple[Tuple[int, Tuple[str, ...]], ...]
# A tuple of valid style numbers.
_stylenums = tuple(str(t[0]) for t in _stylemap)  # type: Tuple[str, ...]


# Build a module-level map of fore, back, and style names to escape code.
codeformat = '\033[{}m'.format  # type: CodeFormatFunc
extforeformat = '\033[38;5;{}m'.format  # type: CodeFormatFunc
extbackformat = '\033[48;5;{}m'.format  # type: CodeFormatFunc
rgbforeformat = '\033[38;2;{};{};{}m'.format  # type: CodeFormatRgbFunc
rgbbackformat = '\033[48;2;{};{};{}m'.format  # type: CodeFormatRgbFunc


def _build_code_nums() -> Dict[str, Dict[str, int]]:
    """ Build code map, encapsulated to reduce module-level globals. """
    built = {
        'fore': {},
        'fore_ext': {},
        'back': {},
        'back_ext': {},
        'style': {},
    }  # type: Dict[str, Dict[str, int]]

    # Set codes for forecolors (30-37) and backcolors (40-47)
    # Names are given to some of the 256-color variants as 'light' colors.
    for name, number in _namemap:
        # Not using format_* functions here, no validation needed.
        built['fore'][name] = 30 + number
        built['back'][name] = 40 + number

        # Light colors (90-97 for fore, and 100-107 for bg.)
        litename = 'light{}'.format(name)  # type: str
        built['fore'][litename] = 90 + number
        built['back'][litename] = 100 + number

    # Set reset codes for fore/back.
    built['fore']['reset'] = 39
    built['back']['reset'] = 49

    # Set style codes.
    for code, names in _stylemap:
        for alias in names:
            built['style'][alias] = code

    # Extended (256 color codes)
    for i in range(256):
        built['fore_ext'][str(i)] = i
        built['back_ext'][str(i)] = i

    return built


def _build_code_nums_reverse() -> Dict[str, Dict[int, str]]:
    """ Build a reverse code number to name map. """
    built = {}  # type: Dict[str, Dict[int, str]]
    for codetype, codemap in code_nums.items():
        for name, codenum in codemap.items():
            # Skip shorcut aliases to avoid overwriting long names.
            if (not name.isdigit()) and len(name) < 2:
                continue
            if built.get(codetype, None) is None:
                built[codetype] = {}
            built[codetype][codenum] = name
    return built


def _build_codes() -> Dict[str, Dict[str, str]]:
    """ Build code map, encapsulated to reduce module-level globals. """
    built = {
        'fore': {},
        'back': {},
        'style': {},
    }  # type: Dict[str, Dict[str, str]]

    for code_type, nameinfo in code_nums.items():
        if code_type in ('fore', 'back', 'style'):
            built[code_type] = {k: codeformat(v) for k, v in nameinfo.items()}
        elif code_type == 'fore_ext':
            built['fore'].update(
                {k: extforeformat(v) for k, v in nameinfo.items()}
            )
        elif code_type == 'back_ext':
            built['back'].update(
                {k: extbackformat(v) for k, v in nameinfo.items()}
            )

    return built


def _build_codes_reverse(
        codes: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    """ Build a reverse escape-code to name map, based on an existing
        name to escape-code map.
    """
    built = {}  # type: Dict[str, Dict[str, str]]
    for codetype, codemap in codes.items():
        for name, escapecode in codemap.items():
            # Skip shorcut aliases to avoid overwriting long names.
            if len(name) < 2:
                continue
            if built.get(codetype, None) is None:
                built[codetype] = {}
            built[codetype][escapecode] = name
    return built


def _add_alias_names(d: Dict[str, Dict[str, str]]) -> None:
    """ Add some short aliases for basic colors and light colors. """
    aliases = {
        'fore': {s[0]: s for s in basic_names},
        'back': {s[0]: s for s in basic_names},
    }
    for codetype in ('fore', 'back'):
        aliases[codetype].update({
            'l{}'.format(s[0]): 'light{}'.format(s)
            for s in basic_names
        })
        # Special case for blue/black because they start with the same char.
        # Blue should have the one char alias because it is used more.
        aliases[codetype]['b'] = 'blue'
        aliases[codetype]['bl'] = 'black'
        aliases[codetype]['blk'] = 'black'
        aliases[codetype]['lb'] = 'lightblue'
        aliases[codetype]['lbl'] = 'lightblack'
        aliases[codetype]['lblk'] = 'lightblack'

    # Update the codes dict with these aliases.
    for codetype, aliasinfo in aliases.items():
        for shortname, fullname in aliasinfo.items():
            d[codetype][shortname] = d[codetype][fullname]


# Make plain code numbers available to the user.
code_nums = _build_code_nums()
code_nums_reverse = _build_code_nums_reverse()
# Raw code map, available to users.
codes = _build_codes()
codes_reverse = _build_codes_reverse(codes)
# Short aliases are added for convenience.
_add_alias_names(codes)
