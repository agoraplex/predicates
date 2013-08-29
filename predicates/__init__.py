from operator import (
    # comparisons
    lt, le, eq, ne, ge, gt,

    # booleans
    not_, truth,

    # object identity
    is_, is_not,
    )

from collections import (
    Callable,
    Container,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MappingView,
    ItemsView,
    KeysView,
    ValuesView,
    Sequence,
    MutableSequence,
    Set,
    MutableSet,
    Sized,
    )


# Predicate composition
# ---------------------

def _and (*predicates):
    """
    Returns a `callable` which returns `True` if *all* ``predicates``
    are true. This *is* short-circuiting.
    """
    def _and (*args, **kwargs):
        return all(pred(*args, **kwargs) for pred in predicates)
    return _and

def _or (*predicates):
    """
    Returns a `callable` which returns `True` if *any* ``predicates``
    are true. This *is* short-circuiting.
    """
    def _or (*args, **kwargs):
        return any(pred(*args, **kwargs) for pred in predicates)
    return _or

def _not (*predicates):
    """
    Returns a `callable` which returns `True` if *none* of the
    ``predicates`` are true.
    """
    def _not (*args, **kwargs):
        return not any(pred(*args, **kwargs) for pred in predicates)
    return _not

def _zip (*predicates):
    """
    Returns a `callable` which returns `True` if each application of a
    predicate to its corresponding argument returns `True`. I.e., it
    applies ``predicates[0]`` to ``args[0]``, ``predicates[1]`` to
    ``args[1]``, and so on. Technically, this lives in the grey area
    between :ref:`predicate_composition` and
    :ref:`predicate_application`.

    It inherits the truncation behaviour of :func:`zip` (i.e., it
    truncates to the shorter of `predicates` or `args`).

    The callable ignores keyword arguments, if present.

    **TODO:** What's the correct mathematical term for this? The
    `cross-product` would be *all predicates applied to all arguments*
    (i.e., `n x m`). While we're on the subject, should we add a
    cross-product factory?
    """
    def _zip (*args, **kwargs):
        return all(predicate(arg)
                   for (predicate, arg)
                   in zip(predicates, args))
    return _zip


# Predicate application
# ---------------------

def _all (predicate):
    """
    Returns a `callable` which returns `True` if ``predicate`` returns
    `True` for *all* of its *positional* arguments.
    """
    def _all (*args, **kwargs):
        return all(predicate(arg) for arg in args)
    return _all

def _any (predicate):
    """
    Returns a `callable` which returns `True` if ``predicate`` returns
    `True` for *any* of its *positional* arguments.
    """
    def _any (*args, **kwargs):
        return any(predicate(arg) for arg in args)
    return _any

def _none (predicate):
    """
    Returns a `callable` which returns `True` if ``predicate`` returns
    `True` for *none* of its *positional* arguments.
    """
    def _none (*args, **kwargs):
        return all(not predicate(arg) for arg in args)
    return _none


# Argument predicates
# -------------------

