from setuptools import setup

requirements = {
    'install': [
        'distribute',
        ],
    'extras': {
        'docs': [
            'sphinx>=1.1',
            'agoraplex.themes.sphinx>=0.1.3',
            'pygments',
            ],
        'tests': [
            'nose>=1.2.1',
            'coverage>=3.6',
            'pinocchio>=0.3.1',
            'xtraceback>=0.3.3',
            'pygments',
            ],
        },
    }

# write requirements for Travis and ReadTheDocs to use...
with open("reqs/travis.txt", "w") as travis:
    travis.write('\n'.join(requirements['extras']['tests']) + '\n')

with open("reqs/rtfd.txt", "w") as rtfd:
    rtfd.write('\n'.join(requirements['extras']['docs']) + '\n')

setup(
    name='predicates',
    version='0.0.5',
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

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ]
)
