#!/usr/bin/env python3
""" Colorizes docopt usage/version strings.
    -Christopher Joseph Welborn 11-15-16
"""
import os.path
import sys

from .colr import Colr as C

import docopt

# This can be set with a call to colr_docopt.docopt().
# When set, the script name can be colorized.
SCRIPT = None

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
            line = str(C(line, 'red', style='bold'))
        elif linestripped == 'Options':
            line = str(C(line, 'red', style='bold'))
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
            optstr = ','.join(str(C(o, 'blue')) for o in opts)

            # colorize desc
            valstr = ':'.join(str(C(val, 'green')) for val in vals)
            line = ':'.join((optstr, valstr))
        elif in_opts and line.startswith(bigindent):
            # continued desc string..
            # Make any 'Default:Value' parts look the same as the opt,desc.

            line = ':'.join(str(C(s, 'green')) for s in line.split(':'))
        elif (not line.startswith('    ')):
            # header line.
            line = str(C(line, 'red', style='bold'))
        else:
            # Everything else, usage mainly.
            if SCRIPT:
                line = line.replace(SCRIPT, str(C(SCRIPT, 'green')))

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
        print(C(version, 'blue'))
        sys.exit()

# Functions to override default docopt stuff
docopt.DocoptExit = _ColorDocoptExit
docopt.extras = _docoptextras

_old_docopt = docopt.docopt
# Just provide the docopt function to users.
def docopt(
        doc, argv=None, help=True, version=None, options_first=False,
        script=None):
    """
This is a wrapper for docopt.docopt that also sets SCRIPT to `script`.
    When SCRIPT is set, it can be colorized for the usage string.

Original docopt documentation follows:
    """
    global SCRIPT
    SCRIPT = script
    return _old_docopt(
        doc,
        argv=argv,
        help=help,
        version=version,
        options_first=options_first,
    )

# Append old docopt() documentation to this wrapper's docs.
docopt.__doc__ = '\n'.join((docopt.__doc__, _old_docopt.__doc__))