class ArgSlicer (object):
    """
    Flexible `predicate factory` to convert
    :meth:`~object.__getitem__` slices and direct calls (i.e.,
    :meth:`~object.__call__`) into `predicate partials` which apply a
    set of predicates to a subset of the callables' arguments.

    All access is through its (unenforced) singleton instance,
    :func:`_args`, but we expose the class for subclassing,
    monkeypatching, etc.

    Examples are the best way to explain this beast.

    * :meth:`~object.__getitem__` access to positional arguments.

      Ensure that first positional arg (`args[0]`), if present, is a
      string. Imposes no constraints on other posiitional or keyword
      args.

      .. code-block:: python

         >>> fn = _args[0](isstring)
         >>> fn()
         True
         >>> fn('jack')
         True
         >>> fn(4)
         False
         >>> fn('jack', 8, kate=15)
         True

      Ensure that the first two positional args (`args[0:2]`), if
      present, are strings. Imposes no constraints on other positional
      or keyword args.

      .. code-block:: python

         >>> fn = _args[0:2](isstring)
         >>> fn()
         True
         >>> fn('jack')
         True
         >>> fn('jack', 8)
         False
         >>> fn('jack', 'sawyer', 15, kate=15)
         True

      Ensure that any positional args are strings. Imposes no
      constraints on keyword args.

      .. code-block:: python

         >>> fn = _args[:](isstring)
         >>> fn()
         True
         >>> fn('jack')
         True
         >>> fn('jack', 8)
         False
         >>> fn('jack', 'sawyer', kate=15)

    * :meth:`~object.__call__` access to positional arguments:

      Ensure all positional arguments are strings. Imposes no
      constraints on keyword args. This is equivalent to (and, in
      fact, is implemented as) the ``_args[:](isstring)`` example,
      above.

      .. code-block:: python

         >>> fn = _args(isstring)
         >>> fn()
         True
         >>> fn('jack')
         True
         >>> fn('jack', 8)
         False
         >>> fn('jack', 'sawyer', kate=15)

    * :meth:`~object.__call__` access to keyword arguments:

      Ensure that keyword arguments ``jack`` and ``kate`` *exist*, and
      that `jack` is a string, and `kate` is an integer. Imposes no
      constraints on positional or other keyword args.

      .. code-block:: python

         >>> fn = _args(jack=isstring, kate=isint)

         >>> fn()
         False
         >>> fn(jack='', kate=15)
         True
         >>> fn(jack='')
         False
         >>> fn(jack=4)
         False
         >>> fn(4, 8, jack='', kate=15)
         True

    * :meth:`~object.__call__` access to positional and keyword
      arguments:

      Ensure that keyword arguments ``jack`` and ``kate`` *exist*,
      that `jack` is a string, that `kate` is an integer, and that any
      positional arguments are strings. Imposes no constraints on
      other keyword args.

      .. code-block:: python

         >>> fn = _args(isstring, jack=isstring, kate=isint)

         >>> fn()
         False
         >>> fn(jack='', kate=15)
         True
         >>> fn("bad robot!", jack='', kate=15)
         True
         >>> fn("bad robot!", jack='')
         False
         >>> fn(jack=4)
         False
         >>> fn(4, 8, jack='', kate=15)
         False

    * Mixed :meth:`~object.__getitem__` and :meth:`~object.__call__`
      access to positional and keyword arguments:

      Ensure that keyword arguments ``jack`` and ``kate`` *exist*,
      that `jack` is a string, that `kate` is an integer, and that the
      first two positional arguments (`args[0:2]`), if present, are
      strings. Imposes no constraints on other positional or keyword
      arguments.

      .. code-block:: python

         >>> fn = _args[0:2](isstring, jack=isstring, kate=isint)
         >>> fn()
         False
         >>> fn(jack='', kate=15)
         True
         >>> fn("bad robot!", jack='', kate=15)
         True
         >>> fn("bad robot!", 'sawyer', jack='', kate=15)
         True
         >>> fn("bad robot!", 'sawyer', 23, jack='', kate=15)
         True
         >>> fn(4, "bad robot!", jack='', kate=15)
         False
         >>> fn("bad robot!", 'sawyer', 23, jack=4, kate='15')
         False

    .. note::

       **TODO:** use multi-dimensional extended slice syntax to apply
       predicates to specific args. E.g.,

       .. code-block:: python

          >>> fn = _args[0, 1, 3:5](isstring, isint, isfloat, hurley=isint)
          >>> fn("bad robot!", 4, (), 8.0, 15.0, hurley=16)
          True

       Another option is to put the keyword args into the slice:

       .. code-block:: python

          >>> fn = _args[0, 1, 3:5, 'hurley'](
          ...         isstring, isint, isfloat, isint)
          >>> fn("bad robot!", 4, (), 8.0, 15.0, hurley=16)
          True

       ...or is it starting to get ridiculous? I don't like the
       increasing distance between the arg selector (the `key` to
       :meth:`~object.__getitem__`) and the corresponding
       predicate. Maybe we should move to the simpler ``_args(p0, p1,
       p2, key1=p3, key2=p4)`` form? Combining :func:`_all` and
       :func:`_apply` would let us duplicate the behaviour of the
       current ``_args(predicate)``, but we'd lose the ability to
       (easily) apply separate predicates to *ranges* of args,
       including *overlapping* ranges, like we get with the
       multidimensional slice. E.g.,

       .. code-block:: python

          >>> fn = _args[0:4, 3:5](isstring, _not(isempty))
          >>> fn('', '', "bad robot!")
          True
          >>> fn('', "bad robot!", '', 'jack', (42,))
          True
          >>> fn('', "bad robot!", '', 'jack', ())
          False

       Ultimately, what I'm looking for is a "single point of truth"
       for specifying, concisely, constraints on all of the arguments
       I care about.
    """

    def __call__ (self, pos_predicate=None, **kwargs):
        """
        Wrapper around :meth:`__getitem__` to shortcut the 'apply to
        all arguments' (`[:]`) case and 'apply to keyword argument(s)'
        (`['x', 'y', 'z']) cases.
        """
        return self[:](pos_predicate, **kwargs)

    def __getitem__ (self, key):
        """
        Returns a `predicate factory` which will create a `callable`
        which returns `True` if its ``predicate`` returns `True` for
        each element of the slice of its args using this function's
        `key` argument. I.e., ``args[key]``.

        **NOTE:** keys must (currently) be integers or :func:`slice`
        objects.
        """
        # replace each non-slice element of `key` with an equivalent
        # slice, forcing the result to be a tuple (we need `args[0]`
        # to return `(x,)`, not `x`, so we can use it as `*args[0]` ).
        key = (key if isslice(key)
               else slice(key, key+1) if key >= 0
               else slice(key, None))

        def _args_factory (pos_predicate=None, **kw_predicates):
            """
            Returns a `callable` which returns `True` if
            `pos_predicate` returns `True` for each positional arg in
            the slice ``args[key]`` (where `key` is the value
            originally passed to ``_args[...]``), and, for each `(kw,
            predicate)` pair in `kwargs`, applying the predicate to
            ``kwargs[kw]`` returns `True`.
            """

            if not (pos_predicate or kw_predicates):
                raise ValueError(
                    "must specify a predicate for positional args, " +
                    "a set of predicates for keyword args, or both.")

            # keyword predicates only
            if not pos_predicate:
                def _args (*args, **kwargs):
                    return all(predicate(kwargs.get(kw, None))
                               for (kw, predicate)
                               in kw_predicates.items())
                return _args

            # get a predicate to map the predicate to an iterable
            pos_predicate = _all(pos_predicate)

            # positional predicate only
            if not kw_predicates:
                def _args (*args, **kwargs):
                    return pos_predicate(*args[key])
                return _args

            # positional *and* keyword predicates
            def _args (*args, **kwargs):
                return (pos_predicate(*args[key]) and
                        all(predicate(kwargs.get(kw, None))
                            for (kw, predicate)
                            in kw_predicates.items()))
            return _args
        return _args_factory
