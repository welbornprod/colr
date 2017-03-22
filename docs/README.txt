Colr
====

A python module for using terminal colors in linux. It contains a simple
``color`` function that accepts style and color names, and outputs a
string with escape codes, but also has all colors and styles as
chainable methods on the ``Colr`` object.

--------------

Dependencies:
-------------

System
~~~~~~

-  **Python 3.5+** - This library uses ``yield from`` and the ``typing``
   module. `Python 2 support is not planned. <#python-2>`__

Modules
~~~~~~~

*There are no dependencies required for importing this library on
Linux*, however:

-  `Docopt <https://github.com/docopt/docopt>`__ - Only required for the
   `command line tool <#colr-tool>`__ and the `colr.docopt
   wrapper <#colrdocopt>`__, not the library itself.
-  `Colorama <https://github.com/tartley/colorama>`__ - `Windows
   only <#windows>`__. This is not required on linux. It provides a
   helper for basic color support for Windows.

Installation:
-------------

Colr is listed on `PyPi <https://pypi.python.org/pypi/Colr>`__, and can
be installed using `pip <https://pip.pypa.io/en/stable/installing/>`__:

::

    pip install colr

Or you can clone the repo on
`GitHub <https://github.com/welbornprod/colr>`__ and install it from the
command line:

::

    git clone https://github.com/welbornprod/colr.git
    cd colr
    python3 setup.py install

--------------

Examples:
---------

Simple:
~~~~~~~

.. code:: python

    from colr import color
    print(color('Hello world.', fore='red', style='bright'))

Chainable:
~~~~~~~~~~

.. code:: python

    from colr import Colr as C
    print(
        C()
        .bright().red('Hello ')
        .normal().blue('World')
    )

    # Background colors start with 'bg', and AttributeError will be raised on
    # invalid method names.
    print(C('Hello ', fore='red').bgwhite().blue('World'))

Examples (256 Colors):
----------------------

Simple:
~~~~~~~

.. code:: python

    from colr import color
    # Invalid color names/numbers raise a ValueError.
    print(color('Hello world', fore=125, back=80))

Chainable:
~~~~~~~~~~

.. code:: python

    from colr import Colr as C
    # Foreground colors start with 'f_'
    # Background colors start with 'b_'
    print(C().f_125().b_80('Hello World'))

Examples (True Color):
----------------------

Simple:
~~~~~~~

.. code:: python

    from colr import color
    print(color('Hello there.', fore=(255, 0, 0), back=(0, 0, 0)))

Chainable:
~~~~~~~~~~

.. code:: python

    from colr import Colr as C
    # Foreground colors are set with the `rgb()` method.
    # Background colors are set with the `b_rgb()` method.
    # Text for the chained methods should be chained after or during
    # the call to the methods.
    print(C().b_rgb(0, 0, 0).rgb(255, 0, 0, 'Hello there.'))

Examples (Hex):
---------------

Simple:
~~~~~~~

.. code:: python

    from colr import color
    # When not using the Colr.hex method, the closest matching extended code
    # is used. For true color, just use:
    #     fore=hex2rgb('ff0000')
    # or
    #     Colr.hex('ff0000', rgb_mode=True)
    print(color('Hello there.', fore='ff0000', back='000'))

Chainable:
~~~~~~~~~~

.. code:: python

    from colr import Colr as C
    # Foreground colors are set with the `hex()` method.
    # Background colors are set with the `b_hex()` method.
    # Text for the chained methods should be chained after or during
    # the call to the methods.
    print(C().b_hex('#000').hex('ff0000', 'Hello there.'))

    # With rgb_mode set, these are the same:
    print(C().hex('ff0000', 'test', rgb_mode=True))
    print(C().rgb(255, 0, 0, 'test'))

--------------

Documentation:
--------------

Documentation for the ``colr`` API can be found in the GitHub repo
(`github.com/welbornprod/colr <https://github.com/welbornprod/colr>`__):

