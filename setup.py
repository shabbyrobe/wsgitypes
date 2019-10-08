import os
from distutils.core import setup
from typing import List

from setuptools import find_packages

__version__ = "0.0.1"


with open('README.rst', 'r') as f:
    readme = f.read()


dependencies = [
    'mypy>=0.720',
    'typing-extensions',
]

setup(
    name="wsgitypes-stubs",
    version=__version__,
    description='MyPy types for WSGI',
    long_description=readme,
    long_description_content_type='text/x-rst',
    license='MIT',
    url="https://github.com/shabbyrobe/wsgitypes",
    author="Blake Williams",
    author_email="code@shabbyrobe.org",
    py_modules=[],
    python_requires='>=3.6',
    install_requires=dependencies,
    packages=[
        'wsgitypes',
        *find_packages(exclude=['scripts']),
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7'
    ]
)
