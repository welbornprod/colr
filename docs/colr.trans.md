# colr.trans

This module holds all of the functions needed to translate from one color
type to another.

## Translation Classes/Functions:

### ColorCode

A class that automatically converts hex, rgb, or terminal codes to the other
types. They can be accessed through the attributes `code`, `hexval`, and `rgb`.

```python
from colr import ColorCode
print(ColorCode(30))
# Terminal:  30, Hex: 008787, RGB:   0, 135, 135

print(ColorCode('de00fa'))
# Terminal: 165, Hex: de00fa, RGB: 222,   0, 250

print(ColorCode((75, 50, 178)))
# Terminal:  61, Hex: 4b32b2, RGB:  75,  50, 178
```

Printing `ColorCode(45).example()` will show the actual color in the terminal.

### hex2rgb

Converts a hex color (`#000000`) to RGB `(0, 0, 0)`.

### hex2term

Converts a hex color to terminal code number.

```python
from colr import color, hex2term
print(color('Testing', hex2term('#FF0000')))
```
### hex2termhex

Converts a hex color to it's closest terminal color in hex.

```python
from colr import hex2termhex
hex2termhex('005500') == '005f00'
```


### is_code

Returns `True` if a string appears to be a single basic escape code.

### is_ext_code

Returns `True` if string appears to be a single extended 256 escape code.

### is_rgb_code

Returns `True` if string appears to be a single rgb escape code.

### rgb2hex

Converts an RGB value `(0, 0, 0)` to it's hex value (`000000`).

### rgb2term

Converts an RGB value to terminal code number.

```python
from colr import color, rgb2term
print(color('Testing', rgb2term(0, 255, 0)))
```

### rgb2termhex

Converts an RGB value to it's closest terminal color in hex.

```python
from colr import rgb2termhex
rgb2termhex(0, 55, 0) == '005f00'
```

### term2hex

Converts a terminal code number to it's hex value.

```python
from colr import term2hex
term2hex(30) == '008787'
```

### term2rgb

Converts a terminal code number to it's RGB value.

```python
from colr import term2rgb
term2rgb(30) == (0, 135, 135)
```
