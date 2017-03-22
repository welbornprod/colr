# colr.progress

This module contains functions and classes to work with progress bars/spinners
for the terminal.

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
p.stop()
```

#### Context Manager
```python
from colr import StaticProgress

with StaticProgress('Loading the thing.', show_time=True) as p:
    # The progress printer has started already.
    long_running_function()
    # The progress printer is stopped when exiting the context manager.
```
## colr.AnimatedProgress

This is like the [`StaticProgress`](#colr.StaticProgress), but it can be
given a set of "frames" to cycle through while printing, to create animations.
Each frame is a character or string to print, and advances/loops after each
delay. There are some predefined [`FrameSet`](#colr.FrameSet)s in the
[`Frames`](#colr.Frames) class.

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
    # Progress is stopped whe the context manager exits.
```

## colr.FrameSet

A `FrameSet` is basically a tuple of strings, with a name and an optional
suggested `delay` attribute.
The [`AnimatedProgress`](#colr.AnimatedProgress) class will honor a `FrameSet`s
`delay`, as long as the user doesn't override it when intializing the
[`AnimatedProgress`](#colr.AnimatedProgress).

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

## colr.Frames

The `Frames` class is a collection of [`FrameSet`s](#colr.FrameSet) included with
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

Also, as noted in the [`FrameSet`](#colr.FrameSet) documentation, you can
always make your own [colorized variants](#FrameSet.as_colr).

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

##### Gradient

* `<name>_gradient_blue`
* `<name>_gradient_cyan`
* `<name>_gradient_green`
* `<name>_gradient_lightred`
* `<name>_gradient_magenta`
* `<name>_gradient_orange`
* `<name>_gradient_red`
* `<name>_gradient_yellow`

##### Rainbow

* `<name>_rainbow`
