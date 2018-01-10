# ------------------------------------------------------------------------------
# This file is part of smaract (https://github.com/ALBA-Synchrotron/smaract)
#
# Copyright 2008-2017 CELLS / ALBA Synchrotron, Bellaterra, Spain
#
# Distributed under the terms of the GNU General Public License,
# either version 3 of the License, or (at your option) any later version.
# See LICENSE.txt for more info.
#
# You should have received a copy of the GNU General Public License
# along with smaract. If not, see <http://www.gnu.org/licenses/>.
# ------------------------------------------------------------------------------


from setuptools import setup, find_packages

# The version is updated automatically with bumpversion
# Do not update manually
__version = '0.0.1-alpha'


long_description = """ Python library to control the Smaract Controller:
SDC and MCS. The library provide a friendly API to configure and use the
controllers and the axes (motors) connected to them. """

# TODO: Include documentation.

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
    'License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2.7',
]

setup(
    name='smaract',
    version=__version,
    packages=find_packages(),
    entry_points={},
    author='R.Homs and J.Andreu',
    author_email='ctbeamlines@cells.es',
    maintainer='ctbeamlines',
    maintainer_email='ctbeamlines@cells.es',
    url='https://github.com/ALBA-Synchrotron/smaract',
    keywords='APP',
    license='GPL',
    description='Python library to for Smaract Motor Controllers',
    long_description=long_description,
    requires=['setuptools (>=1.1)'],  # In PyPI
    # TODO: include the requirements.
    # install_requires=['socket', 'serial'],  # In PyPI
    classifiers=classifiers
)
