#!/usr/bin/env python3
""" Colr - Progress - Frames
    A collection of frames for `colr.progress.Progress`.

    -Christopher Welborn 3-12-17
"""

from collections import UserList

from .colr import Colr as C


class FrameList(UserList):
    """ A single spinner frame list, with helper methods for colorizing each
        frame.
    """
    def __init__(self, iterable=None):
        super().__init__(iterable)

    def __bool__(self):
        return bool(self.data)

    def as_colr(self, **kwargs):
        """ Wrap each frame in a Colr object, using `kwargs` for Colr().
            Keyword Arguments:
                fore  : Fore color for each frame.
                back  : Back color for each frame.
                style : Style for each frame.
        """
        return self.__class__(C(s, **kwargs) for s in self)

    def as_gradient(self, name=None):
        """ Wrap each frame in a Colr object, using `Colr.gradient`.
            Arguments:
                name  : Starting color name. One of `Colr.gradient_names`.
        """
        offset = C.gradient_names.get(name, None)
        if offset is None:
            offset = C.gradient_names['blue']
        colrs = []
        for i, char in enumerate(self):
            colrs.append(
                C(char, style='bright').rainbow(
                    offset=offset + i,
                    spread=1,
                )
            )
        return self.__class__(colrs)

    def as_rainbow(self, offset=35):
        """ Wrap each frame in a Colr object, using `Colr.rainbow`. """
        colrs = []
        for i, char in enumerate(self):
            colrs.append(
                C(char, style='bright').rainbow(
                    offset=offset + i,
                    freq=0.25,
                    spread=1,
                )
            )
        return self.__class__(colrs)


class Frames(object):
    """ A collection of frames/spinners that can be used with Progress. """
    dots = FrameList('⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏' * 3)


for colorname in ('blue', 'red', 'yellow', 'magenta'):
    setattr(
        Frames,
        'dots_{}'.format(colorname),
        Frames.dots.as_colr(
            fore=colorname,
            style='bright',
        )
    )

for gradname in C.gradient_names:
    setattr(
        Frames,
        'dots_gradient_{}'.format(gradname),
        Frames.dots.as_gradient(name=gradname)
    )
Frames.dots_rainbow = Frames.dots.as_rainbow()
# Default frames to use when none are specified.
Frames.default = Frames.dots_blue
