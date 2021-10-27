#!/usr/bin/env python3

from distutils.core import setup

import re
VERSIONFILE = "justhink_world/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

setup(
    name='justhink_world',
    version=verstr,
    description=('Python package for representing the problem and the state'
                 ' in the JUSThink human-robot collaborative activity'),
    author='Utku Norman',
    author_email='utku.norman@epfl.ch',
    packages=['justhink_world'],
    license='LICENSE',
    long_description=open('README.md').read(),
    install_requires=[
        "wheel",
        "pomdp_py",
        "networkx",
        "pyglet",
        "pathlib",
        "importlib_resources",
        "pqdict",
    ],
    zip_safe=False,
)
