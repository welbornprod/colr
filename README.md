# Colr

A python module for using terminal colors. It contains a simple
`color` function that accepts style and color names, and outputs a string
with escape codes, but also has all colors and styles as chainable methods
on the `Colr` object.

_______________________________________________________________________________

## Dependencies:

### System

* **Python 3.5+** -
    This library uses `yield from` and the `typing` module.
    [Python 2 support is not planned.](#python-2)

### Modules

There are no dependencies required for importing this library, however:

* [Docopt](https://github.com/docopt/docopt) -
    Only required for the command line tools ([colr](#colr-tool) and [colr-run](#colr-run))
    and the [colr.docopt wrapper](#colrdocopt), not the library itself.

## Installation:

Colr is listed on [PyPi](https://pypi.python.org/pypi/Colr),
and can be installed using [pip](https://pip.pypa.io/en/stable/installing/):

```
pip install colr
```

Or you can clone the repo on [GitHub](https://github.com/welbornprod/colr)
and install it from the command line:

```
git clone https://github.com/welbornprod/colr.git
cd colr
python3 setup.py install
```

_______________________________________________________________________________


## Examples:

### Simple:

```python
from colr import color
print(color('Hello world.', fore='red', style='bright'))
```

### Chainable:
```python
from colr import Colr as C
print(
    C()
    .bright().red('Hello ')
    .normal().blue('World')
)

# Background colors start with 'bg', and AttributeError will be raised on
# invalid method names.
print(C('Hello ', fore='red').bgwhite().blue('World'))

```

## Examples (256 Colors):

### Simple:

```python
from colr import color
# Invalid color names/numbers raise a ValueError.
print(color('Hello world', fore=125, back=80))
```

### Chainable:

```python
from colr import Colr as C
# Foreground colors start with 'f_'
# Background colors start with 'b_'
print(C().f_125().b_80('Hello World'))
```

## Examples (True Color):

### Simple:

```python
from colr import color
print(color('Hello there.', fore=(255, 0, 0), back=(0, 0, 0)))
```

### Chainable:

```python
from colr import Colr as C
# Foreground colors are set with the `rgb()` method.
# Background colors are set with the `b_rgb()` method.
# Text for the chained methods should be chained after or during
# the call to the methods.
print(C().b_rgb(0, 0, 0).rgb(255, 0, 0, 'Hello there.'))
```

## Examples (Hex):

### Simple:

```python
from colr import color
# When not using the Colr.hex method, the closest matching extended code
# is used. For true color, just use:
#     fore=hex2rgb('ff0000')
# or
#     Colr.hex('ff0000', rgb_mode=True)
print(color('Hello there.', fore='ff0000', back='000'))
```

### Chainable:

```python
from colr import Colr as C
# Foreground colors are set with the `hex()` method.
# Background colors are set with the `b_hex()` method.
# Text for the chained methods should be chained after or during
# the call to the methods.
print(C().b_hex('#000').hex('ff0000', 'Hello there.'))

# With rgb_mode set, these are the same:
print(C().hex('ff0000', 'test', rgb_mode=True))
print(C().rgb(255, 0, 0, 'test'))
```

_______________________________________________________________________________


## Documentation:

Documentation for the `colr` API can be found in the GitHub repo
([github.com/welbornprod/colr](https://github.com/welbornprod/colr)):

Module/Object | Description
------------------------------------- | --------------------------------------
[colr.Colr](https://github.com/welbornprod/colr/blob/dev/docs/colr.Colr.md) | Methods for the `Colr` object, to colorize text.
[colr.Control](https://github.com/welbornprod/colr/blob/dev/docs/colr.controls.md) | Functions, classes, and methods for the `Control` object, to control the cursor/screen.
colr.ColrControl | `Colr` and `Control` merged into one class. See `colr.Colr` and `colr.Control`.
[colr.progress](https://github.com/welbornprod/colr/blob/dev/docs/colr.progress.md) | Progress updates, bars, or spinners.
[colr.trans](https://github.com/welbornprod/colr/blob/dev/docs/colr.trans.md) | Color code translation/detection.

_______________________________________________________________________________

## Colr Tool:

The `colr` package can be used as a command line tool. An entry point script
named `colr` is created when installed with pip. Otherwise it can be executed
using the `python -m colr` method.
```bash
colr --help
```

Basic usage involves passing text, or piping stdin data and setting the colors
by position or flag.

```bash
# These all do the same thing:
colr "Test" "red" "white" "bright"
colr "Test" -f "red" -b "white" -s "bright"
printf "Test" | colr -f "red" -b "white" -s "bright"
```

Using the positional arguments is faster for just setting fore colors, but
the flag method is needed for stdin data, or for picking just the background
color or style:

```bash
colr "Test" -s "bright"
```

Extended and True colors are supported:
```bash
colr "Test" 124 255
colr "Test" "255, 0, 0" "255, 255, 255"
# Use true color (rgb) escape codes to generate a gradient, and then
# center it in the terminal (0 means use terminal width).
colr "Test" -G "255,0,0" -G "0,0,255" -c 0
```

It will do fore, back, style, gradients, rainbows, justification,
and translation.
It can strip codes from text (as an argument or stdin), or explain the
codes found in the text.

[lolcat](https://github.com/busyloop/lolcat) emulation:
```bash
fortune | colr --rainbow
```

The colr tool does not read files, but it's not a problem:
```bash
cat myfile.txt | colr --gradient red
```

Also see [ccat](https://github.com/welbornprod/ccat).


## Colr-run:

A small command-runner is included, called `colr-run`. This
program will run another program, printing an animated message instead of the
normal output.

It is used to turn "noisy" commands into a nice single-line animation.

### Basic Example:

To run a program with the default settings, `--` is still required:
```bash
colr-run -- bash -c 'x=0; while ((x<1000000)); do let x+=1; done'
```

Any stderr output from the program will ruin the animation, which may be fine
if you are only looking for errors.

You can silence stderr output with `-e` if you don't need it:
```bash
colr-run -e -- some-long-running-command
```

The exit status of `colr-run` is the exit status of the command being
executed. For `colr-run` errors, the exit status is `1` for basic errors,
and `2` for cancelled commands.

## Colr.docopt:

Colr provides a wrapper for docopt that will automatically colorize usage
strings. If you provide it a script name it will add a little more color by
colorizing the script name too.
```python
from colr import docopt
argd = docopt(USAGE, script='mycommand')
```

_______________________________________________________________________________

## Contributing:

As always contributions are welcome here. If you think you can improve something,
or have a good idea for a feature, please file an
[issue](https://github.com/welbornprod/colr/issues/new) or a
[pull request](https://github.com/welbornprod/colr/compare).

_______________________________________________________________________________

## Notes:

### Reasons

In the past, I used a simple `color()` function because I'm not fond of the
string concatenation style that other libraries use. The 'clor' javascript
library uses method chaining because that style suits javascript, but I wanted
to make it available to Python also, at least as an option.

### Reset Codes

The reset code is appended only if some kind of text was given, and
colr/style args were used. The only values that are considered 'no text'
values are `None` and `''` (empty string). `str(val)` is called on all other
values, so `Colr(0, 'red')` and `Colr(False, 'blue')` will work, and the reset
code will be appended.

This makes it possible to build background colors and styles, but
also have separate styles for separate pieces of text.

### Python 2

I don't really have the desire to back-port this to Python 2.
It wouldn't need too many changes, but I like the Python 3 features
(`yield from`, `str/bytes`).

### Windows

Windows 10 finally has support for ANSI escape codes.
Colr can now be used on Windows 10+ by calling `SetConsoleMode`.
Older Windows versions are not supported and haven't been tested. If you are
using Colr for a tool that needs to support older Windows versions, you will
need to detect the current Windows version and call `colr.disable()` for those
that aren't supported. Otherwise you will have "junk" characters printed to
the screen.

### Misc.
This library may be a little too flexible:

```python
from colr import Colr as C
warnmsg = lambda s: C('warning', 'red').join('[', ']')(' ').green(s)
print(warnmsg('The roof is on fire again.'))
```

![The possibilities are endless.](https://welbornprod.com/static/media/img/colr-warning.png)
