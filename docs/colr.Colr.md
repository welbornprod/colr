# colr.Colr

The `Colr` object is for building colorized strings.

## Colr Methods:

The `Colr` object has several helper methods.
The `color()` method returns a `str`, but the rest return a `Colr` instance
so they can be chained.

A chainable version of `color()` does exist (`chained()`), but it's not really
needed outside of the `colr` module itself. It could be used to append strings
to a `Colr`, but `Colr.join()` is more flexible.

### Colr.center

Like `str.center`, except it ignores escape codes.

```python
Colr('Hello', fore='green').center(40)

# This also ignores escape codes:
'{:^40}'.format(Colr('Hello', fore='green'))
```

### Colr.format

Like `str.format`, except it operates on `Colr.data`.

```python
Colr('Hello').blue(' {}').red(' {}').format('my', 'friend').center(40)
```

### Colr.gradient

Like `rainbow()`, except a known name can be passed to choose the color
(same names as the basic fore colors).

```python
(Colr('Wow man, ').gradient(name='red')
.gradient('what a neat feature that is.', name='blue'))
```

### Colr.gradient_black

Builds a black and white gradient. The default starting color is black, but
white will be used if `reverse=True` is passed. Like the other `gradient/rainbow`
functions, if you pass a `fore` color, the background will be gradient.

```python
(C('Why does it have to be black or white?').gradient_black(step=3)
.gradient_black(' ' * 10, fore='reset', reverse=True))
```

### Colr.gradient_rgb

Uses true color (rgb codes) to build a gradient from one rgb value to another.
Just like the other `gradient/rainbow` methods, passing a `fore` color means
the background is gradient.

When using `linemode=True` (where each line is a separate gradient), you can
"shift" the gradient left or right for each line using `movefactor=N`. `N` can
be positive or negative to change the direction of the shift, or `None` / `0`
to not shift at all (the default is `None`).

```python
C('This is pretty fancy.').gradient_rgb((0, 0, 255), (255, 0, 0), step=5)
```

### Colr.hex

This will set the fore color using hex values. It accepts
the same args as the other chained methods, except the hex value should be the
first argument. With `rgb_mode=True`, the value is converted straight to
a true color (rgb) code.

```python
# This will use true color (rgb) codes, equivalent to Colr.rgb(255, 55, 55).
Colr().hex('ff3737', rgb_mode=True).bgwhite('Test')
# Without `rgb_mode`, it finds the nearset extended terminal color.
# This is equivalent to extended code 203, or rgb(255, 95, 95).
Colr().hex('ff3737').bgwhite('Test')
```

### Colr.join

Joins `Colr` instances or other types together.
If anything except a `Colr` is passed, `str(thing)` is called before
joining. `join` accepts multiple args, and any list-like arguments are
flattened at least once (simulating str.join args).

```python
Colr('alert', 'red').join('[', ']').yellow(' This is neat.')
```

### Colr.ljust

Like `str.ljust`, except it ignores escape codes.

```python
Colr('Hello', 'blue').ljust(40)

# This also ignores escape codes:
'{:<40}'.format(Colr('Hello', 'blue'))
```

### Colr.lstrip

Like `str.lstrip()`, except it returns a `Colr`.

```python
Colr('    Hello').lstrip() == Colr('Hello')
Colr('    Hello', 'red',  style='bright').lstrip() == Colr('Hello', 'red', style='bright')
```

### Colr.rainbow

