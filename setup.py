from setuptools import setup

requirements = {
    'install': [
        'distribute',
        ],
    'extras': {
        'docs': [
            'sphinx>=1.1',
            'agoraplex.themes.sphinx>=0.1.2',
            ],
        'tests': [
            'nose>=1.2.1',
            'coverage>=3.6',
            'pinocchio>=0.3.1',
            'xtraceback>=0.3.3',
            ],
        },
    }

setup(
    name='predicates',
    version='0.0.1',
    author='Tripp Lilley',
    author_email='tripplilley@gmail.com',
    packages=['predicates'],
    namespace_packages=[],
    url='https://github.com/agoraplex/predicates',
    license='BSD',
    description='A collection of predicate factories, functions, and partials, for functional programming.',
    long_description=open('README.rst').read(),
    install_requires=requirements.get('install', None),
    tests_require=requirements.get('extras', {}).get('tests', None),
    extras_require=requirements.get('extras', None),
)
