from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup


setup(
    name='predicates',
    version='0.0.0',
    author='Tripp Lilley',
    author_email='tripplilley@gmail.com',
    packages=['predicates'],
    namespace_packages=[],
    url='',
    license='See LICENSE',
    description='',
    long_description=open('README.rst').read(),
    install_requires=[],
    tests_require=['nose>=1.2.1'],
    extras_require={
        'docs': [
            'sphinx>=1.1',
            'agoraplex.themes.sphinx',
            ],
        },
)
