============
 predicates
============

A collection of predicate factories, functions, and partials, for
functional programming.

.. image:: https://travis-ci.org/agoraplex/predicates.png?branch=master
   :target: https://travis-ci.org/agoraplex/predicates

.. image:: https://coveralls.io/repos/agoraplex/predicates/badge.png?branch=master
   :target: https://coveralls.io/r/agoraplex/predicates

The ``predicates`` module provides a variety of `predicates`, `predicate
factories`, and `predicate partials`.

    "A predicate is a function that returns the truth value of some
    condition."

    -- Andrew M. Kuchling,
       `Python Functional Programming HOWTO <http://docs.python.org/2/howto/functional.html#built-in-functions>`_

`Predicate factories` are functions which *create* new predicates
based on their arguments (e.g., ``_and``, ``_nargs``). `Predicate
partials` are functions created by `partial application <http://en.wikipedia.org/wiki/Partial_application>`_ of a
predicate's arguments.

Complete `project documentation
<http://predicates.readthedocs.org/>`__ is available. Project source
is available at the `github project page
<https://github.com/agoraplex/predicates>`__.


Install
-------

To install from PyPI::

    $ pip install predicates


Developer installation
----------------------

To install the development version from the `github repository
<https://github.com/agoraplex/predicates>`__::

    $ git clone https://github.com/agoraplex/predicates.git predicates
    $ cd predicates
    $ virtualenv-2.7 --no-site-packages venv
    $ pip install -e '.[docs,tests]'

.. note::

   Pay particular attention to that `pip install` line. That's a
   `period`, followed by ``[docs,tests]`` [#hack]_ (and it's in
   single-quotes to keep bash from misunderstanding the square
   brackets).

Use `nosetests` to run the test suite::

    $ python setup.py nosetests

Use Sphinx to generate the HTML docs::

    # to build in build/sphinx/html/...:
    $ python setup.py build_sphinx

    # to build in docs/_build/html/... (which is what I do):
    $ make -C docs

.. [#hack] Yes, it's a hack. See the `python setup.py develop and
   extras <http://mail.python.org/pipermail/distutils-sig/2012-November/019369.html>`__
   thread on the `python-distutils-sig <http://www.python.org/community/sigs/current/distutils-sig/>`__
   `mailing list <http://mail.python.org/pipermail/distutils-sig/>`__).
