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
    def __init__(self, iterable=None, name=None):
        super().__init__(iterable)
        self.name = name or self.__class__.__qualname__

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

    def as_gradient(self, name=None, style=None):
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
                C(char, style=style).rainbow(
                    offset=offset + i,
                    spread=1,
                )
            )
        return self.__class__(colrs)

    def as_rainbow(self, offset=35, style=None):
        """ Wrap each frame in a Colr object, using `Colr.rainbow`. """
        colrs = []
        for i, char in enumerate(self):
            colrs.append(
                C(char, style=style).rainbow(
                    offset=offset + i,
                    freq=0.25,
                    spread=1,
                )
            )
        return self.__class__(colrs)


class Frames(object):
    """ A collection of frames/spinners that can be used with Progress. """
    # This is set after _build_color_frames() is called.
    names = []

    # Basic non-color framelists.
    arc = FrameList('◜◠◝◞◡◟' * 3, name='arc')
    arrows = FrameList(
        (
            '▹▹▹▹▹',
            '▸▹▹▹▹',
            '▹▸▹▹▹',
            '▹▹▸▹▹',
            '▹▹▹▸▹',
            '▹▹▹▹▸'
        ),
        name='arrows',
    )
    bounce = FrameList('⠁⠂⠄⠂' * 6, name='bounce')
    bouncing_ball = FrameList(
        (
            '( ●    )',
            '(  ●   )',
            '(   ●  )',
            '(    ● )',
            '(     ●)',
            '(    ● )',
            '(   ●  )',
            '(  ●   )',
            '( ●    )',
            '(●     )',
        ),
        name='bouncing_ball',
    )
    dots = FrameList('⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏' * 3, name='dots')
    dots_orbit = FrameList('⢄⢂⢁⡁⡈⡐⡠' * 3, name='dots_orbit')
    dots_chase = FrameList(
        (
            '⢀⠀',
            '⡀⠀',
            '⠄⠀',
            '⢂⠀',
            '⡂⠀',
            '⠅⠀',
            '⢃⠀',
            '⡃⠀',
            '⠍⠀',
            '⢋⠀',
            '⡋⠀',
            '⠍⠁',
            '⢋⠁',
            '⡋⠁',
            '⠍⠉',
            '⠋⠉',
            '⠋⠉',
            '⠉⠙',
            '⠉⠙',
            '⠉⠩',
            '⠈⢙',
            '⠈⡙',
            '⢈⠩',
            '⡀⢙',
            '⠄⡙',
            '⢂⠩',
            '⡂⢘',
            '⠅⡘',
            '⢃⠨',
            '⡃⢐',
            '⠍⡐',
            '⢋⠠',
            '⡋⢀',
            '⠍⡁',
            '⢋⠁',
            '⡋⠁',
            '⠍⠉',
            '⠋⠉',
            '⠋⠉',
            '⠉⠙',
            '⠉⠙',
            '⠉⠩',
            '⠈⢙',
            '⠈⡙',
            '⠈⠩',
            '⠀⢙',
            '⠀⡙',
            '⠀⠩',
            '⠀⢘',
            '⠀⡘',
            '⠀⠨',
            '⠀⢐',
            '⠀⡐',
            '⠀⠠',
            '⠀⢀',
            '⠀⡀',
        ),
        name='dots_chase',
    )
    hamburger = FrameList(('☱ ', '☲ ', '☴ '), name='hamburger')

    @classmethod
    def get_by_name(cls, name):
        try:
            val = getattr(cls, name)
        except AttributeError:
            for attr in (a for a in dir(cls) if not a.startswith('_')):
                try:
                    val = getattr(cls, attr)
                except AttributeError:
                    # Is known to happen.
                    continue
                valname = getattr(val, 'name', None)
                if valname == name:
                    return val
            else:
                raise ValueError('No FrameList with that name: {}'.format(
                    name
                ))
        else:
            return val


_colornames = (
    # 'black',
    'red',
    'green',
    'yellow',
    'blue',
    'magenta',
    'cyan',
    'white',
)


def _build_color_frames():
    """ Build colorized variants of all frames and return a list of
        all frame object names.
    """
    frametypes = []
    for attr in [a for a in dir(Frames) if not a.startswith('_')]:
        try:
            frameobj = getattr(Frames, attr)
        except AttributeError:
            # Has happened before, not here. I've seen it though.
            continue
        if isinstance(frameobj, FrameList):
            frametypes.append(frameobj)

    # Initially, frame_names only contains the basic framelist types.
    frame_names = [frameobj.name for frameobj in frametypes]
    for colorname in _colornames:
        for framesobj in frametypes:
            framename = '{}_{}'.format(framesobj.name, colorname)
            newframes = framesobj.as_colr(fore=colorname)
            newframes.name = framename
            setattr(Frames, framename, newframes)
            frame_names.append(framename)

    for gradname in C.gradient_names:
        for framesobj in frametypes:
            framename = '{}_gradient_{}'.format(framesobj.name, gradname)
            newframes = framesobj.as_gradient(name=gradname)
            newframes.name = framename
            setattr(Frames, framename, newframes)
            frame_names.append(framename)

    for framesobj in frametypes:
        framename = '{}_rainbow'.format(framesobj.name)
        newframes = framesobj.as_rainbow()
        newframes.name = framename
        setattr(Frames, framename, newframes)
        frame_names.append(framename)
    return frame_names


Frames.names = _build_color_frames()
# Default frames to use when none are specified.
Frames.default = Frames.dots_blue