Beautiful rainbow gradients in the same style as [lolcat](https://github.com/busyloop/lolcat).
This method is incapable of doing black and white gradients. That's what
`gradient_black()` is for.

```python
Colr('This is really pretty.').rainbow(freq=.5)
```

If your terminal supports it, you can use true color (rgb codes) by using
`rgb_mode=True`:

```python
Colr('This is even prettier.').rainbow(rgb_mode=True)
```

### Colr.rgb

This will set the fore color using true color (rgb codes). It accepts
the same args as the other chained methods, except the `r`, `g`, and `b`
values should be the first arguments.

```python
Colr().rgb(255, 55, 55).bgwhite('Test')
```

It has a background version called `b_rgb`.

```python
Colr().b_rgb(255, 255, 255).rgb(255, 55, 55, 'Test')
```

### Colr.rjust

Like `str.rjust`, except it ignores escape codes.

```python
Colr('Hello', 'blue').rjust(40)

# This also ignores escape codes:
'{:>40}'.format(Colr('Hello', 'blue'))
```

### Colr.rstrip

Like `str.rstrip()`, except it returns a `Colr`.

```python
Colr('Hello    ').rstrip() == Colr('Hello')
Colr('Hello    ', 'red',  style='bright').rstrip() == Colr('Hello', 'red', style='bright')
```

### Colr.str

The same as calling `str()` on a `Colr` instance.
```python
Colr('test', 'blue').str() == str(Colr('test', 'blue'))
```

### Colr.strip

Like `str.strip()`, except it returns a `Colr`.

```python
Colr('    Hello    ').strip() == Colr('Hello')
Colr('    Hello    ', 'red',  style='bright').strip() == Colr('Hello', 'red', style='bright')
```

### Colr.stripped

The same as calling `strip_codes(Colr().data)`.
```python
data = 'Testing this.'
colored = Colr(data, fore='red')
data == colored.stripped()
```

### Colr.\_\_add\_\_

Strings can be added to a `Colr` and the other way around.
Both return a `Colr` instance.

```python
Colr('test', 'blue') + 'this' == Colr('').join(Colr('test', 'blue'), 'this')
'test' + Colr('this', 'blue') == Colr('').join('test', Colr(' this', 'blue'))

```

### Colr.\_\_bytes\_\_

Calling `bytes()` on a `Colr` is like calling `Colr().data.encode()`. For
custom encodings, you can use `str(Colr()).encode(my_encoding)`.

```python
bytes(Colr('test')) = 'test'.encode()
```

### Colr.\_\_call\_\_

`Colr` instances are callable themselves.
Calling a `Colr` will append text to it, with the same arguments as `color()`.

```python
Colr('One', 'blue')(' formatted', 'red')(' string.', 'blue')
```

### Colr.\_\_eq\_\_, \_\_ne\_\_

`Colr` instances can also be compared with other `Colr` instances.
They are equal if `self.data` is equal to `other.data`.

```python
Colr('test', 'blue') == Colr('test', 'blue')
Colr('test', 'blue') != Colr('test', 'red')
```

### Colr.\_\_lt\_\_, \_\_gt\_\_, \_\_le\_\_, \_\_ge\_\_
Escape codes are stripped for less-than/greater-than comparisons.

```python
Colr('test', 'blue') < Colr('testing', 'blue')
```

### Colr.\_\_getitem\_\_

Escape codes are stripped when subscripting/indexing, but `Colr` tries to
be smart and grab any color codes *before* the index, and append a reset
code if necessary *after*.

```python
Colr('test', 'blue')[1:3] == Colr('es', 'blue')

# A complicated example:
c = Colr('test', 'red').blue('this').rgb(25, 25, 25, 'thing')
# Index 5 points to 'h' in 'testthisthing', `c` without escape codes.
c[5] == Colr(fore='red').blue('h')
# Slices use the last escape code used before the starting index.
# All codes are kept, including reset/closing codes.
c[:] == c
c[8:] == Colr(fore='red').blue().rgb(25, 25, 25, 'thing')
```

### Colr.\_\_hash\_\_

Hashing a `Colr` just means hashing `Colr().data`, but this works:
```python
hash(Colr('test', 'blue')) == hash(Colr('test', 'blue'))
```

### Colr.\_\_iter\_\_

Iterating over a `Colr` just means iterating over `Colr().data`:
```python
# Generator, equivalent to: str(Colr('test', 'blue'))
s = ''.join(c for c in Colr('test', 'blue'))

# For-loop, equivalent to: for c in str(Colr('test', 'blue'))
for c in Colr('test', 'blue'):
    print(c, end='')
```

### Colr.\_\_mul\_\_

`Colr` instances can be multiplied by an `int` to build color strings.
These are all equal:

```python
Colr('*', 'blue') * 2
Colr('*', 'blue') + Colr('*', 'blue')
Colr('').join(Colr('*', 'blue'), Colr('*', 'blue'))
```
