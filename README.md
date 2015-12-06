Colr
====

A python module for using terminal colors in linux. It contains a simple
`color` function that accepts style and color names, and outputs a string
with escape codes, but also has all colors and styles as chainable methods
on the `Colr` object.

_______________________________________________________________________________

Examples:
---------

###Simple:

```python
from colr import color
print(color('Hello world.', fore='red', style='bright'))
```

###Chainable:
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

Examples (256 Colors):
----------------------

###Simple:

```python
from colr import color
# Invalid color names/numbers raise a ValueError.
print(color('Hello world', fore=125, back=80))
```

###Chainable:

```python
from colr import Colr as C
# Foreground colors start with 'f_'
# Background colors start with 'b_'
print(C().f_125().b_80('Hello World'))
```

_______________________________________________________________________________


Other methods:
--------------

The `Colr` object has several helper methods.
The `color()` method returns a `str`, but the rest return a `Colr` instance
so they can be chained. A chainable version of `color()` does exist (`chainable()`),
but it's not really needed outside of the `colr` module itself.

###Colr.center

Like `str.center`, except it ignores escape codes.

```python
Colr('Hello', fore='green').center(40)
```

###Colr.format

Like `str.format`, except it operates on `Colr.data`.

```python
Colr('Hello').blue(' {}').red(' {}').format('my', 'friend').center(40)
```

###Colr.gradient

Builds gradient text, with optional start code and step.
The method for building gradients may change in the future.

```python
(Colr('Wow man, ').gradient(start=232)
.gradient('what a neat feature that is.', start=49))
```

###Colr.join

Joins `Colr` instances or other types together.
If anything except a `Colr` is passed, `str(thing)` is called before
joining. `join` accepts multiple args, and any list-like arguments are
flattened at least once (simulating str.join args).

```python
Colr('alert', 'red').join('[', ']').yellow(' This is neat.')
```

###Colr.ljust

Like `str.ljust`, except it ignores escape codes.

```python
Colr('Hello', 'blue').ljust(40)
```

###Colr.rjust

Like `str.rjust`, except it ignores escape codes.

```python
Colr('Hello', 'blue').rjust(40)
```

###Colr.str

The same as calling `str()` on a `Colr` instance.
```python
Colr('test', 'blue').str() == str(Colr('test', 'blue'))
```

###Colr.\_\_add\_\_

Strings can be added to a `Colr` and the other way around.
Both return a `Colr` instance.

```python
Colr('test', 'blue') + 'this' == Colr('').join(Colr('test', 'blue'), 'this')
'test' + Colr('this', 'blue') == Colr('').join('test', Colr(' this', 'blue'))

```

###Colr.\_\_call\_\_

`Colr` instances are callable themselves.
Calling a `Colr` will append text to it, with the same arguments as `color()`.

```python
Colr('One', 'blue')(' formatted', 'red')(' string.', 'blue')
```

###Colr.\_\_eq\_\_, \_\_ne\_\_

`Colr` instances can also be compared with other `Colr` instances.
They are equal if `self.data` is equal to `other.data`.

```python
Colr('test', 'blue') == Colr('test', 'blue')
Colr('test', 'blue') != Colr('test', 'red')
```

###Colr.\_\_lt\_\_, \_\_gt\_\_, \_\_le\_\_, \_\_ge\_\_
Escape codes are stripped for less-than/greater-than comparisons.

```python
Colr('test', 'blue') < Colr('testing', 'blue')
```

###Colr.\_\_getitem\_\_

Escape codes are stripped when subscripting/indexing.

```python
Colr('test', 'blue')[2] == Colr('s')
Colr('test', 'blue')[1:3] == Colr('es')
```

###Colr.\_\_mul\_\_

`Colr` instances can be multiplied by an `int` to build color strings.
These are all equal:

```python
Colr('*', 'blue') * 2
Colr('*', 'blue') + Colr('*', 'blue')
Colr('').join(Colr('*', 'blue'), Colr('*', 'blue'))
```


_______________________________________________________________________________

Notes:
------

Windows is not supported yet, but I'm working on it. In the past, I used
a simple `color()` function because I'm not fond of the string concatenation
style that other libraries use. The 'clor' javascript library uses method
chaining because that style suits javascript, but I wanted to make it available
to Python also, at least as an option.

The reset code is appended to all text unless the text is empty.
This makes it possible to build background colors and styles, but
also have separate styles for separate pieces of text.

This library may be a little too flexible, and that may change:

```python
from colr import Colr as C
warnmsg = lambda s: C('warning', 'red').join('[', ']')(' ').green(s)
print(warnmsg('The roof is on fire again.'))
```

![The possibilities are endless.](https://welbornprod.com/static/media/img/colr-warning.png)


