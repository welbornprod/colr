#!/usr/bin/env python3
""" Colr - Progress - Frames
    A collection of frames for `colr.progress.Progress`.

    -Christopher Welborn 3-12-17

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
from collections import namedtuple
from functools import total_ordering

from .colr import Colr as C


# Argument set for `range` in `BarSet._generate_move`.
RangeMoveArgs = namedtuple('RangeMoveArgs', ('forward', 'backward'))


def cls_get_by_name(cls, name):
    """ Return a class attribute by searching the attributes `name` attribute.
    """
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
            raise ValueError('No {} with that name: {}'.format(
                cls.__name__,
                name,
            ))
    else:
        return val


def cls_names(cls, wanted_cls, registered=True):
    """ Return a list of attributes for all `wanted_cls` attributes in this
        class, where `wanted_cls` is the desired attribute type.
    """
    return [
        fset.name
        for fset in cls_sets(cls, wanted_cls, registered=registered)
    ]


def cls_register(cls, frameset, new_class, init_args, name=None):
    """ Register a new FrameSet or FrameSet subclass as a member/attribute
        of a class.
        Returns the new FrameSet or FrameSet subclass.
        Arguments:
            frameset  : An existing FrameSet, or an iterable of strings.
            init_args : A list of properties from the `frameset` to try to use
                        for initializing the new FrameSet.
            new_class : The class type to initialize.
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
    kwargs = {'name': name}
    for initarg in init_args:
        kwargs[initarg] = getattr(frameset, initarg, None)

    newframeset = new_class(frameset, **kwargs)
    # Mark this FrameSet/BarSet as a registered item (not basic/original).
    newframeset._registered = True
    setattr(cls, name, newframeset)
    return newframeset


def cls_sets(cls, wanted_cls, registered=True):
    """ Return a list of all `wanted_cls` attributes in this
        class, where `wanted_cls` is the desired attribute type.
    """
    sets = []
    for attr in dir(cls):
        if attr.startswith('_'):
            continue
        val = getattr(cls, attr, None)
        if not isinstance(val, wanted_cls):
            continue
        if (not registered) and getattr(val, '_registered', False):
            continue
        sets.append(val)
    return sets


