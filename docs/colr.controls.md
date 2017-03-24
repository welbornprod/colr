# colr.controls

This module contains functions and classes to work with escape codes that
control the cursor or screen.
You can use the file-writing [functions](#functions), or
for `Colr`-like, chained behavior you can use the [`Control`](#colrcontrol)
object.

## Functions

Module-level functions will write the appropriate escape code to their `file`
argument (Default: `sys.stdout`).

If you would like to retrieve the escape code strings themselves, then use a
[`Control`](#colrcontrol) object, or one of the `cursor`, `erase`, `move`,
`position`, or `scroll` `EscapeCode` objects from `colr.control_codes`.

### cursor_hide
`cursor_hide(file=sys.stdout)`

Hide the cursor.

### cursor_show
`cursor_show(file=sys.stdout)`

Show the cursor.

### erase_display
`erase_display(method=EraseMethod.ALL_MOVE, file=sys.stdout)`

Clear the screen or part of the screen,
and possibly moves the cursor to the "home" position (1, 1).
See `method` argument below.

The `method` argument can be one of these possible values:

EraseMethod | Description
--- | ---
`EraseMethod.END` or `0` | Clear from cursor to the end of the screen.
`EraseMethod.START` or `1` | Clear from cursor to the start of the screen.
`EraseMethod.ALL_MOVE` or `2` | Clear all, and move home.
`EraseMethod.ALL_ERASE` or `3` | Clear all, and erase scrollback buffer.
`EraseMethod.ALL_MOVE_ERASE` or `4` | Like doing 2 and 3 in succession. This is a feature of `Colr`. It is not standard.

### erase_line
`erase_line(method=EraseMethod.ALL, file=sys.stdout)`

Erase a line, or part of a line. See `method` argument below.
Cursor position does not change.

The `method` argument can be one of these possible values:

EraseMethod | Description
--- | ---
`EraseMethod.END` or `0` | Clear from cursor to the end of the line.
`EraseMethod.START` or `1` | Clear from cursor to the start of the line.
`EraseMethod.ALL_MOVE` or `2` | Clear entire line.

### move_back
`move_back(columns=1, file=sys.stdout)`

Move the cursor back a number of columns.

### move_column
`move_column(column=1, file=sys.stdout)`

Move the cursor to the specified column.

### move_down
`move_down(lines=1, file=sys.stdout)`

Move the cursor down a number of lines.

### move_forward
`move_forward(columns=1, file=sys.stdout)`

Move the cursor forward a number of columns.

### move_next
`move_next(lines=1, file=sys.stdout)`

Move the cursor to the beginning of the line, a number of lines down.

### move_pos
`move_pos(line=1, column=1, file=sys.stdout)`

Move the cursor to the specified coordinates (1-based).

### move_prev
`move_prev(lines=1, file=sys.stdout)`

Move the cursor to the beginning of the line, a number of lines up.

### move_up
`move_up(lines=1, file=sys.stdout)`

Move the cursor up a number of lines.

### pos_restore
`pos_restore(file=sys.stdout)`

Restore cursor position from a prevous call to [`pos_save`](#pos_save)

### pos_save
`pos_save(file=sys.stdout)`

Save the cursor position for recall later, with [`pos_restore`](#pos_restore)

### scroll_down
`scroll_down(lines=1, file=sys.stdout)`

Scroll the page down a number of lines. New lines are added to the top.

### scroll_up
`scroll_up(lines=1, file=sys.stdout)`

Scroll the page up a number of lines. New lines are added to the bottom.

## Print functions

Several print-related functions are made available.

### print_inplace
`print_inplace(*args, **kwargs)`

A wrapper for `print()`, except it saves the cursor position, prints the text,
and then restores the position.
Calling this repeatedly will print in the same place over and over.

### print_overwrite
`print_overwrite(*args, **kwargs)`

A wrapper for `print()`, except it will move to the beginning of the line
before printing.

## colr.Control

The `Control` object allows you to build cursor movements/instructions by
using chained methods (much like the `Colr` object does for colors).
They are basically like strings, and can be used with `Colr` to build
animated or otherwise complex text.

### Example

```python
from colr import Control, Colr
# Build a string containing 'Hello',
# Move back 1 column,
# Append ' yes', with a fore color of red.
# Write the result to stdout, ending with a newline.
Control('Hello').move_back().text(Colr(' yes', 'red')).write(end='\n')

# Calling `write` on a Control will erase it's data. So that multiple `write`
# calls can be chained:
(
    Control()
    .move_column(5).text('Hey').write()
    # delay works when previous data is already written.
    .delay(0.5)
    # Starting fresh.
    .move_column(5).text('There').write(end='\n')
)
```
### Methods

A `Control` has all of the same methods as the module-level cursor-related
functions, except they build the escape code string within the `Control`
object for printing or `Control.write()`ing later.

#### Control.\_\_init\_\_

A `Control` can be initialized with any string data.

#### Control.chained
`Control.chained(data)`

Append some data/text to a `Control` and return the `Control`. `str(data)`
is called before appending.

#### Control.cursor_hide
`Control.cursor_hide`

Append the "hide cursor" code to this `Control`.

#### Control.cursor_show
`Control.cursor_show`

Append the "show cursor" code to this `Control`.

#### Control.delay
`Control.delay(seconds)`

Run `time.sleep(seconds)` and return this `Control`.

#### Control.erase_display
`Control.erase_display(method=EraseMethod.ALL_MOVE)`

Appends the code to clear the screen or part of the screen,
and possibly move the cursor to the "home" position (1, 1).
See `method` argument below.

The `method` argument can be one of these possible values:

EraseMethod | Description
--- | ---
`EraseMethod.END` or `0` | Clear from cursor to the end of the screen.
`EraseMethod.START` or `1` | Clear from cursor to the start of the screen.
`EraseMethod.ALL_MOVE` or `2` | Clear all, and move home.
`EraseMethod.ALL_ERASE` or `3` | Clear all, and erase scrollback buffer.
`EraseMethod.ALL_MOVE_ERASE` or `4` | Like doing 2 and 3 in succession. This is a feature of `Colr`. It is not standard.


#### Control.erase_line
`Control.erase_line(method=EraseMethod.ALL)`

Appends the code to erase a line, or part of a line.
See `method` argument below.
Cursor position does not change.

The `method` argument can be one of these possible values:

EraseMethod | Description
--- | ---
`EraseMethod.END` or `0` | Clear from cursor to the end of the line.
`EraseMethod.START` or `1` | Clear from cursor to the start of the line.
`EraseMethod.ALL_MOVE` or `2` | Clear entire line.

#### Control.last_code
`Control.last_code`

Returns the last escape code appended to this `Control`.
If no escape codes are found, `''` (empty string) is returned.

#### Control.move_back
`Control.move_back(columns=1)`

Appends the code to move the cursor back a number of columns.

#### Control.move_carriage_return
`Control.move_carriage_return()`

Appends the code to move the cursor to the beginning of the line, using `\r`.
This is the same as `self.move_column(1)`.

#### Control.move_column
`Control.move_column(column=1)`

Appends the code to move the cursor to a specific column.

#### Control.move_down
`Control.move_down(lines=1)`

Appends the code to move the cursor down a number of lines.

#### Control.move_forward
`Control.move_forward(columns=1)`

Appends the code to move the cursor forward a number of columns.

#### Control.move_next
`Control.move_next(lines=1)`

Appends the code to move the cursor to the beginning of the line, a number of
lines down.

#### Control.move_pos
`Control.move_pos(line=1, column=1)`

Appends the code to move the cursor to a new position.

#### Control.move_prev
`Control.move_prev(lines=1)`

Appends the code to move the cursor to the beginning of the line, a number
of lines up.

#### Control.move_up
`Control.move_up(lines=1)`

Appends the code to move the cursor up a number of lines.

#### Control.pos_restore
`Control.pos_restore`

Appends the code to restore the cursor position saved with `pos_save()`.

#### Control.pos_save
`Control.pos_save`

Appends the code to save current cursor position. Can be restored with
`pos_restore()`.

#### Control.repeat
`Control.repeat(count=2)`

Repeat the last control code a number of times.
Returns a new Control with this one's data and the repeated code.

```python
Control().move_up().repeat(3) == Control().move_up().move_up().move_up()
```

This only works if the last method called appended an escape code.

#### Control.repeat_all
`Control.repeat_all(count=2)`

Repeat this entire Control code a number of times.
Returns a new Control with this one's data repeated.

```python
Control('test').move_up().repeat(2) == Control('test').move_up().text('test').move_up()
```

This only works for text and escape codes, not `Control.delay` or
`Control.write`.

#### Control.scroll_down
`Control.scroll_down(lines=1)`

Appends the code to scroll the whole page down a number of lines,
new lines are added to the top.

#### Control.scroll_up
`Control.scroll_up(lines=1)`

Appends the code to scroll the whole page up a number of lines,
new lines are added to the bottom.

#### Control.stripped
`Control.stripped()`

Returns a str with all control codes stripped from this instance.

#### Control.text
`Control.text(text)`

Appends some text to this `Control`.

#### Control.write
`Control.write(file=sys.stdout, end='', delay=None)`

Write this control code to a file, clear the `Control`s data, and
return a blank `Control`. If `delay` is set, `time.sleep(delay)` will be
called in between character writes (somewhat simulates typing).
