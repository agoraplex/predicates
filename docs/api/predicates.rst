:mod:`predicates` --- Predicates for functional programming
===========================================================

.. module:: predicates
   :synopsis: A collection of predicate factories, functions, and partials, for functional programming.

.. include:: ../narr/blurb.rst


Naming conventions
------------------

Predicates prefixed with an underscore (``_``) are `predicate
factories`, returning `callables`, for composition, currying, or
delayed evaluation.

Predicates without a suffix, or suffixed with an underscore, are
`simple predicates` (i.e., they act immediately). Most of these begin
with `is` (e.g., :func:`isstring`, :func:`isatom`). If present, the
underscore suffix is to avoid conflicts with keywords, in the style of
:mod:`~operator.not_`).

Where names conflict with builtins or the standard library, an
appropriate mnemonic prefix or suffix distinguishes them.

There are a few places where we alias or duplicate builtins or
standard library functions to present a consistently-named set of
functions. E.g., :func:`iscallable` is equivalent to :func:`callable`.


.. _predicate_composition:

Predicate composition
---------------------

These functions take a sequence of predicates and return a callable
which composes those predicates into a single function.  These are the
complement of the :ref:`predicate_application` functions.

Unless otherwise noted, the signature of the returned callable is:

.. function:: fn (*args, **kwargs) -> bool

E.g.,

.. code-block:: python

   >>> fn = _and(isstring, isempty)
   >>> fn('')
   True
   >>> fn("bad robot!")
   False

We may compose the composition predicates, themselves, too. E.g.,

.. code-block:: python

   >>> fn = _and(isstring, _not(isempty))
   >>> fn("bad robot!")
   True
   >>> fn('')
   False

Note that `fn` is passing ``*args`` and ``**kwargs`` to its predicates
all at once, instead of applying them to each argument,
individually. We're effectively calling each predicate as
``pred(*args, **kwargs)``, which, in this case, would be ``pred('',
'')``.

.. code-block:: python

   >>> fn('', '')
   TypeError: _isa takes exactly 1 argument (2 given)

Passing two empty strings produces a :exc:`TypeError`. Since
:func:`isstring` and :func:`isempty` each take only one argument, we
get the :exc:`TypeError`. The :ref:`predicate_application` functions
apply a predicate to each argument.

To apply multiple predicates to multiple arguments, combine the
`composition` and `application` factories. E.g., to ensure that all of
a function's arguments are non-empty strings:

.. code-block:: python

   >>> non_empty_string = _and(isstring, _not(isempty))
   >>> fn = _all(non_empty_string)
   >>> fn("bad robot!")
   True
   >>> fn("bad robot!", "hurley")
   True
   >>> fn("bad robot!", '')
   False
   >>> fn("bad robot!", 4)
   False

Explanation
~~~~~~~~~~~

Conceptually, you may think of the produced callables as applying
their corresponding boolean comparisons to the results of evaluating
each predicate, in turn, on all of `fn`'s arguments *at once* . The
example above is equivalent to:

.. code-block:: python

   >>> isstring('') and isempty('')
   True
   >>> isstring("bad robot!") and isempty("bad robot!")
   False

These are also equivalent to (and, in fact, are implemented by)
calling :func:`all`, etc., on a list comprehension which applies each
of the predicates onto `fn`'s arguments. The function produced by the
example above is:

.. code-block:: python

   predicates = (isstring, isempty)
   def fn (*args, **kwargs):
       return all(pred(*args, **kwargs) for pred in predicates)

which is equivalent to:

.. code-block:: python

   def fn (*args, **kwargs):
       return all(pred(*args, **kwargs) for pred in (isstring, isempty))

which is equivalent to:

.. code-block:: python

   def fn (*args, **kwargs):
       predicate_results = (isstring(*args, **kwargs), isempty(*args, **kwargs))
       return all(predicate_results)


.. autofunction:: _and
.. autofunction:: _not
.. autofunction:: _or
.. autofunction:: _zip


.. _predicate_application:

Predicate application
---------------------

