# io.open is needed for projects that support Python 2.7
# It ensures open() defaults to text mode with universal newlines,
# and accepts an argument to specify the text encoding
# Python 3 only projects can skip this import
from io import open
from os import path

from setuptools import setup, find_packages

__version__ = '0.2.6'

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requires = f.read().splitlines()

setup(
    name='python-ibmcclient',
    version=__version__,
    description='iBMC client',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    author='xFusion Digital Technologies Co., Ltd.',
    author_email='',
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Apache Software License',

        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],

    keywords='iBMC redfish API client',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required
    install_requires=requires,
    extras_require={  # Optional
        'dev': ['check-manifest', 'flake8'],
        'test': ['coverage'],
    },
    project_urls={  # Optional
        'Bug Reports': '',
        'Source': '',
    },
)
