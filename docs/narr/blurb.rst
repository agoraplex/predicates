The :mod:`predicates` module provides a variety of `predicates`,
`predicate factories`, and `predicate partials`.

`Predicates` are functions which evaluate their arguments according to
some set of constraints, returning either :data:`True` or
:data:`False` (e.g., :func:`~predicates.isstring`,
:func:`~predicates.isempty`). `Predicate factories` are functions
which *create* new predicates based on their arguments (e.g.,
:func:`~predicates._and`, :func:`~predicates._nargs`). `Predicate
partials` are functions created by :wikipedia:`partial application` of
a predicate's arguments.