These functions take a single predicate and return a callable which
applies that predicate to each of its arguments, applying the
corresponding boolean mapping to the results. These are the complement
of the :ref:`predicate_composition` functions.

Unless otherwise noted, the signature of the returned callable is:

.. function:: fn (*args, **kwargs) -> bool

E.g.,

.. code-block:: python

    >>> fn = _all(isstring)
    >>> fn()
    True
    >>> fn("bad robot!")
    True
    >>> fn("bad robot!", "jack")
    True
    >>> fn("bad robot!", "jack", 4, 8, 15, 16, 23, 42)
    False
    >>> fn(4)
    False


.. autofunction:: _all
.. autofunction:: _any
.. autofunction:: _none


`_args` is a special, extremely flexible, very overloaded `predicate
factory` for applying predicates to a function's arguments. It is a
singleton instance of :class:`ArgSlicer`, the documentation for which
covers all of the :func:`_args` use-cases. It is a `predicate
application` because it selects a set of arguments to which to *apply*
a set of predicates.

.. function:: _args (...)

.. autoclass:: ArgSlicer


Argument predicates
-------------------

These are `predicate factories` which check constraints on the
presence or absence of the arguments with which the resulting
predicates are called. I.e., the new predicates evaluate the
*structure* of their arguments, not their *values*.

Unless otherwise noted, the signature of the returned callable is:

.. function:: fn (*args, **kwargs) -> bool

E.g., to test whether or not the new predicate receives at least one
argument:

.. code-block:: python

    >>> fn = _npos(atleast=1)
    >>> fn()
    False
    >>> fn("bad robot!")
    True
    >>> fn("bad robot!", "jack")
    True

To test whether or not the new predicate receives at least the keyword
arguments ``jack`` and ``sawyer``:

.. code-block:: python

    >>> fn = _inkw(atleast=('jack', 'sawyer')
    >>> fn(4)
    False
    >>> fn(jack=4, sawyer=8)
    True

.. autofunction:: _nargs
.. autofunction:: _npos
.. autofunction:: _nkw
.. autofunction:: _inkw


Value predicates
----------------

These predicates test aspects of the *values* of their
arguments. E.g., ``isempty(val)`` tests that ``val`` has zero length,
without making demands on its type (iterability, etc.), beyond its
implementing ``__len__``.

.. autofunction:: isempty


Type predicates
---------------

These predicates test aspects of the *type* of their arguments. E.g.,
``isstring(val)`` tests that ``val`` is a string (:func:`str` or
:func:`unicode`), without making demands on its value (empty,
non-empty, etc.)

They are `composable`, since they test only the features they
need. E.g., ``_and(iscallable, isiterable)`` would be `True` for any
class which implemented both ``__call__`` and ``__iter__``.

Type predicate factory
~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: _isa

Generated type predicates
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: isatom
.. autofunction:: isiterable
.. autofunction:: isnsiterable

.. autofunction:: iscallable
.. autofunction:: iscontainer
.. autofunction:: ishashable
.. autofunction:: isiterator

.. autofunction:: ismap
.. autofunction:: ismmap
.. autofunction:: ismapv
.. autofunction:: isitemsv
.. autofunction:: iskeysv
.. autofunction:: isvalsv

.. autofunction:: isseq
.. autofunction:: ismseq
.. autofunction:: isset
.. autofunction:: ismset
.. autofunction:: issized
.. autofunction:: isslice
.. autofunction:: islist
.. autofunction:: istuple

.. autofunction:: isstring
.. autofunction:: isstr
.. autofunction:: isunicode

.. autofunction:: isbool

.. autofunction:: isint
.. autofunction:: islong
.. autofunction:: isfloat


Identity predicates
-------------------

These predicates test object identity (i.e., the :ref:`is <is>`
operator).

Identity predicate factory
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: _is

Generated identity predicates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: isnone
.. autofunction:: istrue
.. autofunction:: isfalse


Helpers
-------

These functions are the foundations upon which several of the
predicates are built. They may be useful when writing new predicates
that are more than composition and application of the existing
predicates.

.. autofunction:: _apply
.. autofunction:: _return
.. autofunction:: _nis
.. autofunction:: _fnis
