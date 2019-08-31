#!/usr/bin/env python3

""" colr/style.py
    Preset object for the Colr class.
    A callable that will wrap it's argument in a Colr using the arguments
    given on __init__.
    -Christopher Welborn 05-21-2019
"""

from functools import total_ordering
from .colr import Colr


@total_ordering
class Preset(object):
    """ Colr arg dict for fore, back, and style arguments.
        Callable to wrap strings in a Colr that uses these arguments.
        Example:
            warn = Preset('red', 'white', 'bold')
            print(warn('Watch out!'))

    """
    __slots__ = ('fore', 'back', 'style')

    def __init__(self, fore=None, back=None, style=None):
        self.fore = fore
        self.back = back
        self.style = style

    def __call__(self, text, fore=None, back=None, style=None):
        """ Calling a Preset returns a Colr instance.
            Preset arguments can be temporarily overwritten by providing them
            to this call.
        """
        return Colr(
            text,
            fore=self.fore if fore is None else fore,
            back=self.back if back is None else back,
            style=self.style if style is None else style,
        )

    def __eq__(self, other):
        if not isinstance(other, Preset):
            raise TypeError(
                'Expecting a Preset instance, got: ({}) {!r}'.format(
                    type(other).__name__,
                    other,
                )
            )
        return (
            self.fore == other.fore and
            self.back == other.back and
            self.style == other.style
        )

    def __hash__(self):
        return hash((self.fore, self.back, self.style))

    def __lt__(self, other):
        if not isinstance(other, Preset):
            raise TypeError(
                'Expecting a Preset instance, got: ({}) {!r}'.format(
                    type(other).__name__,
                    other,
                )
            )
        return (
            (self.fore, self.back, self.style) <
            (other.fore, other.back, other.style)
        )

    def __repr__(self):
        return (
            '{t}(fore={s.fore!r}, back={s.back!r}, style={s.style!r})'.format(
                t=type(self).__name__,
                s=self,
            )
        )

    def as_dict(self):
        d = {}
        if self.fore is not None:
            d['fore'] = self.fore
        if self.back is not None:
            d['back'] = self.back
        if self.style is not None:
            d['style'] = self.style
        return d

    def merge(self, styleobj, fore=None, back=None, style=None):
        """ Merge new Colr arguments with this Preset and return a new Preset.
        """
        d = self.as_dict()
        d.update(styleobj.as_dict())
        args = self.__class__(fore=fore, back=back, style=style)
        d.update(args.as_dict())
        return self.__class__(**d)
