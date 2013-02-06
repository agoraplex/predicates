predicates
==========

A collection of predicate factories, functions, and partials, for
functional programming.

The ``predicates`` module provides a variety of `predicates`, `predicate
factories`, and `predicate partials`.

`Predicates` are functions which evaluate their arguments according to
some set of constraints, returning either `True` or `False` (e.g.,
``isstring``, ``isempty``). `Predicate factories` are functions which
*create* new predicates based on their arguments (e.g., ``_and``,
``_nargs``). `Predicate partials` are functions created by `partial
application`_ of a predicate's arguments.

.. _partial application: http://en.wikipedia.org/wiki/Partial_application