_args = ArgSlicer()

def _nargs (atleast=False, atmost=False, exactly=False):
    """
    Returns a `callable` which returns `True` if it is called with `at
    least`, `at most`, or `exactly` the number of positional *and*
    keyword arguments specified in `atleast`, `atmost`, and `exactly`,
    respectively. See :func:`_npos` and :func:`_nkw` for separate
    constraints on positional and keyword args, respectively.

    `atleast` and `atmost` may be combined, but `exactly` must stand
    alone.
    """
    def length (*args, **kwargs):
        return len(args) + len(kwargs)
    return _fnis(length, atleast, atmost, exactly)

def _npos (atleast=False, atmost=False, exactly=False):
    """
    Returns a `callable` which returns `True` if it is called with `at
    least`, `at most`, or `exactly` the number of positional arguments
    specified in `atleast`, `atmost`, and `exactly`, respectively. See
    :func:`_nkw` and :func:`_nargs`.

    `atleast` and `atmost` may be combined, but `exactly` must stand
    alone.
    """
    def length (*args, **kwargs):
        return len(args)
    return _fnis(length, atleast, atmost, exactly)

def _nkw (atleast=False, atmost=False, exactly=False):
    """
    Returns a `callable` which returns `True` if it is called with `at
    least`, `at most`, or `exactly` the number of keyword arguments
    specified in `atleast`, `atmost`, and `exactly`, respectively. See
    :func:`_npos` and :func:`_nargs`.

    `atleast` and `atmost` may be combined, but `exactly` must stand
    alone.
    """
    def length (*args, **kwargs):
        return len(kwargs)
    return _fnis(length, atleast, atmost, exactly)

def _inkw (atleast=False, atmost=False, exactly=False):
    """
    Returns a `callable` which returns `True` if it has `at least`,
    `at most`, or `exactly`, the keyword arguments specified. This
    constrains the *argument names*, while :func:`_nkw` constrains the
    *number* of arguments.

    Note, too, that this does *not* constrain the keyword arguments'
    *values*.

    `atleast` and `atmost` may be combined, but `exactly` must stand
    alone.

    **TODO:** add a new predicate, or extend this one, to validate
    keyword argument values (which means we'll also need an equivalent
    predicate for positional args, and one for mixed positional and
    keyword args.)
    """
    if not exactly is False:
        if not ((atleast is False) and (atmost is False)):
            raise ValueError(
                "cannot mix 'exactly' and 'atleast' or 'atmost'")

        def _inkw (*args, **kwargs):
            return (len(kwargs) == len(exactly)
                    and all(kw in kwargs for kw in exactly))
        return _inkw

    if atleast is False and atmost is False:
        raise ValueError(
            "must specify 'exactly' or one or both of 'atleast' and 'atmost'")

    if atleast is False:
        atleast = ()
    atleast = frozenset(atleast)

    if atmost is False:
        def _inkw (*args, **kwargs):
            keys = frozenset(kwargs.keys())
            return keys >= atleast
        return _inkw

    atmost = frozenset(atmost)
    def _inkw (*args, **kwargs):
        keys = frozenset(kwargs.keys())
        return atleast <= keys <= atmost
    return _inkw