@total_ordering
class FrameSetBase(object):
    """ The base class for FrameSets/BarSets. Shares specialized methods
        for building new FrameSets/BarSets.
    """
    def __init__(self):
        raise NotImplementedError('FrameSetBase.__init__ must be overridden.')

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

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(
                'Cannot compare {} to {}.'.format(
                    type(self).__name__,
                    type(other).__name__,
                )
            )
        return (
            (self.data == getattr(other, 'data', None)) and
            (self.name == getattr(other, 'name', None))
        )

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
                'Cannot multiply {} by non-int type: {}'.format(
                    type(self).__name__,
                    type(n).__name__
                )
            )

        return self.__class__(self.data * n)

    def __radd__(self, other):
        return self.__add__(other)

    def __reversed__(self):
        return self.__class__(
            reversed(self.data),
            name='reversed_{}'.format(self.name),
        )

    def __rmul__(self, other):
        return self.__mul__(other)

    def __setitem__(self, key, value):
        raise TypeError('{} does not support assignment.'.format(
            type(self).__name__,
        ))

    def __str__(self):
        """ A string representation of this FrameSet is it's frames joined
            together.
        """
        return ''.join(str(x) for x in self)

    def _as_colr(self, init_args, **kwargs):
        """ Wrap each frame of a FrameSet or FrameSet subclass in a Colr object,
            using `kwargs` for Colr().
            Arguments:
                init_args  : A list of properties to get from the instance and
                             use for initializing the new instance.

            Keyword Arguments:
                fore       : Fore color for each frame.
                back       : Back color for each frame.
                style      : Style for each frame.
        """
        clsargs = {'name': 'custom_{}_as_colr'.format(self.name)}
        for initarg in init_args:
            clsargs[initarg] = getattr(self, initarg, None)
        newfset = self.__class__(
            (C(s, **kwargs) for s in self),
            **clsargs,
        )
        return newfset

    def _as_gradient(self, init_args, name=None, style=None, rgb_mode=False):
        """ Wrap each frame of a FrameSet or FrameSet subclass in a Colr object,
            using `Colr.gradient`.
            Arguments:
                init_args : A list of properties to get from the instance and
                            use for initializing the new instance.
                name      : Starting color name. One of `Colr.gradient_names`.
                style     : Style arg for Colr.
                rgb_mode  : Whether to use RGB codes, instead of extended
                            256 color approximate matches.
        """
        # TODO: Better, smoother gradients.
        offset = C.gradient_names.get(name, None)
        if offset is None:
            offset = C.gradient_names['blue']
        colrs = []
        for i, char in enumerate(self):
            colrs.append(
                C(char, style=style).rainbow(
                    offset=offset + i,
                    spread=1,
                    rgb_mode=rgb_mode,
                )
            )
        namefmt = 'custom_{}_as_gradient'
        if rgb_mode:
            namefmt = ''.join((namefmt, '_rgb'))
        clsargs = {'name': namefmt.format(self.name)}
        for initarg in init_args:
            clsargs[initarg] = getattr(self, initarg, None)
        return self.__class__(colrs, **clsargs)

    def _as_rainbow(self, init_args, offset=35, style=None, rgb_mode=False):
        """ Wrap each frame of a FrameSet or FrameSet subclass in a Colr
            object, using `Colr.rainbow`.
            Arguments:
                init_args  : A list of properties to get from the instance and
                             use for initializing the new instance.
                offset     : Starting offset for the rainbow.
                style      : Style arg for Colr.
                rgb_mode   : Whether to use RGB codes, instead of extended
                             256 color approximate matches.
        """
        colrs = []
        for i, char in enumerate(self):
            colrs.append(
                C(char, style=style).rainbow(
                    offset=offset + i,
                    freq=0.25,
                    spread=1,
                    rgb_mode=rgb_mode,
                )
            )
        clsargs = {'name': 'custom_{}_as_rainbow'.format(self.name)}
        for initarg in init_args:
            clsargs[initarg] = getattr(self, initarg, None)
        return self.__class__(colrs, **clsargs)

    def has_codes(self):
        """ Returns True if one the frames in this FrameSet has an escape code
            in it.
        """
        return any(s.startswith('\x1b[') for s in self)


class FrameSet(FrameSetBase):
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

    def __repr__(self):
        """ Eval-friendly representation of this FrameSet. """
        return ''.join((
            '{clsname}',
            '({s.data!r}, name={s.name!r}, delay={s.delay!r})'
        )).format(clsname=self.__class__.__name__, s=self)

    def append(self, append_str):
        """ Append a string to every frame. """
        app = str(append_str)
        self.data = tuple(
            ''.join((str(s), app))
            for s in self.data
        )
        return self

    def as_colr(self, **kwargs):
        """ Wrap each frame in a Colr object, using `kwargs` for Colr().
            Keyword Arguments:
                fore  : Fore color for each frame.
                back  : Back color for each frame.
                style : Style for each frame.
        """
        return self._as_colr(('delay', ), **kwargs)

    def as_gradient(self, name=None, style=None, rgb_mode=False):
        """ Wrap each frame in a Colr object, using `Colr.gradient`.
            Arguments:
                name  : Starting color name. One of `Colr.gradient_names`.
        """
        return self._as_gradient(
            ('delay', ),
            name=name,
            style=style,
            rgb_mode=rgb_mode,
        )

    def as_rainbow(self, offset=35, style=None, rgb_mode=False):
        """ Wrap each frame in a Colr object, using `Colr.rainbow`. """
        return self._as_rainbow(
            ('delay', ),
            offset=offset,
            style=style,
            rgb_mode=rgb_mode,
        )

    @classmethod
    def from_barset(
            cls, barset, name=None, delay=None,
            use_wrapper=True, wrapper=None):
        """ Copy a BarSet's frames to create a new FrameSet.

            Arguments:
                barset      : An existing BarSet object to copy frames from.
                name        : A name for the new FrameSet.
                delay       : Delay for the animation.
                use_wrapper : Whether to use the old barset's wrapper in the
                              frames.
                wrapper     : A new wrapper pair to use for each frame.
                              This overrides the `use_wrapper` option.
        """
        if wrapper:
            data = tuple(barset.wrap_str(s, wrapper=wrapper) for s in barset)
        elif use_wrapper:
            data = tuple(barset.wrap_str(s) for s in barset)
        else:
            data = barset.data
        return cls(
            data,
            name=name,
            delay=delay
        )

    def prepend(self, prepend_str):
        """ Prepend a string to every frame. """
        prep = str(prepend_str)
        self.data = tuple(
            ''.join((prep, str(s)))
            for s in self.data
        )
        return self


