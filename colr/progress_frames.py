#!/usr/bin/env python3
""" Colr - Progress - Frames
    A collection of frames for `colr.progress.Progress`.

    -Christopher Welborn 3-12-17
"""
from functools import total_ordering

from .colr import Colr as C


@total_ordering
class FrameSet(object):
    """ A single spinner/progress frame list, with helper methods for
        colorizing each frame. A FrameSet actually behaves like a `tuple`.
        It is immutable, hashable, and comparable.
    """
    def __init__(self, name, iterable):
        self.data = tuple(iterable)
        if not self.data:
            raise ValueError(
                'Empty FrameSet is not allowed. Got: {!r}'.format(
                    iterable,
                )
            )
        self.name = str(name).strip().lower()
        if not self.name:
            raise ValueError('Empty name is not allowed. Got: {!r}'.format(
                name,
            ))

    def __bool__(self):
        return bool(self.data)

    def __contains__(self, value):
        return value in self.data

    def __getitem__(self, index):
        return self.data[index]

    def __hash__(self):
        return hash(self.data)

    def __iter__(self):
        return self.data.__iter__()

    def __len__(self):
        return len(self.data)

    def __lt__(self, other):
        if isinstance(getattr(other, 'data', None), tuple):
            return self.data < other.data
        return self.data < other

    def __reversed__(self):
        return self.__class__(reversed(self.data))

    def __setitem__(self, key, value):
        raise TypeError('FrameSet does not support assignment.')

    def as_colr(self, **kwargs):
        """ Wrap each frame in a Colr object, using `kwargs` for Colr().
            Keyword Arguments:
                fore  : Fore color for each frame.
                back  : Back color for each frame.
                style : Style for each frame.
        """
        return self.__class__(
            'custom_{}_as_colr'.format((self.name)),
            (C(s, **kwargs) for s in self)
        )

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
        return self.__class__(
            'custom_{}_as_gradient'.format(self.name),
            colrs
        )

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
        return self.__class__('custom_{}_as_rainbow'.format(self.name), colrs)


class Frames(object):
    """ A collection of frames/spinners that can be used with Progress. """
    # This is set after _build_color_frames() is called.
    names = []

    # Basic non-color framelists.
    arc = FrameSet('arc', '◜◠◝◞◡◟' * 3)
    # arrows kinda works in a 'TERM=linux' terminal, the black arrows will be
    # missing.
    arrows = FrameSet(
        'arrows',
        (
            '▹▹▹▹▹',
            '▸▹▹▹▹',
            '▹▸▹▹▹',
            '▹▹▸▹▹',
            '▹▹▹▸▹',
            '▹▹▹▹▸'
        ),
    )
    bounce = FrameSet('bounce', '⠁⠂⠄⠂' * 6)
    # bouncing_ball works in a 'TERM=linux' terminal (basic, with bad fonts)
    bouncing_ball = FrameSet(
        'bouncing_ball',
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
    )
    dots = FrameSet('dots', '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏' * 3)
    dots_orbit = FrameSet('dots_orbit', '⢄⢂⢁⡁⡈⡐⡠' * 3)
    dots_chase = FrameSet(
        'dots_chase',
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
        )
    )
    hamburger = FrameSet('hamburger', ('☱ ', '☲ ', '☴ '))

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
                raise ValueError('No FrameSet with that name: {}'.format(
                    name
                ))
        else:
            return val


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
        if isinstance(frameobj, FrameSet):
            frametypes.append(frameobj)

    # Initially, frame_names only contains the basic framelist types.
    frame_names = [frameobj.name for frameobj in frametypes]

    _colornames = [
        # 'black', disabled for now, it won't show on my terminal.
        'red',
        'green',
        'yellow',
        'blue',
        'magenta',
        'cyan',
        'white',
    ]
    _colornames.extend('light{}'.format(s) for s in _colornames[:])
    for colorname in _colornames:
        for framesobj in frametypes:
            framename = '{}_{}'.format(framesobj.name, colorname)
            newframes = framesobj.as_colr(fore=colorname)
            newframes.name = framename
            setattr(Frames, framename, newframes)
            frame_names.append(framename)

    for gradname in C.gradient_names:
        if gradname in ('white', ):
            # This gradient name does not work as advertised.
            continue
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
    return sorted(frame_names)


Frames.names = _build_color_frames()
# Default frames to use when none are specified.
Frames.default = Frames.dots_blue
