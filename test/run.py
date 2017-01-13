#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" test_colr.py
    Run a few tests for the Colr library.
    Besides unit tests, just running this script will display any obvious
    display bugs.
    -Christopher Welborn 08-30-2015
"""
# NOTE: There are actual tests to run, but this helps with display/formatting
#       problems.

import os
import random
import sys

parentdir = os.path.split(os.path.abspath(sys.path[0]))[0]
if parentdir.endswith('colr'):
    # Use dev version before installed version.
    sys.path.insert(0, parentdir)

try:
    from colr import (
        __version__,
        Colr,
        auto_disable,
        color,
        disabled,
        docopt,
        name_data,
    )
except ImportError as ex:
    print('\nUnable to import Colr!: {}'.format(ex), file=sys.stderr)
    sys.exit(1)

NAME = 'Colr Test Run'
VERSIONSTR = '{} v. {}'.format(NAME, __version__)
SCRIPT = os.path.split(os.path.abspath(sys.argv[0]))[1]
SCRIPTDIR = os.path.abspath(sys.path[0])

USAGESTR = """{versionstr}
    Usage:
        {script} [-h | -v]

    Options:
        -h,--help     : Show this help message.
        -v,--version  : Show version.
""".format(script=SCRIPT, versionstr=VERSIONSTR)

# Max widths, 1/3 width, for justification tests.
maxwidth = 78
chunkwidth = maxwidth / 3

# Automatically disable colors when piping output.
auto_disable()


def main(argd):
    """ Main entry point, expects doctopt arg dict as argd. """
    print('Running {}'.format(color(VERSIONSTR, fore='red', style='bright')))

    justify_tests()
    join_tests()
    gradient_override_tests()
    gradient_mix_tests()
    rainbow_tests()
    name_data_tests()

    if disabled():
        print('\nColr was disabled.')
    return 0


def gradient_mix_tests():
    """ Test display of the gradient options. """
    # Gradient should operate on self.data when no text is provided.
    print(Colr('This is a gradient self.data.').gradient())

    # Gradient should append to self.data when no text is provided.
    print(
        Colr('This is a green self.data', fore='green')(' ')
        .gradient('And this is an appended gradient.', name='blue'))

    # Gradient should be okay with ljust/center/rjust.
    print(Colr().gradient('This is a left gradient').ljust(maxwidth))
    print(Colr().gradient('Center gradient.').center(maxwidth))
    print(Colr().gradient('Right-aligned gradient.').rjust(maxwidth))

    # Gradient and ljust/center/rjust would be chainable.
    print(Colr()
          .ljust(chunkwidth, text='Chained left.').gradient(name='red')
          .center(chunkwidth, text='Chained center.').gradient(name='white')
          .rjust(chunkwidth, text='Chained right.').gradient(name='blue'))

    # Black/white gradient should work in linemode or non-linemode.
    lines = ['This is a block made into a sad rainbow' for _ in range(5)]
    print(Colr('\n'.join(lines)).gradient(name='black'))
    lines = ['This is a block made into a long sad rainbow' for _ in range(5)]
    print(Colr('\n'.join(lines)).gradient(name='white', linemode=False))
    lines = ['This is a block made into a better rainbow' for _ in range(5)]
    print(Colr('\n'.join(lines)).gradient(name='red'))


def gradient_override_tests():
    """ Test gradient with explicit fore, back, and styles. """
    try:
        # Both fore and back are not allowed in a gradient.
        print(Colr().gradient(' ' * maxwidth, fore='reset', back='reset'))
    except ValueError:
        pass

    # Gradient back color.
    print(Colr().gradient(' ' * maxwidth, name='black', fore='reset'))
    # Explicit gradient fore color.
    print(Colr().gradient('-' * maxwidth, name='white', spread=2, back='blue'))
    # Implicit gradient fore color.
    print(Colr().gradient('_' * maxwidth, name='white'), end='\n\n')


def join_tests():
    """ Test join mixed with other methods. """
    def fancy_log(label, msg, tag):
        """ Squeezed justification with complex joins should account for
            existing text width.
        """
        return (
            Colr(label, fore='green')
            .center(
                # Centering on maxwidth would ruin the next rjust because
                # the spaces created by .center will not be overwritten.
                maxwidth - (len(tag) + 2),
                text=msg,
                fore='yellow',
                squeeze=True
            )
            .rjust(
                maxwidth,
                text=Colr(tag, fore='red').join(
                    '[', ']',
                    fore='blue'
                ),
                squeeze=True)
        )
    print(fancy_log('This is a label:', 'This is centered.', 'Status: Okay'))

    print(Colr('|', fore='blue').join(
        'This is regular text.'.ljust(maxwidth // 2 - 1),
        Colr('This is colored.', fore='red').rjust(maxwidth // 2)
    ))


def justify_tests():
    """ Test the justification methods, alone and mixed with other methods.
    """
    # Justified text should be chainable.
    print(
        Colr()
        .ljust(chunkwidth, text='Left', fore=255, back='green', style='b')
        .center(chunkwidth, text='Middle', fore=255, back='blue', style='b')
        .rjust(chunkwidth, text='Right', fore=255, back='red', style='b')
    )

    # Chained formatting must provide the 'text' argument,
    # otherwise the string is built up and the entire string width grows.
    # This built up string would then be padded, instead of each individual
    # string.
    print(
        Colr()
        # 256 color methods can be called with bg_<num>, b_<num>, b256_<num>.
        .b_82().b().f_255().ljust(chunkwidth, text='Left')
        .b256_56().b().f_255().center(chunkwidth, text='Middle')
        # Named background color start with 'bg' or 'b_'
        .bgred().b().f_255().rjust(chunkwidth, text='Right')
    )
    # Width should be calculated without color codes.
    print(Colr('True Middle').center(maxwidth, fore='magenta'))

    # Squeezed justification should account for existing text width.
    # But if text was previously justified, don't ruin it.
    print(Colr('Lefty', fore=232, back=255).center(
        maxwidth,
        text='Center',
        fore=232,
        back='blue',
        style='bright',
        squeeze=True))
    print(
        Colr('LeftyCenter'.center(maxwidth // 2), fore=232, back=255)
        .center(
            maxwidth / 2,
            text='Center',
            fore=232,
            back='blue',
            style='bright',
            squeeze=True
        )
    )


def name_data_tests(width=5, height=20):
    """ Test known names with name_data. """
    names = list(name_data)
    # Get width * height unique color names and print them (with their color).
    if width * height > len(names):
        width = 5
        height= 10
    names_done = set()
    for _ in range(height):
        cols = []
        for _ in range(width):
            n = random.choice(names)
            while n in names_done:
                n = random.choice(names)
            names_done.add(n)
            cols.append(Colr(n.center(16), fore=n))
        print(Colr(' ').join(cols))


def rainbow_tests():
    """ Test rainbow output, with or without linemode (short/long output)
    """
    print(Colr('This is a rainbow. It is very pretty.').rainbow())
    lines = ['This is a block of text made into a rainbow' for _ in range(5)]
    print(Colr('\n'.join(lines)).rainbow(movefactor=5))
    lines = ['This is a block made into a long rainbow' for _ in range(5)]
    print(Colr('\n'.join(lines)).rainbow(linemode=False))

    # Rainbow should honor fore,back,styles.
    print(Colr(' ' * maxwidth).rainbow(fore='reset', spread=.5))
    print(Colr('-' * maxwidth).rainbow(back='black', offset=30))
    print(Colr('Rainbow bright.').rainbow(style='bright').center(maxwidth))


if __name__ == '__main__':
    mainret = main(docopt(USAGESTR, version=VERSIONSTR, script=SCRIPT))
    sys.exit(mainret)
