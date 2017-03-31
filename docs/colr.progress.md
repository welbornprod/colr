# colr.progress

This module contains functions and classes to work with progress bars/spinners
for the terminal.

Section | Description
--- | ---
[AnimatedProgress](#colranimatedprogress) | Usage and examples for the `AnimatedProgress` object.
[Bars](#colrbars) | A collection of `BarSets` included with `Colr` by default.
[BarSet](#colrbarset) | Usage and examples for the `BarSet` object, a list of animation frames for the `ProgressBar` object.
[FrameSet](#colrframeset) | Usage and examples for the `FrameSet` object, a list of animation frames for the `AnimatedProgress` object.
[Frames](#colrframes) | A collection of `FrameSets` included with `Colr` by default.
[StaticProgress](#colrstaticprogress) | Usage and examples for the `StaticProgress` object.

## colr.StaticProgress

`StaticProgress(text=None, delay=None, fmt=None, show_time=False, char_delay=None, file=None)`

A `StaticProgress` simply prints text, with an optional "elapsed time", to
the same line until stopped. The text can be updated by setting the `text`
attribute.

### Example

#### Basic Usage
```python
from colr import StaticProgress

p = StaticProgress('Loading the thing.', show_time=True)
p.start()
long_running_function()
p.text = 'Loading another thing.'
another_function()
p.stop()
```

#### Context Manager
```python
from colr import StaticProgress

with StaticProgress('Loading the thing.', show_time=True) as p:
    # The progress printer has started already.
    long_running_function()
    p.text = 'Still loading...'
    another_function()
    # The progress printer is stopped when exiting the context manager.
```
## colr.AnimatedProgress

This is like the [`StaticProgress`](#colrstaticprogress), but it can be
given a set of "frames" to cycle through while printing, to create animations.
Each frame is a character or string to print, and advances/loops after each
delay. There are some predefined [`FrameSet`](#colrframeset)s in the
[`Frames`](#colrframes) class.

### Example

#### Basic Usage
```python
from colr import AnimatedProgress, Frames

p = AnimatedProgress(
    'Loading',
    frames=Frames.dots_orbit_blue,
    show_time=True,
)
p.start()
long_running_function()
p.text = 'Still loading...'
another_function()
p.stop()
```

#### Context Manager
```python
from colr import AnimatedProgress, Frames

p = AnimatedProgress(
    'Loading',
    frames=Frames.dots_orbit_blue,
    show_time=True,
)
with p:
    # Progress has already started.
    long_running_function()
    p.text = 'Still loading...'
    another_function()    # Progress is stopped whe the context manager exits.
```

## colr.ProgressBar

This is like the [`AnimatedProgress`](#colranimatedprogress), but deals with
percentage-based progress updates. It uses a [`BarSet`](#colrbarset) object
to draw custom progress bars to the screen and receives state updates from
the user.
There are some predefined [`BarSet`](#colrbarset) objects in the
[`Bars`](#colrbars) class.

### Example

#### Basic Usage
```python
from colr import ProgressBar, Bars
from time import sleep
p = ProgressBar(
    'Loading',
    frames=Bars.blocks_blue,
    show_time=True,
)
p.start()
for x in range(0, 100, 10):
    # Pretend we are doing something.
    p.update(percent=x)
    if x > 50:
        p.message = 'Halfway done...'
    sleep(0.5)
p.stop()
```

#### Context Manager
```python
from colr import ProgressBar, Bars
from time import sleep
p = ProgressBar(
    'Loading',
    frames=Bars.blocks_blue,
    show_time=True,
)

with p:
    # Progress has already started.
    for x in range(0, 100, 10):
        # Pretend we are doing something.
        p.update(percent=x, text='Still loading')
        # You can also set the message without updating percentage.
        p.message = 'Still loading the thing.'
        sleep(0.5)
    # Progress is stopped whe the context manager exits.
```

## colr.Bars

The `Bars` class is a collection of [`BarSet`](#colrbarset) objects included with
`colr` by default. It includes the basic plain animations, and many colorized
versions of those animations (generated with `BarSet.as_colr`,
`BarSet.as_gradient`, and `BarSet.as_rainbow`).

### Methods

#### Bars.get_by_name
`Bars.get_by_name(name)`

Retrieve a known `BarSet` from `Bars` by name. This will only recognize
`BarSet`s that have been previously registered with `Bars.register()`

#### Bars.names
`Bars.names()`

Returns a list of all `BarSet` names that have been registered as attributes
of the `Bars` class.

#### Bars.register
`Bars.register(bars, name=None)`

Registers a `BarSet` as a member of the `Bars` class. This is not required
to use a `BarSet`. It is only needed if you want the `BarSet` to be used
with `Bars.get_by_name()` or `Bars.names()`.

The `bars` argument can be an existing `BarSet`, or an iterable of strings
to build a `BarSet` with.

### Basic BarSets

These are some basic `BarSet`s that are included with `colr` by default:

* `arrows`
* `blocks`
* `bounce`
* `bounce_big`
* `numbers`

The `Bars` class also has many [colorized variants](#colorized-variants), as
noted in the [`Frames`](#basic-framesets) documentation.

## colr.BarSet

A `BarSet` is a tuple of strings, with a name and an optional "wrapper"
string. Each "frame" of the `BarSet` is wrapped in the "wrapper" when
`BarSet.as_percentage()` is called. The `BarSet` should include a starting
frame, and the ending frame, and preferably at least `8` frames in between
those. `BarSet.as_percentage()` is used to draw the frame needed when a
`ProgressBar`s state is updated.

### Example

```python
from colr import ProgressBar, BarSet
# For this example only.
from time import sleep
bset = BarSet(
    ('-   ', '--  ', '--- ', '----'),
    name='dashes',
    wrapper=('[', ']')
)
# This same barset could be drawn with:
bset = BarSet.from_str(
    '----',
    name='dashes',
    fill_char=' ', # This is the default fill character.
    wrapper='[', ']',
)

p = ProgressBar('Loading', bars=bset)
with p:
    for x in range(0, 100, 10):
        p.update(x)
        # Simulate some work.
        sleep(0.5)
```

### Methods

#### BarSet.as_colr
`BarSet.as_colr(fore=None, back=None. style=None)`

Returns a new `BarSet`, with each frame wrapped in a `Colr` object.
All `kwargs` are forwarded to `Colr`.

#### BarSet.as_gradient
`BarSet.as_gradient(name=None, **kwargs)`

Returns a new `BarSet`, with each frame wrapped in one iteration of
`Colr.gradient`. The `name` argument is the starting color name, one of
`Colr.gradient_names`.

#### BarSet.as_rainbow
`BarSet.as_rainbow(offset=35, style=None)`

Returns a new `BarSet`, with each frame wrapped in one iteration of
`Colr.rainbow`. The `offset` arg is the starting offset for `Colr.rainbow`,
and the `style` arg is forwarded.

#### BarSet.as_percent
`BarSet.as_percent(percent)`

Returns a single frame string representing a percentage of progress completed.
The frame is wrapped in `self.wrapper` and returned.

#### BarSet.from_char
`from_char(
    char, name=None, width=None, fill_char=None,
    bounce=False, reverse=False, back_char=None, wrapper=None
)`

Generate a "moving" progress bar animation from a character (or string).
The character will move from left to right (unless `reverse` is used), and
can be set to move back the other direction if `bounce` is used. If
`back_char` is set, the character will be used on it's way "back".

The character moves through the `fill_char`, forming a string of `length`
characters (plus the `wrapper` length when `as_percentage()` is called).

#### BarSet.from_str
`from_str(s, name=None, fill_char=None, wrapper=None)`

Generate a "growing" progress bar animation from a string. The progress bar
starts as empty space (defined by `fill_char`), and "grows" to fill the space
for `len(s)` frames, and stops when all of the string has been used.


## colr.FrameSet

A `FrameSet` is basically a tuple of strings, with a name and an optional
suggested `delay` attribute.
The [`AnimatedProgress`](#colranimatedprogress) class will honor a `FrameSet`s
`delay`, as long as the user doesn't override it when intializing the
[`AnimatedProgress`](#colranimatedprogress).

### Example

```python
from colr import AnimatedProgress, FrameSet
fset = FrameSet('-\|/', name='backslash_spinner', delay=0.5)
p = AnimatedProgress('Spinning...', frames=fset)
```

### Methods

#### FrameSet.as_colr
`FrameSet.as_colr(fore=None, back=None. style=None)`

Returns a new `FrameSet`, with each frame wrapped in a `Colr` object.
All `kwargs` are forwarded to `Colr`.

#### FrameSet.as_gradient
`FrameSet.as_gradient(name=None, **kwargs)`

Returns a new `FrameSet`, with each frame wrapped in one iteration of
`Colr.gradient`. The `name` argument is the starting color name, one of
`Colr.gradient_names`.

#### FrameSet.as_rainbow
`FrameSet.as_rainbow(offset=35, style=None)`

Returns a new `FrameSet`, with each frame wrapped in one iteration of
`Colr.rainbow`. The `offset` arg is the starting offset for `Colr.rainbow`,
and the `style` arg is forwarded.

#### FrameSet.from_barset
`FrameSet.from_barset(barset, name=None, delay=None, use_wrapper=True, wrapper=None)`

Create a looping animation from an existing [`BarSet`](#colrbarset) animation.
The wrapper can be omitted if `use_wrapper` is `False`.

## colr.Frames

The `Frames` class is a collection of [`FrameSet`s](#colrframeset) included with
`colr` by default. It includes the basic plain animations, and many colorized
versions of those animations (generated with `FrameSet.as_colr`,
`FrameSet.as_gradient`, and `FrameSet.as_rainbow`).

### Methods

#### Frames.get_by_name
`Frames.get_by_name(name)`

Retrieve a known `FrameSet` from `Frames` by name. This will only recognize
`FrameSet`s that have been previously registered with `Frames.register()`

#### Frames.names
`Frames.names()`

Returns a list of all `FrameSet` names that have been registered as attributes
of the `Frames` class.

#### Frames.register
`Frames.register(frames, name=None)`

Registers a `FrameSet` as a member of the `Frames` class. This is not required
to use a `FrameSet`. It is only needed if you want the `FrameSet` to be used
with `Frames.get_by_name()` or `Frames.names()`.

The `frames` argument can be an existing `FrameSet`, or an iterable of strings
to build a `FrameSet` with.

### Basic FrameSets

These are some basic `FrameSet`s that are included with `colr` by default:

* `arc`
* `arrows`
* `bounce`
* `bouncing_ball`
* `dots`
* `dots_chase`
* `dots_orbit`
* `hamburger`

#### Colorized Variants

Each of these has a color, light-color, gradient, and rainbow variant. You
can access them by the names listed below, where `<name>` is the name of the
basic `FrameSet`.

Also, as noted in the [`FrameSet`](#colrframeset) documentation, you can
always make your own [colorized variants](#framesetas_colr).

##### Basic Colors

* `<name>_blue`
* `<name>_cyan`
* `<name>_green`
* `<name>_magenta`
* `<name>_red`
* `<name>_white`
* `<name>_yellow`

##### Light Colors

* `<name>_lightblue`
* `<name>_lightcyan`
* `<name>_lightgreen`
* `<name>_lightmagenta`
* `<name>_lightred`
* `<name>_lightwhite`
* `<name>_lightyellow`
