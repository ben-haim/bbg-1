#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    'blpapi',
    'numpy',
    'pandas'
]

test_requirements = [
    'nose'
]

setup(
    name='bbg',
    version='0.1.0',
    description='bbg provides an interface to the Bloomberg API (blpapi).',
    long_description=readme + '\n\n' + history,
    author='Brian Jacobowski',
    author_email='bjacobowski.dev@gmail.com',
    url='https://github.com/bjacobowski/bbg',
    packages=[
        'bbg',
        'bbg.bloomberg',
        'bbg.globals',
        'bbg.tests',
        'bbg.utils'
    ],
    package_dir={'bbg':
                 'bbg'},
    include_package_data=True,
    install_requires=requirements,
    dependency_links=[
        "static.bloomberglabs.com/api/python/"
    ],
    license="BSD",
    zip_safe=False,
    keywords='bbg',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],
    test_suite='tests',
    tests_require=test_requirements
)