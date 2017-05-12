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
from version import version

src_dir = path.abspath(path.dirname(__file__))
root_dir = path.join(src_dir, '..')

# Get the long description from the README file
with open(path.join(root_dir, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='jointbox',
    # Semantic versioning should be used:
    # https://packaging.python.org/distributing/?highlight=entry_points#semantic-versioning-preferred
    version=version,
    description='Your DIY smart house. Simplified.',
    long_description=long_description,
    url='htpp://jointbox.org',
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
        'License :: OSI Approved :: GPLv3 License',
        # Python versions support
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    # Structure
    packages=find_packages(exclude=['opi']),
    py_modules=["app", 'cli', 'daemonize'],

    install_requires=[
        'PyYAML==3.11',
        'paho-mqtt==1.1',
        'typing==3.5.3.0',
        'numpy==1.12.0',
        'daemons==1.3.0',
        'smbus2==0.1.4'
    ],

    # Extra dependencies might be installed with:
    # pip install -e .[dev,test]
    extras_require={
        'dev': [],
        'test': [],
    },

    package_data={
        'examples': [path.join(root_dir, 'examples')],
    },

    entry_points={
        'console_scripts': [
            'jointbox=cli:main',
            'jointboxd=daemonize:main',
        ],
    }
)