# Value predicates
# ----------------

def isempty (val):
    """
    `True` if ``val`` is empty. *Empty*, here, means zero-length, not
    'false-y'. I.e., :data:`False` and ``0`` are *not* empty, even
    though they are `false` in a boolean context.

    Use :func:`~operator.truth` and :func:`~operator.not_` for
    'standard' truth testing.
    """
    return issized(val) and len(val) == 0

def _contains (*contents):
    """
    Returns a `callable` which returns `True` if *each* member of
    ``contents`` is a member of its ``container`` argument.

    The signature of the returned callable is:

    .. function:: fn (container:Container) -> bool
    """

    # :func:`all` would return `True` with an empty `contents`
    if len(contents) == 0:
        return true_

    # no reason to call :func:`all` if we're only testing one value
    if len(contents) == 1:
        el = contents[0]
        def _contains (container):
            return el in container
        return _contains

    # otherwise, we need to check each element.
    def _contains (container):
        return all(el in container for el in contents)
    return _contains


# Type predicates
# ---------------

def _isa (classinfo, docstring=None):
    """
    A wrapper around :func:`isinstance` to swap the argument ordering,
    so it can be used as a partial.

    The signature of the returned `callable` is:

    .. function:: fn (obj) -> bool

    If `docstring` is supplied, it will become the docstring of the
    new `callable`. If `docstring` is :data:`None`, a docstring will
    be created based on `classinfo`.
    """
    def _isa (obj):
        return isinstance(obj, classinfo)

    # Make the docstring reflect what the new method does
    if docstring is None:
        name = getattr(classinfo, '__name__', None)
        if name:
            name = ":class:`%s`" % name
        else:
            if isiterable(classinfo):
                name = ('(' +
                        ", ".join(getattr(t, '__name__', str(t))
                                  for t in classinfo) +
                        ')')
            else:
                name = str(classinfo)
        docstring = "`True` if `obj` is an instance of %s" % name
    _isa.__doc__ = docstring

    return _isa

doctmpl = "`True` if `obj` %s."

iscallable  = _isa(Callable,        doctmpl % 'is `callable`')
iscontainer = _isa(Container,       doctmpl % 'is a `container`')
ishashable  = _isa(Hashable,        doctmpl % 'is `hashable`')
isiterable  = _isa(Iterable,        doctmpl % 'is `iterable`')
isiterator  = _isa(Iterator,        doctmpl % 'is an `iterator`')
ismap       = _isa(Mapping,         doctmpl % 'is a `mapping`')
ismmap      = _isa(MutableMapping,  doctmpl % 'is a mutable `mapping`')
ismapv      = _isa(MappingView,     doctmpl % 'is a `mapping view`')
isitemsv    = _isa(ItemsView,       doctmpl % 'is an `items view`')
iskeysv     = _isa(KeysView,        doctmpl % 'is a `keys view`')
isvalsv     = _isa(ValuesView,      doctmpl % 'is a `values view`')
isseq       = _isa(Sequence,        doctmpl % 'is a `sequence`')
ismseq      = _isa(MutableSequence, doctmpl % 'is a `mutable sequence`')
isset       = _isa(Set,             doctmpl % 'is a `set`')
ismset      = _isa(MutableSet,      doctmpl % 'is a `mutable set`')
issized     = _isa(Sized,           doctmpl % 'has a :meth:`~object.__len__` method')
isslice     = _isa(slice,           doctmpl % 'is a :func:`slice`')
islist      = _isa(list,            doctmpl % 'is a :func:`list`')
istuple     = _isa(tuple,           doctmpl % 'is a :func:`tuple`')
isstring    = _isa(basestring,      doctmpl % 'is a :func:`string <basestring>`')
isstr       = _isa(str,             doctmpl % 'is an :func:`str`')
isunicode   = _isa(unicode,         doctmpl % 'is a :func:`unicode string <unicode>`')

isbool      = _isa(bool,            doctmpl % 'is a :func:`bool`')
isint       = _isa(int,             doctmpl % 'is an :func:`int`')
islong      = _isa(long,            doctmpl % 'is a :func:`long`')
isfloat     = _isa(float,           doctmpl % 'is a :func:`float`')

