from setuptools import setup
from Cython.Build import cythonize

setup(
    name='XScript Core',
    ext_modules=cythonize("src/modules/defines.pyx", language_level="3"),
)