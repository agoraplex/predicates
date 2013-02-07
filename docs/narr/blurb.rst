The :mod:`predicates` module provides a variety of `predicates`,
`predicate factories`, and `predicate partials`.

    A predicate is a function that returns the truth value of some
    condition

    -- Andrew M. Kuchling, `Python Functional Programming HOWTO`_

.. _Python Functional Programming HOWTO: http://docs.python.org/2/howto/functional.html#built-in-functions

`Predicate factories` are functions which *create* new predicates
based on their arguments (e.g., :func:`~predicates._and`,
:func:`~predicates._nargs`). `Predicate partials` are functions
created by :wikipedia:`partial application` of a predicate's
arguments.