class BarSet(FrameSet):
    """ A single progress bar frame list, with helper methods for
        colorizing each frame. A BarSet actually behaves like a `tuple`.
        It is immutable, hashable, and comparable.
    """
    # The beginning and end of a progress bar, never animated/changed.
    default_wrapper = ('[', ']')
    # Default width for generated progress bars.
    default_width = 25
    # Default fill character for "empty" space when generating progress bars.
    default_fill_char = ' '

    def __init__(self, iterable, name=None, wrapper=None):
        super().__init__(iterable, name=name)
        self.wrapper = wrapper or self.default_wrapper
        if len(self.wrapper) == 1:
            self.wrapper = (self.wrapper[0], '')

    def __repr__(self):
        """ Eval-friendly representation of this FrameSet. """
        return ''.join((
            '{clsname}',
            '({s.data!r}, name={s.name!r}, wrapper={s.wrapper!r})'
        )).format(clsname=self.__class__.__name__, s=self)

    def as_colr(self, **kwargs):
        """ Wrap each frame in a Colr object, using `kwargs` for Colr().

            Keyword Arguments:
                fore    : Fore color for each frame.
                back    : Back color for each frame.
                style   : Style for each frame.
        """
        return self._as_colr(('wrapper', ), **kwargs)

    def as_gradient(self, name=None, style=None, rgb_mode=False):
        """ Wrap each frame in a Colr object, using `Colr.gradient`.
            Arguments:
                name  : Starting color name. One of `Colr.gradient_names`.
        """
        return self._as_gradient(
            ('wrapper', ),
            name=name,
            style=style,
            rgb_mode=rgb_mode,
        )

    def as_percent(self, percent):
        """ Return a string representing a percentage of this progress bar.
            BarSet('1234567890', wrapper=('[, ']')).as_percent(50)
            >>> '[12345     ]'
        """
        if not self:
            return self.wrap_str()

        length = len(self)
        # Using mod 100, to provide some kind of "auto reset". 0 is 0 though.
        percentmod = (int(percent) % 100) or min(percent, 100)
        index = int((length / 100) * percentmod)
        try:
            barstr = str(self[index])
        except IndexError:
            barstr = self[-1]

        return self.wrap_str(barstr)

    def as_rainbow(self, offset=35, style=None, rgb_mode=False):
        """ Wrap each frame in a Colr object, using `Colr.rainbow`. """
        return self._as_rainbow(
            ('wrapper', ),
            offset=offset,
            style=style,
            rgb_mode=rgb_mode,
        )

    @classmethod
    def from_char(
            cls, char, name=None, width=None, fill_char=None,
            bounce=False, reverse=False, back_char=None, wrapper=None):
        """ Create progress bar frames from a "moving" character.
            The frames simulate movement of the character, from left to
            right through empty space (`fill_char`).

            Arguments:
                char           : Character to move across the bar.
                name           : Name for the new BarSet.
                width          : Width of the progress bar.
                                 Default: 25
                fill_char      : Character to fill empty space.
                                 Default: ' ' (space)
                bounce         : Whether the frames should simulate a bounce
                                 from one side to another.
                                 Default: False
                reverse        : Whether the character should start on the
                                 right.
                                 Default: False
                back_char  : Character to use when "bouncing" backward.
                                 Default: `char`
        """
        return cls(
            cls._generate_move(
                char,
                width=width or cls.default_width,
                fill_char=str(fill_char or cls.default_fill_char),
                bounce=bounce,
                reverse=reverse,
                back_char=back_char,
            ),
            name=name,
            wrapper=wrapper or cls.default_wrapper,
        )

    @classmethod
    def from_str(cls, s, name=None, fill_char=None, wrapper=None):
        """ Create progress bar frames from a single string.
            The frames simulate growth, from an empty string to the final
            string (`s`).

            Arguments:
                s          : Final string for a complete progress bar.
                name       : Name for the new BarSet.
                fill_char  : Character to fill empty space.
                             Default: ' ' (space)
                wrapper    : Wrapping characters for the new bar set.
                             Default: cls.default_wrapper

        """
        fill_char = fill_char or cls.default_fill_char
        maxlen = len(s)
        frames = []
        for pos in range(1, maxlen):
            framestr = s[:pos]
            # Not using ljust, because fill_char may be a str, not a char.
            frames.append(
                ''.join((
                    framestr,
                    fill_char * (maxlen - len(framestr))
                ))
            )
        frames.append(s)
        return cls(
            frames,
            name=name,
            wrapper=wrapper,
        )

    @classmethod
    def _generate_move(
            cls, char, width=None, fill_char=None,
            bounce=False, reverse=True, back_char=None):
        """ Yields strings that simulate movement of a character from left
            to right. For use with `BarSet.from_char`.

            Arguments:
                char          : Character to move across the progress bar.
                width         : Width for the progress bar.
                                Default: cls.default_width
                fill_char     : String for empty space.
                                Default: cls.default_fill_char
                bounce        : Whether to move the character in both
                                directions.
                reverse       : Whether to start on the right side.
                back_char  : Character to use for the bounce's backward
                                movement.
                                Default: `char`
        """
        width = width or cls.default_width
        char = str(char)
        filler = str(fill_char or cls.default_fill_char) * (width - len(char))

        rangeargs = RangeMoveArgs(
            (0, width, 1),
            (width, 0, -1),
        )
        if reverse:
            # Reverse the arguments for range to start from the right.
            # Not using swap, because the stopping point is different.
            rangeargs = RangeMoveArgs(
                (width, -1, -1),
                (0, width - 1, 1),
            )

        yield from (
            ''.join((filler[:i], char, filler[i:]))
            for i in range(*rangeargs.forward)
        )

        if bounce:
            bouncechar = char if back_char is None else back_char
            yield from (
                ''.join((filler[:i], str(bouncechar), filler[i:]))
                for i in range(*rangeargs.backward)
            )

    def with_wrapper(self, wrapper=None, name=None):
        """ Copy this BarSet, and return a new BarSet with the specified
            name and wrapper.
            If no name is given, `{self.name}_custom_wrapper` is used.
            If no wrapper is given, the new BarSet will have no wrapper.
        """
        name = name or '{}_custom_wrapper'.format(self.name)
        return self.__class__(self.data, name=name, wrapper=wrapper)

    def wrap_str(self, s=None, wrapper=None):
        """ Wrap a string in self.wrapper, with some extra handling for
            empty/None strings.
            If `wrapper` is set, use it instead.
        """
        wrapper = wrapper or (self.wrapper or ('', ''))
        return str('' if s is None else s).join(wrapper)


