#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Colr Setup

-Christopher Welborn 08-14-2015
"""

import sys
from distutils.core import setup
defaultdesc = 'Easy terminal colors, with chainable methods.'
try:
    import pypandoc
except ImportError:
    print('Pypandoc not installed, using default description.')
    longdesc = defaultdesc
else:
    # Convert using pypandoc.
    try:
        longdesc = pypandoc.convert('README.md', 'rst')
    except EnvironmentError:
        # Fallback to README.txt (may be behind on updates.)
        try:
            with open('docs/README.txt') as f:
                longdesc = f.read()
        except EnvironmentError:
            print('\nREADME.md and README.txt failed!', file=sys.stderr)
            longdesc = defaultdesc


setup(
    name='Colr',
    version='0.4.3',
    author='Christopher Welborn',
    author_email='cj@welbornprod.com',
    packages=['colr'],
    url='https://github.com/welbornprod/colr',
    license='LICENSE.txt',
    description=open('DESC.txt').read(),
    long_description=longdesc,
    keywords='python module library 3 terminal color colors escape codes',
    classifiers=[
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