def isnsiterable (obj):
    """`True` if `obj` is a non-string `iterable`"""
    return isiterable(obj) and not isstring(obj)

def isatom (val):
    """
    `True` if ``val`` looks 'atomic' (i.e., is a string, or any
    non-iterable). This is a naive test: any non-string iterable
    yields :data:`False`.
    """
    return not isnsiterable(val)


# Identity predicates
# -------------------

def _is (it, docstring=None):
    """
    A wrapper around :func:`~operator.is_` to set the docstring (which
    :func:`~functools.partial` does not).
    """
    def _is (obj):
        return obj is it

    # Make the docstring reflect what the new method does
    _is.__doc__ = (docstring or
                   ("`True` if `obj` is %s" %
                    getattr(it, '__name__', it)))
    return _is

isnone      = _is(None,             doctmpl % '*is* :data:`None`')
istrue      = _is(True,             doctmpl % '*is* :data:`True`')
isfalse     = _is(False,            doctmpl % '*is* :data:`False`')


# Helpers
# -------

def _apply (func):
    """
    Returns a `callable` which expands its `args` and `kwargs` into
    the `*args` and `**kwargs` of `func`. It's equivalent to
    ``partial(apply, func)``, except that :func:`apply` is
    deprecated.

    The signature of the returned callable is:

    .. function:: fn(args=(), kwargs={}) -> object

    Its principal use is to make predicates which operate on all of
    their arguments (i.e., `*args`) operate on *any* iterable. E.g.,
    ``_apply(_all(isstring))(['jack', 'kate'])`` is equivalent to
    ``_all(isstring)('jack', 'hurley')``.

    This is especially useful when testing the *contents* of arguments
    passed to a :func:`_zip` callable. E.g.,

    .. code-block:: python

       >>> int_and_strings = _zip(isint, _apply(_all(isstring)))
       >>> int_and_strings(42, ['jack', 'kate', 'sawyer'])
       True
    """
    def _apply (args=(), kwargs={}):
        return func(*args, **kwargs)
    return _apply

__cache_return = {}
def _return (val):
    """
    Always returns `val`.

    WHY?!? Because, sometimes you need a `callable` that's just a
    closure over ``return val``. E.g., in the 'no contents'
    special-case in :func:`_contains`.

    **NOTE:** This is one of the few memoized factories, because we
    don't want a proliferation of `_return(True)` and `_return(False)`
    helpers (of course, that's why we have :func:`true_` and
    :func:`false_`, but no matter).
    """
    if ishashable(val):
        if val not in __cache_return:
            def _return (*args, **kwargs):
                return val
            __cache_return[val] = _return
        return __cache_return[val]

    def _return (*args, **kwargs):
        return val
    return _return

true_ = _return(True)
false_ = _return(False)

def _nis (atleast=False, atmost=False, exactly=False):
    """
    Returns a `callable` which returns `True` if ``n`` is ``>=``
    `atleast`, ``<=`` `atmost`, or ``==`` `exactly`. See
    :func:`_nargs`, :func:`_nkw`, etc., for example use.

    The signature of the returned `callable` is:

    .. function:: fn (n:number) -> bool

    `atleast` and `atmost` may be combined, but `exactly` must stand
    alone.
    """
    if (atleast < 0) or (atmost < 0) or (exactly < 0):
        raise ValueError("arg limits cannot be negative")

    if not exactly is False:
        if not ((atleast is False) and (atmost is False)):
            raise ValueError(
                "cannot mix 'exactly' and 'atleast' or 'atmost'")
        def _nis_exactly (n):
            return n == exactly
        return _nis_exactly

    if atleast is False and atmost is False:
        raise ValueError(
            "must specify 'exactly' or one or both of 'atleast' and 'atmost'")

    if atleast is False:
        atleast = 0

    if atmost is False:
        atmost = float('inf')

    def _nis_between (n):
        return (atleast <= n <= atmost)
    return _nis_between

def _fnis (func, atleast=False, atmost=False, exactly=False):
    """
    Returns a `callable` which returns `True` if the result of
    ``func(*args, **kwargs)`` is ``>=`` `atleast` ``<=`` `atmost`, or
    ``==`` `exactly`. See :func:`_nargs`, :func:`_nkw`, etc., for
    example use.

    `atleast` and `atmost` may be combined, but `exactly` must stand
    alone.
    """
    __nis = _nis(atleast, atmost, exactly)
    def _fnis (*args, **kwargs):
        return __nis(func(*args, **kwargs))
    return _fnis