class Bars(object):
    """ A collection of bars that can be used with ProgressBar. """

    @classmethod
    def get_by_name(cls, name):
        """ Return a BarSet in this class by name. """
        return cls_get_by_name(cls, name)

    @classmethod
    def names(cls, registered=True):
        """ Return a list of names for all BarSet attributes in this class.
        """
        return cls_names(cls, BarSet, registered=registered)

    @classmethod
    def register(cls, barset, name=None):
        """ Register a new BarSet as a member/attribute of this class.
            Returns the new BarSet.
            Arguments:
                barset    : An existing BarSet, or an iterable of strings.
                name      : New name for the BarSet, also used as the
                            classes attribute name.
                            If the `barset` object has not `name` attribute,
                            this argument is required. It must not be empty
                            when given.
        """
        return cls_register(cls, barset, BarSet, ('wrapper', ), name=name)

    @classmethod
    def sets(cls, registered=True):
        """ Return a list of all BarSet attributes in this class. """
        return cls_sets(cls, BarSet, registered=registered)

    arrows = BarSet.from_char(
        '⮊',
        bounce=True,
        back_char='⮈',
        name='arrows',
        wrapper=('[', '] '),
    )
    blocks = BarSet.from_str('█' * BarSet.default_width, name='blocks')
    bounce = BarSet.from_char('●', bounce=True, name='bounce')
    bounce_big = BarSet.from_char('⬤ ', bounce=True, name='bounce_big')
    # This bar actually has 101 frames, but as_percent(1) will show 1 percent.
    # and as_percent(100) will show 100 percent.
    numbers = BarSet(
        ('%{:>3}'.format(x) for x in range(0, 101)),
        name='numbers',
    )