+------------------------------------------------------------------------------------------+-------------------------------------------------------+
| Module/Object                                                                            | Description                                           |
+==========================================================================================+=======================================================+
| `colr.Colr <https://github.com/welbornprod/colr/blob/dev/docs/colr.Colr.md>`__           | Methods for the ``Colr`` object, to colorize text.    |
+------------------------------------------------------------------------------------------+-------------------------------------------------------+
| `colr.controls <https://github.com/welbornprod/colr/blob/dev/docs/colr.controls.md>`__   | Functions and classes to control the cursor/screen.   |
+------------------------------------------------------------------------------------------+-------------------------------------------------------+
| `colr.progress <https://github.com/welbornprod/colr/blob/dev/docs/colr.progress.md>`__   | Progress updates, bars, or spinners.                  |
+------------------------------------------------------------------------------------------+-------------------------------------------------------+
| `colr.trans <https://github.com/welbornprod/colr/blob/dev/docs/colr.trans.md>`__         | Color code translation/detection.                     |
+------------------------------------------------------------------------------------------+-------------------------------------------------------+

--------------

Colr Tool:
----------

The ``colr`` package can be used as a command line tool. An entry point
script named ``colr`` is created when installed with pip. Otherwise it
can be executed using the ``python -m colr`` method.

.. code:: bash

    colr --help

Basic usage involves passing text, or piping stdin data and setting the
colors by position or flag.

.. code:: bash

    # These all do the same thing:
    colr "Test" "red" "white" "bright"
    colr "Test" -f "red" -b "white" -s "bright"
    printf "Test" | colr -f "red" -b "white" -s "bright"

Using the positional arguments is faster for just setting fore colors,
but the flag method is needed for stdin data, or for picking just the
background color or style:

.. code:: bash

    colr "Test" -s "bright"

Extended and True colors are supported:

.. code:: bash

    colr "Test" 124 255
    colr "Test" "255, 0, 0" "255, 255, 255"
    # Use true color (rgb) escape codes to generate a gradient, and then
    # center it in the terminal (0 means use terminal width).
    colr "Test" -G "255,0,0" -G "0,0,255" -c 0

It will do fore, back, style, gradients, rainbows, justification, and
translation. It can strip codes from text (as an argument or stdin), or
explain the codes found in the text.

`lolcat <https://github.com/busyloop/lolcat>`__ emulation:

.. code:: bash

    fortune | colr --rainbow

The colr tool does not read files, but it's not a problem:

.. code:: bash

    cat myfile.txt | colr --gradient red

Also see `ccat <https://github.com/welbornprod/ccat>`__.

Colr.docopt:
------------

Colr provides a wrapper for docopt that will automatically colorize
usage strings. If you provide it a script name it will add a little more
color by colorizing the script name too.

.. code:: python

    from colr import docopt
    argd = docopt(USAGE, script='mycommand')

--------------

Contributing:
-------------

As always contributions are welcome here. If you think you can improve
something, or have a good idea for a feature, please file an
`issue <https://github.com/welbornprod/colr/issues/new>`__ or a `pull
request <https://github.com/welbornprod/colr/compare>`__.

--------------

Notes:
------

Reasons
~~~~~~~

In the past, I used a simple ``color()`` function because I'm not fond
of the string concatenation style that other libraries use. The 'clor'
javascript library uses method chaining because that style suits
javascript, but I wanted to make it available to Python also, at least
as an option.

Reset Codes
~~~~~~~~~~~

The reset code is appended only if some kind of text was given, and
colr/style args were used. The only values that are considered 'no text'
values are ``None`` and ``''`` (empty string). ``str(val)`` is called on
all other values, so ``Colr(0, 'red')`` and ``Colr(False, 'blue')`` will
work, and the reset code will be appended.

This makes it possible to build background colors and styles, but also
have separate styles for separate pieces of text.

Python 2
~~~~~~~~

I don't really have the desire to back-port this to Python 2. It
wouldn't need too many changes, but I like the Python 3 features
(``yield from``, ``str/bytes``).

Windows
~~~~~~~

Basic colors are supported on Windows through the
`colorama <https://github.com/tartley/colorama>`__ library. It is only
imported if ``platform.system() == 'Windows'``. It provides a wrapper
around ``stdout`` and ``stderr`` to make basic ansi codes work. If the
import fails, then all color codes are disabled (as if
``colr.disable()`` was called). I booted into Windows 8 for the first
time in months to make this little feature happen, only to discover that
the color situation for CMD and PowerShell really sucks. If you think
you can help improve the ``colr`` package for windows, please see the
`contributing <#contributing>`__ section.

Misc.
~~~~~

This library may be a little too flexible:

.. code:: python

    from colr import Colr as C
    warnmsg = lambda s: C('warning', 'red').join('[', ']')(' ').green(s)
    print(warnmsg('The roof is on fire again.'))

.. figure:: https://welbornprod.com/static/media/img/colr-warning.png
   :alt: The possibilities are endless.

   The possibilities are endless.
