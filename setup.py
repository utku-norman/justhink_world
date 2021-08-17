#!/usr/bin/env python3

from distutils.core import setup

setup(
    name='justhink_world',
    version='0.1.0',
    description='TODO',
    author='Utku Norman',
    author_email='utku.norman@epfl.ch',
    packages=['justhink_world'],
    license='LICENSE',
    long_description=open('README.md').read(),
    install_requires=[
        "pomdp_py",
        "networkx",
        "pyglet",
        "pathlib",
        "importlib_resources",
        "pqdict",
    ],
    zip_safe=False,
)
