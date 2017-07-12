from setuptools import setup, find_packages

# The version is updated automatically with bumpversion
# Do not update manually
__version = '0.1.0-alpha'


long_description = """ Python library to control the Smaract Controller:
SDC and MCS. The library provide a friendly API to configure and to use the
controllers and the motors connected to them. """


classifiers = [
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 3 - Alpha',

    # Indicate who your project is intended for
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'Topic :: Scientific/Engineering',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: User Interfaces',

    # Pick your license as you wish (should match "license" above)
    'License :: OSI Approved :: GNU Library or Lesser General Public ' + \
    'License (LGPL)',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2.7',
]

setup(
    name='smaract',
    version=__version,
    packages=find_packages(),
    entry_points={},
    author='Jordi Andreu Segura',
    author_email='jandreu@cells.es',
    maintainer='ctbeamlines',
    maintainer_email='ctbeamlines@cells.es',
    url='https://git.cells.es/controls/smaract',
    keywords='APP',
    license='LGPL',
    description='Python library to for Smaract Motor Controllers',
    long_description=long_description,
    requires=['setuptools (>=1.1)'],  # In PyPI
    # TODO: include the requires.
    # install_requires=['socket', 'serial'],  # In PyPI
    classifiers=classifiers
)
