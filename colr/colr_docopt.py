#!/usr/bin/env python3
""" Colorizes docopt usage/version strings.

    -Christopher Joseph Welborn 11-15-16

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
    DEALINGS IN THE SOFTWARE."""
import sys

import docopt

from .colr import Colr as C

docopt_version = docopt.__version__
docopt_file = getattr(getattr(docopt, '__spec__', None), 'origin', None)

__all__ = ['docopt', 'docopt_version', 'docopt_file']

# This can be set with a call to colr_docopt.docopt().
# When set, the script name can be colorized.
SCRIPT = None

ARGS_DESC = {'fore': 'green'}
ARGS_HEADER = {'fore': 'lightblue'}
ARGS_LABEL = {'fore': 'red', 'style': 'bold'}
ARGS_OPTIONS = {'fore': 'blue'}
ARGS_SCRIPT = {'fore': 'green'}
ARGS_VERSION = {'fore': 'blue'}


class _ColorDocoptExit(SystemExit):

    """ Custom DocoptExit class, colorizes the help text. """

    usage = ''

    def __init__(self, message=''):
        usagestr = '{}\n{}'.format(message,
                                   _coloredhelp(self.usage)).strip()
        SystemExit.__init__(self, usagestr)


def _coloredhelp(s):
    """ Colorize the usage string for docopt
        (ColorDocoptExit, docoptextras)
    """
    newlines = []
    bigindent = (' ' * 16)
    in_opts = False
    for line in s.split('\n'):
        linestripped = line.strip('\n').strip().strip(':')
        if linestripped == 'Usage':
            # label
            line = line.replace('Usage', str(C('Usage', **ARGS_LABEL)))
        elif linestripped == 'Options':
            line = line.replace('Options', str(C('Options', **ARGS_LABEL)))
            in_opts = True
        elif (':' in line) and (not line.startswith(bigindent)):
            # opt,desc line. colorize it.
            lineparts = line.split(':')
            opt = lineparts[0]
            vals = [lineparts[1]] if len(lineparts) == 2 else lineparts[1:]

            # colorize opt
            if ',' in opt:
                opts = opt.split(',')
            else:
                opts = [opt]
            optstr = ','.join(str(C(o, **ARGS_OPTIONS)) for o in opts)

            # colorize desc
            valstr = ':'.join(str(C(val, **ARGS_DESC)) for val in vals)
            line = ':'.join((optstr, valstr))
        elif in_opts and line.startswith(bigindent):
            # continued desc string..
            # Make any 'Default:Value' parts look the same as the opt,desc.

            line = ':'.join(str(C(s, **ARGS_DESC)) for s in line.split(':'))
        elif (not line.startswith('    ')):
            # header line.
            line = str(C(line, **ARGS_HEADER))
        else:
            # Everything else, usage mainly.
            if SCRIPT:
                line = line.replace(SCRIPT, str(C(SCRIPT, **ARGS_SCRIPT)))

        newlines.append(
            '{}{}'.format(line, C('', style='reset_all'))
        )
    return '\n'.join(newlines)


def _docoptextras(help, version, options, doc):
    if (
            help and
            any((o.name in ('-h', '--help')) and o.value for o in options)):
        print(_coloredhelp(doc).strip("\n"))
        sys.exit()
    if (
            version and
            any(o.name == '--version' and o.value for o in options)):
        print(C(version, **ARGS_VERSION))
        sys.exit()


# Functions to override default docopt stuff
docopt.DocoptExit = _ColorDocoptExit
docopt.extras = _docoptextras

# We still need to use docopt later.
_old_docopt = docopt.docopt


# Replacement function for original docopt.docopt.
def docopt(
        doc, argv=None, help=True, version=None, options_first=False,
        script=None, colors=None):
    """
This is a wrapper for docopt.docopt that also sets SCRIPT to `script`.
    When SCRIPT is set, it can be colorized for the usage string.
    A dict of Colr options can be passed with `colors` to alter the
    styles.
    Available color options keys:
        desc     : Colr args for the description of options.
        label    : Colr args for the 'Usage:' and 'Options:' labels.
        header   : Colr args for the top line (program name), and any
                   other line that is not indented at all.
        options  : Colr args for the options themselves ('-h,--help').
        script   : Colr args for the script name, if found in the usage
                   text.
        version  : Colr args for the version when --version is used.

    Example:
        # `colors` only updates the default settings. You must override
        # them to change ALL the settings.
        argd = docopt(
            ...,
            script=SCRIPT,
            colors={'script': {'fore': 'red'}}
        )

Original docopt documentation follows:
    """
    # docopt documentation is appended programmatically after this func def.

    global SCRIPT
    global ARGS_DESC, ARGS_HEADER, ARGS_LABEL, ARGS_OPTIONS
    global ARGS_SCRIPT, ARGS_VERSION

    SCRIPT = script
    if colors:
        # Setup colors, if any were given.
        ARGS_DESC.update(
            colors.get('desc', colors.get('description', {}))
        )
        ARGS_HEADER.update(colors.get('header', {}))
        ARGS_LABEL.update(colors.get('label', {}))
        ARGS_OPTIONS.update(colors.get('options', {}))
        ARGS_SCRIPT.update(colors.get('script', {}))
        ARGS_VERSION.update(colors.get('version', {}))

    return _old_docopt(
        doc,
        argv=argv,
        help=help,
        version=version,
        options_first=options_first,
    )


# Append old docopt() documentation to this wrapper's docs.
docopt.__doc__ = '\n'.join((docopt.__doc__, _old_docopt.__doc__))
