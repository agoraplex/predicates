.. Agoraplex Predicates documentation master file, created by
   sphinx-quickstart2 on Fri Jan 11 20:37:25 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _index:

====================================
 The `Agoraplex` Predicates Library
====================================

.. include:: narr/blurb.rst

The `Agoraplex` Predicates Library is licensed under the BSD
"3-clause" license. See :doc:`LICENSE` for details.


Motivation and applications
---------------------------

You could say that I hate Python's `lambda` syntax, and that this is
just a very indirect way of expressing it. While I *do* dislike the
syntax, that's really not it at all...

:mod:`predicates` is actually part of an extensible (work-in-progress)
way to build matchers (or selectors, or whatever you call them). I.e.,
do something based on matching a value to a set of rules.

The original motivation was (is) a :wikipedia:`predicate dispatch` library
[#why_arg_predicates]_ for Python, but... something else came up.

.. code-block:: python

   >>> from predicates import (
   ...   _any,
   ...   _nis,
   ...   _contains,
   ...   isstring,
   ...   _and,
   ...   true_
   ... )

   >>> def the_answer (*args, **kwargs):
   ...   return "forty-two"

   >>> def the_question (*args, **kwargs):
   ...   return "what do you get when you multiply six by nine?"

   >>> def other (*args, **kwargs):
   ...   return "yeah. I got nuthin'. sorry."

   >>> def marvin (*args, **kwargs):
   ...   return "no, that's okay, i'll just sit here and rust."

   >>> the_guide = (
   ...   (_any(_nis(exactly=42)), the_question),
   ...   (_any(_and(isstring, _contains("sad"))), marvin),
   ...   (_any(
               _and(isstring,
                    _contains("life", "the universe", "everything"))),
          the_answer),
   ...   (true_, other)
   ... )

   >>> def dispatch (rules, *args, **kwargs):
   ...   for (rule, method) in rules:
   ...     if rule(*args, **kwargs):
   ...       return method(*args, **kwargs)
   ...   raise NotImplementedError

   >>> dispatch(the_guide, 42)
   'what do you get when you multiply six by nine?'

   >>> dispatch(the_guide, 23, 64, "how sad is he?")
   "no, that's okay, i'll just sit here and rust."

   >>> dispatch(the_guide,
   ...   "he's pondering the question.",
   ...   "which question?",
   ...   "THE question!",
   ...   "life. the universe. everything!",
   ...   "oh. that one.")
   'forty-two'


Of course, that's a very ugly example, since it doesn't use
decorators, or mine `annotations` [#using_anodi]_. Worse, though, it
uses that brutally naïve linear probe through the predicates. While
that allows giving rules precedence, it it also needlessly repeats any
shared tests, and, well, it's just embarassing. So... future work on
:mod:`predicates` will include a predicate compiler and an
optimizer. The compiler might expand boolean predicates into Python
statements, instead of requiring multiple nested function calls. The
optimizer might, given a set of predicates, canonicalize them and
build a tree, with each leaf being one of the original set's results.

*Tomorrow Man* [#tomorrow_man]_ is gonna get right on that.


.. [#why_arg_predicates] ...which explains all of the ``argXXX``
   predicates, I hope.

.. [#using_anodi] Using :pypi:`anodi`, for example...

.. [#tomorrow_man] Not to be confused with *The* Tomorrow Man, about
   whom Google just told me.


API Documentation
=================

Documentation for every :doc:`predicates <api/predicates>` API.

.. toctree::
   :maxdepth: 2

   api/predicates


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. add misc docs to a hidden toc to avoid warnings (a trick borrowed
   from Pyramid docs)

.. toctree::
   :hidden:

   narr/blurb
   LICENSE
