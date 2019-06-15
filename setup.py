from setuptools import setup
import os
import codecs
import re

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

# Get the long description from the README file
with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='csmdirsearch',
    version=find_version("csmdirsearch", "__init__.py"),

    description='Search the Mines directory',
    long_description=long_description,

    url='https://github.com/jackrosenthal/csmdirsearch',

    author='Jack Rosenthal, Samuel Warfield',
    author_email='warfield@mines.edu',

    license='MIT',

    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Education',
        'Topic :: System :: Systems Administration :: Authentication/Directory',

        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],

    # What does your project relate to?
    keywords='directory mines scraping',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=['csmdirsearch'],

    python_requires='>=3.7, <7',

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['beautifulsoup4>=4.4.0', 'requests>=2.0.0'],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'dirsearch=csmdirsearch.__main__:main',
        ],
    },
)
