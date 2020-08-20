# !/usr/bin/env python

from distutils.core import setup

setup(
    name='ARID Dataset Helper',
    version='0.1.0',
    author='Justin Rokisky',
    author_email='jrokisky831@gmail.com',
    packages=['arid'],
    scripts=['arid/arid.py'],
    description='Helper function for working with the ARID dataset.',
    install_requires=[
        "jupyterlab",
        "Pillow"
    ],
)


