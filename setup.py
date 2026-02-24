from setuptools import setup
from Cython.Build import cythonize

setup(
    name='XScript Core',
    # cythonize convierte el .pyx en un .c y luego prepara la compilación
    ext_modules=cythonize("src/modules/defines.pyx", language_level="3"),
)