class Frames(object):
    """ A collection of frames/spinners that can be used with
        AnimatedProgress.
        """

    @classmethod
    def get_by_name(cls, name):
        """ Return a FrameSet in this class by name. """
        return cls_get_by_name(cls, name)

    @classmethod
    def names(cls, registered=True):
        """ Return a list of names for all FrameSet attributes in this class.
        """
        return cls_names(cls, FrameSet, registered=registered)

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
        return cls_register(cls, frameset, FrameSet, ('delay', ), name=name)

    @classmethod
    def sets(cls, registered=True):
        """ Return a list of all FrameSet attributes in this class. """
        return cls_sets(cls, FrameSet, registered=registered)

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
    arrows_bar = FrameSet.from_barset(
        Bars.arrows,
        name='arrows_bar',
        delay=0.1,
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


def _build_color_variants(cls):
    """ Build colorized variants of all frames and return a list of
        all frame object names.
    """
    # Get the basic frame types first.
    frametypes = cls.sets(registered=False)

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
            cls.register(
                framesobj.as_colr(fore=colorname),
                name=framename,
            )


def _build_gradient_variants(cls):
    # Get the basic frame types first.
    frametypes = cls.sets(registered=False)
    for gradname in C.gradient_names:
        if gradname in ('white', ):
            # This gradient name does not work as advertised.
            continue
        for framesobj in frametypes:
            framename = '{}_gradient_{}'.format(framesobj.name, gradname)
            cls.register(
                framesobj.as_gradient(name=gradname),
                name=framename
            )
            framename = '{}_gradient_{}_rgb'.format(
                framesobj.name,
                gradname,
            )
            cls.register(
                framesobj.as_gradient(name=gradname, rgb_mode=True),
                name=framename
            )


def _build_rainbow_variants(cls):
    # Get the basic frame types first.
    frametypes = cls.sets(registered=False)

    for framesobj in frametypes:
        framename = '{}_rainbow'.format(framesobj.name)
        cls.register(framesobj.as_rainbow(), name=framename)
        framename = '{}_rainbow_rgb'.format(framesobj.name)
        cls.register(framesobj.as_rainbow(rgb_mode=True), name=framename)
    return None


# Not building gradient/rainbow variants right now. It takes too long.
_build_color_variants(Frames)
_build_color_variants(Bars)

# Default frames to use when none are specified.
Frames.default = Frames.dots_blue  # type: ignore
Bars.default = Bars.blocks_blue  # type: ignore
