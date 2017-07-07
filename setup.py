from setuptools import setup


name = 'smaract'
scripts = []
author = 'jandreu (CTBeamlines)'
author_email = 'ctbeamlines@cells.es'
description = 'Python library to for Smaract Motor Controllers'
url = 'gitcomputing.cells.es'
requires = []

setup(
    name=name,
    packages=['smaract'],
    scripts=scripts,
    author=author,
    author_email=author_email,
    description=description,
    url=url,
    requires=requires,
)
