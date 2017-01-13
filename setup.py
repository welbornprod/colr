#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Colr Setup

-Christopher Welborn 8-14-2015
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Try using the latest DESC.txt.
shortdesc = 'Easy terminal colors, with chainable methods.'
try:
    with open('DESC.txt', 'r') as f:
        shortdesc = f.read()
except FileNotFoundError:
    pass

# Default README files to use for the longdesc, if pypandoc fails.
readmefiles = ('docs/README.txt', 'README.txt', 'docs/README.rst')
for readmefile in readmefiles:
    try:
        with open(readmefile, 'r') as f:
            longdesc = f.read()
        break
    except EnvironmentError:
        # File not found or failed to read.
        pass
else:
    # No readme file found.
    # If a README.md exists, and pypandoc is installed, generate a new readme.
    try:
        import pypandoc
    except ImportError:
        print('Pypandoc not installed, using default description.')
        longdesc = shortdesc
    else:
        # Convert using pypandoc.
        try:
            longdesc = pypandoc.convert('README.md', 'rst')
        except EnvironmentError:
            # No readme file, no fresh conversion.
            print('Pypandoc readme conversion failed, using default desc.')
            longdesc = shortdesc

setup(
    name='Colr',
    version='0.6.0',
    author='Christopher Welborn',
    author_email='cj@welbornprod.com',
    packages=['colr'],
    url='https://github.com/welbornprod/colr',
    description=shortdesc,
    long_description=longdesc,
    keywords=('python module library 2 3 linux terminal escape codes color'),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points={
        'console_scripts': [
            'colr = colr.__main__:main',
        ]
    }
)
