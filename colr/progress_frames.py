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
    default_delay = 0.1

    def __init__(self, iterable, name=None, delay=None):
        self.data = tuple(iterable)
        if not self.data:
            raise ValueError(
                'Empty FrameSet is not allowed. Got: {!r}'.format(
                    iterable,
                )
            )
        self.name = str(name or '').strip().lower()

        self.delay = delay or self.default_delay
        if not (isinstance(self.delay, (float, int)) or (self.delay is None)):
            raise TypeError(
                ' '.join((
                    'Expecting None, float, or int for delay.',
                    'Got: ({}) {!r}'
                )).format(
                    type(self.delay).__name__,
                    self.delay,
                )
            )

    def __add__(self, other):
        """ FrameSets can be extended with other self.data lists/tuples, or
            builtin lists/tuples.
        """
        otherdata = getattr(other, 'data', None)
        if isinstance(otherdata, tuple):
            return self.__class__(self.data + other.data)
        elif isinstance(otherdata, list):
            return self.__class__(self.data + tuple(other.data))
        elif isinstance(other, tuple):
            return self.__class__(self.data + other)
        elif isinstance(other, list):
            return self.__class__(self.data + tuple(other))
        else:
            raise TypeError(
                ' '.join((
                    'Expecting list, tuple,',
                    'or object with a list or tuple data attribute.',
                    'Got: ({}) {!r}'
                )).format(
                    type(other).__name__,
                    other,
                )
            )

    def __bool__(self):
        return bool(self.data)

    def __bytes__(self):
        """ bytes(FrameSet()) is the same as str(FrameSet()).encode(). """
        return str(self).encode()

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

    def __mul__(self, n):
        """ The data tuple for this frameset can be multiplied by a number.
            It returns `FrameSet(self.data * n)`.
        """
        if not isinstance(n, int):
            raise TypeError(
                'Cannot multiply FrameSet by non-int type: {}'.format(
                    type(n).__name__
                )
            )

        return self.__class__(self.data * n)

    def __radd__(self, other):
        return self.__add__(other)

    def __reversed__(self):
        return self.__class__(reversed(self.data))

    def __rmul__(self, other):
        return self.__mul__(other)

    def __setitem__(self, key, value):
        raise TypeError('FrameSet does not support assignment.')

    def __str__(self):
        """ A string representation of this FrameSet is it's frames joined
            together.
        """
        return ''.join(str(x) for x in self)

    def __repr__(self):
        """ Eval-friendly representation of this FrameSet. """
        return ''.join((
            '{clsname}',
            '({s.name!r}, {s.data!r}, delay={s.delay!r})'
        )).format(clsname=self.__class__.__name__, s=self)

    def as_colr(self, **kwargs):
        """ Wrap each frame in a Colr object, using `kwargs` for Colr().
            Keyword Arguments:
                fore  : Fore color for each frame.
                back  : Back color for each frame.
                style : Style for each frame.
        """
        return self.__class__(
            (C(s, **kwargs) for s in self),
            name='custom_{}_as_colr'.format((self.name)),
            delay=self.delay,
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
            colrs,
            name='custom_{}_as_gradient'.format(self.name),
            delay=self.delay,
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
        return self.__class__(
            colrs,
            name='custom_{}_as_rainbow'.format(self.name),
            delay=self.delay,
        )


class Frames(object):
    """ A collection of frames/spinners that can be used with Progress. """

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

    @classmethod
    def names(cls):
        """ Return a list of names for all FrameSet attributes in this class.
        """
        names = []
        for attr in dir(cls):
            if attr.startswith('_'):
                continue
            if not isinstance(getattr(cls, attr, None), FrameSet):
                continue
            names.append(attr)
        return names

    @classmethod
    def register(cls, frameset, name=None):
        """ Register a new FrameSet as a member/attribute of this class.
            Returns the new FrameSet.
            Arguments:
                frameset  : An existing FrameSet, or an iterable of strings.
                name      : New name for the FrameSet, also used as the
                            classes attribute name.
                            If the `frameset` object has not `name` attribute,
                            this argument is required. It must not be empty
                            when given.
        """
        name = name or getattr(frameset, 'name', None)
        if name is None:
            raise ValueError(
                '`name` is needed when the `frameset` has no name attribute.'
            )
        newframeset = FrameSet(
            frameset,
            name=name,
            delay=getattr(frameset, 'delay', None)
        )
        setattr(cls, name, newframeset)
        return newframeset

    # Basic non-color framelists.
    arc = FrameSet('◜◠◝◞◡◟' * 3, name='arc', delay=0.25)
    # arrows kinda works in a 'TERM=linux' terminal, the black arrows will be
    # missing.
    arrows = FrameSet(
        (
            '▹▹▹▹▹',
            '▸▹▹▹▹',
            '▹▸▹▹▹',
            '▹▹▸▹▹',
            '▹▹▹▸▹',
            '▹▹▹▹▸'
        ),
        name='arrows',
        delay=0.25,
    )
    bounce = FrameSet('⠁⠂⠄⠂' * 6, name='bounce', delay=0.25)
    # bouncing_ball works in a 'TERM=linux' terminal (basic, with bad fonts)
    bouncing_ball = FrameSet(
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
    dots = FrameSet('⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏' * 3, name='dots')
    dots_orbit = FrameSet('⢄⢂⢁⡁⡈⡐⡠' * 3, name='dots_orbit')
    dots_chase = FrameSet(
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
    # The hamburger FrameSet has display problems on my terminal.
    hamburger = FrameSet(('☱ ', '☲ ', '☴ '), name='hamburger', delay=0.5)


def _build_color_frames():
    """ Build colorized variants of all frames and return a list of
        all frame object names.
    """
    # Get the basic frame types first.
    frametypes = [getattr(Frames, name) for name in Frames.names()]

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
            Frames.register(framesobj.as_colr(fore=colorname), name=framename)

    for gradname in C.gradient_names:
        if gradname in ('white', ):
            # This gradient name does not work as advertised.
            continue
        for framesobj in frametypes:
            framename = '{}_gradient_{}'.format(framesobj.name, gradname)
            Frames.register(
                framesobj.as_gradient(name=gradname),
                name=framename
            )

    for framesobj in frametypes:
        framename = '{}_rainbow'.format(framesobj.name)
        Frames.register(framesobj.as_rainbow(), name=framename)
    return None


_build_color_frames()
# Default frames to use when none are specified.
Frames.default = Frames.dots_blue
