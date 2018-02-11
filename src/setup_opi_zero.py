#!/usr/bin/env python

#    JointBox - Your DIY smart home. Simplified.
#    Copyright (C) 2017 Dmitry Berezovsky
#    
#    JointBox is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    
#    JointBox is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
JontBox setuptools based packaging module.
See: https://packaging.python.org/en/latest/distributing.html
"""

from setuptools import setup, find_packages
from codecs import open
from os import path
from jointbox_opi_zero.version import version

src_dir = path.abspath(path.dirname(__file__))
root_dir = path.join(src_dir, '..')

# Get the long description from the README file
with open(path.join(root_dir, 'README.rst'), encoding='utf-8') as f:
    long_description = """
Jointbox: Orange PI Zero Drivers
================================

This package provides a set of drivers for Orange PI zero board.

Currently the following drivers are implemented:

* GPIO - `jointbox_opi_zero.drivers.OpiH3GPIODriver`

Please see jointbox package for more details: https://pypi.python.org/pypi/jointbox/
    """

setup(
    name='jointbox_opi_zero',
    # Semantic versioning should be used:
    # https://packaging.python.org/distributing/?highlight=entry_points#semantic-versioning-preferred
    version=version,
    description='Orange PI Zero specific drivers for jointbox',
    long_description=long_description,
    url='http://jointbox.org',
    keywords='home automation smarthouse arduino gpio sensors hardware temperature relay',

    # Author
    author='Dmitry Berezovsky',

    # License
    license='GPLv3',

    # Technical meta
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # License (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        # Python versions support
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    # Structure
    packages=find_packages(include=['jointbox_opi_zero']),

    install_requires=[
        'jointbox>=0.1.1',
        'pyA20==0.2.12'
    ],

    # Extra dependencies might be installed with:
    # pip install -e .[dev,test]
    extras_require={
        'dev': [],
        'test': [],
    }
)
