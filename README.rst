predicates
==========

A collection of predicate factories, functions, and partials, for
functional programming.

The ``predicates`` module provides a variety of `predicates`, `predicate
factories`, and `predicate partials`.

    A predicate is a function that returns the truth value of some
    condition

    -- Andrew M. Kuchling, `Python Functional Programming HOWTO`_

.. _Python Functional Programming HOWTO: http://docs.python.org/2/howto/functional.html#built-in-functions

`Predicate factories` are functions which *create* new predicates
based on their arguments (e.g., ``_and``, ``_nargs``). `Predicate
partials` are functions created by `partial application`_ of a
predicate's arguments.

.. _partial application: http://en.wikipedia.org/wiki/Partial_application
