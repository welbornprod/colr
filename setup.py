#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Colr Setup

-Christopher Welborn 08-14-2015
"""

from distutils.core import setup
defaultdesc = 'Terminal colors for linux.'
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
            print('\nREADME.md and README.txt failed!')
            longdesc = defaultdesc


setup(
    name='Colr',
    version='0.2.1-1',
    author='Christopher Welborn',
    author_email='cj@welbornprod.com',
    packages=['colr'],
    url='http://pypi.python.org/pypi/Colr/',
    license='LICENSE.txt',
    description=open('DESC.txt').read(),
    long_description=longdesc,
    keywords='python module library 3 terminal color colors escape codes',
    classifiers=[
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
