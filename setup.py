# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Let\'s you trade stocks with i persistent portfolio.',
    'author': 'Jim Holmström <jimho@kth.se>',
    'version': '0.5',
    'install_requires':[],
    'packages': ['stockmarket'],
    'scripts': [],
    'name': 'stockmarket'
}

setup(**config)
