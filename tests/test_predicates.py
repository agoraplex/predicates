from nose.tools import raises

from predicates import *

# ``import *`` doesn't import the underscore-prefixed names (will it
# fix things to put them into `__all__`?)
from predicates import (
    _apply,

    _and,
    _or,
    _not,
    _zip,
    _all,
    _any,
    _none,

    _args,
    _nis,
    _fnis,
    _nargs,
    _npos,
    _nkw,
    _inkw,

    _isa,
    _is,
    )


# test helpers
def fail (*args, **kwargs):
    raise Exception("should've short-circuited past this")

def true (*args, **kwargs):
    return True

def false (*args, **kwargs):
    return False

def passfail (val):
    """
    raise if ``failure`` is ``'fail'``, otherwise return
    ``val``.
    """
    if val == 'fail':
        fail()
    return val

class Thing (object):
    pass


class TestTypePredicates (object):
    def test_isa (self):
        assert _isa(type)(Thing)
        assert _isa(Thing)(Thing())
        assert _isa(''.__class__)("bad robot!")
        assert _isa((type, object))(Thing)
        assert _isa((type, object))(Thing())
        assert _isa((type, object))("bad robot!")

        assert not _isa(type)("bad robot!")

    def test_isa_docstring (self):
        assert _isa(type).__doc__ == "`True` if `obj` is an instance of :class:`type`"
        assert _isa((type, object)).__doc__ == "`True` if `obj` is an instance of (type, object)"
        assert _isa(type, 'foo').__doc__ == 'foo'
        assert _isa(type, docstring='foo').__doc__ == 'foo'

        # This is a bit of a roundabout hack to get coverage for an
        # extremely corner-ish corner case.
        class C (object): pass
        C.__name__ = ''
        assert _isa(C).__doc__ == "`True` if `obj` is an instance of <class 'test_predicates.'>"

    def test_isatom (self):
        assert isatom("bad robot!")
        assert isatom(u"bad robot!")
        assert isatom(1)
        assert not isatom(())
        assert not isatom((4, 8, 15, 16, 23, 42))
        assert not isatom([4, 8, 15, 16, 23, 42])

    def test_isnsiterable (self):
        assert isnsiterable(())
        assert isnsiterable([])
        assert not isnsiterable("bad robot!")
        assert not isnsiterable(u"bad robot!")


class TestIdentityPredicates (object):
    def test_is (self):
        assert _is(None)(None)
        assert _isa(Thing)(Thing())
        assert _isa(''.__class__)("bad robot!")

    def test_isa_docstring (self):
        assert _isa(type).__doc__ == "`True` if `obj` is an instance of :class:`type`"
        assert _isa(type, 'foo').__doc__ == 'foo'
        assert _isa(type, docstring='foo').__doc__ == 'foo'

    def test_isempty (self):
        assert isempty(())
        assert isempty([])
        assert isempty('')
        assert isempty({})

        assert not isempty((1,))
        assert not isempty(' ')
        assert not isempty(None)
        assert not isempty(0)
        assert not isempty(False)


class TestApplyHelper (object):
    def test_apply (self):
        # args
        assert _apply(isint)([42,])
        assert _apply(_all(isstring))(['jack', 'sawyer'])
        assert _zip(isint, _apply(_all(isstring)))(42, ['jack', 'sawyer'])

        # args + kwargs
        assert _apply(_npos(exactly=2)([42, "bad robot!"],
                                       {'jack': 4, 'kate': 15}))
        assert _apply(_nkw(exactly=2)([42, "bad robot!"],
                                      {'jack': 4, 'kate': 15}))
        assert _apply(_nargs(exactly=4)([42, "bad robot!"],
                                        {'jack': 4, 'kate': 15}))

        # recursive (yeah, it makes my brain hurt, too...) It's
        # actually pretty simple, though...  It's equivalent to
        # _and(isstring)(chain(people)) (in other words, it's a
        # completely contrived example which is much more cleanly
        # solved in another way! :-))

        # apply `isstring` to each element in an iterable. I.e.,
        # ``_apply(_all(isstring))(['jack', 'hurley'])`` is equivalent
        # to ``_all(isstring)('jack', 'hurley')
        all_strings = _apply(_all(isstring))

        # make two groups of people, then combine them
        group_1 = ['jack', 'sawyer']
        group_2 = ['kate', 'hurley']
        people = (group_1, group_2)

        assert _apply(_zip(all_strings, all_strings))(people)

    @raises(TypeError)
    def test_apply_noniterable (self):
        # this doesn't do what you think...
        _apply(isint)(42)

    @raises(TypeError)
    def test_apply_too_many_args_for_predicate (self):
        _apply(isint)([23, 42])

    @raises(TypeError)
    def test_apply_unexpected_kwargs (self):
        _apply(isstring)(["bad robot!"], {'jack': 4, 'kate': 15})


class TestCompositePredicates (object):
    def test_not (self):
        # no predicates
        assert _not()(True)

        # single predicate
        assert _not(isfalse)(True)
        assert _not(istrue)(False)
        assert not _not(isempty)('')

        # multiple predicates
        assert _not(isfalse, isstring)(True)
        assert _not(istrue, isstring)(False)
        assert not _not(isempty, isfalse)('')
        assert not _not(istrue, isstring)(True)

    def test_and (self):
        # no predicates
        assert _and()(True)

        # single predicate
        assert _and(isempty)('')
        assert _and(istrue)(True)
        assert not _and(isfalse)(True)
        assert not _and(istrue)(False)

        # multiple predicates
        assert _and(isempty, not_)('')
        assert not _and(isfalse, isstring)(False)
        assert not _and(isfalse, isstring)(True)
        assert not _and(istrue, isstring)(False)

    def test_or (self):
        # no predicates
        assert not _or()(True)

        # single predicate
        assert _or(isempty)('')
        assert _or(not_)(0)
        assert not _or(isfalse)(True)
        assert not _or(istrue)(False)

        # multiple predicates
        assert _or(isempty, not_)(0)
        assert _or(isfalse, isstring)('')
        assert not _or(isfalse, isstring)(True)

    def test_zip (self):
        # no predicates
        assert _zip()()
        assert _zip()(jack=4, kate=16)
        assert _zip()(4, 8, 15, 16, 23, 42)
        assert _zip()(4, 8, 15, hurley=16, locke=23)

        # len(predicates) == len(args)
        assert _zip(isstring, isempty, isnsiterable)(
            "bad robot!", (), (4, 8))
        assert _zip(isstring, isempty, isnsiterable)(
            "bad robot!", (), (4, 8), kate=15, hurley=16)

        assert not _zip(isstring, isempty, isnsiterable)(
            "bad robot!", (4, 8), ())
        assert not _zip(isstring, isempty, isnsiterable)(
            "bad robot!", (4, 8), (), kate=15, hurley=16)

        # len(predicates) != len(args)
        assert _zip(isstring)("bad robot!", (), (4, 8))
        assert _zip(isstring)("bad robot!", (), (4, 8),
                              kate=15, hurley=16)

        assert _zip(isstring, isempty)("bad robot!", (), (4, 8))
        assert _zip(isstring, isempty)("bad robot!", (), (4, 8),
                                       kate=15, hurley=16)

        assert not _zip(isstring)((), (4, 8))
        assert not _zip(isstring)((), (4, 8), kate=15, hurley=16)
        assert not _zip(isstring, isempty)("bad robot!", (4, 8), ())
        assert not _zip(isstring, isempty)("bad robot!", (4, 8), (),
                                           kate=15, hurley=16)

    def test_composition (self):
        assert not _and(_not(isstring), _or(isempty, isatom))('')
        assert _and(_not(isstring), _or(isempty, isatom))(())
        assert _and(_not(isstring), _or(isempty, isatom))(42)

    def test_short_circuit (self):
        assert _any(passfail)(True, 'fail')
        assert not _all(passfail)(False, 'fail')
        assert not _none(passfail)(True, 'fail')


class TestApplicationPredicates (object):
    def test_all (self):
        # no args
        assert _all(istrue)()

        # single arg
        assert _all(istrue)(True)
        assert _all(isstring)("bad robot!")
        assert not _all(isfalse)(True)

        # multiple args
        assert _all(istrue)(True, True)
        assert _all(isstring)("bad robot!", "I made this!")
        assert not _all(isfalse)(False, True)

    def test_any (self):
        # no args
        assert not _any(istrue)()

        # single arg
        assert _any(istrue)(True)
        assert _any(isstring)("bad robot!")
        assert not _any(isfalse)(True)

        # multiple args
        assert _any(istrue)(False, True)
        assert _any(isstring)(42, "bad robot!")
        assert not _any(isfalse)(0, True)

    def test_none (self):
        # no args
        assert _none(istrue)()
        assert _none(isfalse)()
        assert _none(truth)()
        assert _none(not_)()
        assert _none(isempty)()

        # single arg
        assert _none(istrue)(False)
        assert _none(isstring)(42)
        assert not _none(isfalse)(False)

        # multiple args
        assert _none(istrue)(False, 42)
        assert _none(isstring)(23, 42)
        assert not _none(isfalse)(0, True, False)
        assert not _none(isstring)((), "bad robot!")

    def test_composition (self):
        assert _all(_or(isempty, isatom))('', (), 42)
        assert not _all(_or(isempty, isatom))('', (), (42,))

    def test_short_circuit (self):
        assert not _and(false, fail)()
        assert _or(true, fail)()
        assert not _not(true, fail)()


class TestNumericRangePredicates (object):
    @raises(ValueError)
    def test_nis_bad_spec (self):
        _nis(atleast=1, exactly=2)

    @raises(ValueError)
    def test_nis_no_spec (self):
        _nis()

    @raises(ValueError)
    def test_nis_bad_negative (self):
        _nis(atleast=-1)

    def test_nis_atleast (self):
        assert _nis(atleast=0)(0)
        assert _nis(atleast=0)(1)
        assert _nis(atleast=2)(2)

        assert not _nis(atleast=1)(0)
        assert not _nis(atleast=2)(1)

    def test_nis_atmost (self):
        assert _nis(atmost=0)(0)
        assert _nis(atmost=1)(0)
        assert _nis(atmost=1)(1)

        assert not _nis(atmost=0)(1)
        assert not _nis(atmost=1)(2)

    def test_nis_between (self):
        assert _nis(atleast=0, atmost=1)(0)
        assert _nis(atleast=0, atmost=1)(1)
        assert _nis(atleast=1, atmost=2)(1)
        assert _nis(atleast=1, atmost=2)(2)
        assert _nis(atleast=1, atmost=3)(2)
        assert _nis(atleast=2, atmost=3)(2)
        assert _nis(atleast=2, atmost=3)(3)

        assert not _nis(atleast=1, atmost=2)(0)
        assert not _nis(atleast=1, atmost=2)(3)

    def test_nis_exactly (self):
        assert _nis(exactly=0)(0)
        assert _nis(exactly=1)(1)
        assert _nis(exactly=2)(2)

        assert not _nis(exactly=0)(1)
        assert not _nis(exactly=1)(2)
        assert not _nis(exactly=2)(1)

    @raises(ValueError)
    def test_fnis_bad_spec (self):
        _fnis(lambda: 0, atleast=1, exactly=2)

    @raises(ValueError)
    def test_fnis_bad_negative (self):
        _fnis(lambda: 0, atleast=-1)

    def test_fnis_atleast (self):
        assert _fnis(lambda: 0, atleast=0)()
        assert _fnis(lambda: 1, atleast=0)()
        assert _fnis(lambda: 2, atleast=2)()

        assert not _fnis(lambda: 0, atleast=1)()
        assert not _fnis(lambda: 1, atleast=2)()

    def test_fnis_atmost (self):
        assert _fnis(lambda: 0, atmost=0)()
        assert _fnis(lambda: 0, atmost=1)()
        assert _fnis(lambda: 1, atmost=1)()

        assert not _fnis(lambda: 1, atmost=0)()
        assert not _fnis(lambda: 2, atmost=1)()

    def test_fnis_between (self):
        assert _fnis(lambda: 0, atleast=0, atmost=1)()
        assert _fnis(lambda: 1, atleast=0, atmost=1)()
        assert _fnis(lambda: 1, atleast=1, atmost=2)()
        assert _fnis(lambda: 2, atleast=1, atmost=2)()
        assert _fnis(lambda: 2, atleast=1, atmost=3)()
        assert _fnis(lambda: 2, atleast=2, atmost=3)()
        assert _fnis(lambda: 3, atleast=2, atmost=3)()

        assert not _fnis(lambda: 0, atleast=1, atmost=2)()
        assert not _fnis(lambda: 3, atleast=1, atmost=2)()

    def test_fnis_exactly (self):
        assert _fnis(lambda: 0, exactly=0)()
        assert _fnis(lambda: 1, exactly=1)()
        assert _fnis(lambda: 2, exactly=2)()

        assert not _fnis(lambda: 1, exactly=0)()
        assert not _fnis(lambda: 2, exactly=1)()
        assert not _fnis(lambda: 1, exactly=2)()


class TestArgCountPredicates (object):
    @raises(ValueError)
    def test_nargs_bad_spec (self):
        _nargs(atleast=1, exactly=2)

    @raises(ValueError)
    def test_nargs_bad_negative (self):
        _nargs(atleast=-1)

    def test_nargs_atleast_args (self):
        assert _nargs(atleast=0)()
        assert _nargs(atleast=0)(4)
        assert _nargs(atleast=0)(4, 8)
        assert _nargs(atleast=1)(4, 8)
        assert _nargs(atleast=2)(4, 8)

        assert not _nargs(atleast=1)()
        assert not _nargs(atleast=2)(1)

    def test_nargs_atmost_args (self):
        assert _nargs(atmost=0)()
        assert _nargs(atmost=1)()
        assert _nargs(atmost=2)(4, 8)
        assert _nargs(atmost=3)(4, 8)

        assert not _nargs(atmost=0)(4, 8)
        assert not _nargs(atmost=1)(4, 8)

    def test_nargs_between_args (self):
        assert _nargs(atleast=0, atmost=1)()
        assert _nargs(atleast=0, atmost=1)(4)
        assert _nargs(atleast=1, atmost=2)(4, 8)
        assert _nargs(atleast=1, atmost=3)(4, 8)
        assert _nargs(atleast=2, atmost=3)(4, 8)
        assert _nargs(atleast=2, atmost=3)(4, 8, 15)

        assert not _nargs(atleast=1, atmost=2)()
        assert not _nargs(atleast=1, atmost=2)(4, 8, 15)

    def test_nargs_exactly_args (self):
        assert _nargs(exactly=0)()
        assert _nargs(exactly=1)(4)
        assert _nargs(exactly=2)(4, 8)

        assert not _nargs(exactly=0)(4)
        assert not _nargs(exactly=1)(4, 8)
        assert not _nargs(exactly=2)(4)

    def test_nargs_atleast_kw (self):
        assert _nargs(atleast=0)(jack=4)
        assert _nargs(atleast=0)(jack=4, sawyer=8)
        assert _nargs(atleast=1)(jack=4, sawyer=8)
        assert _nargs(atleast=2)(jack=4, sawyer=8)

        assert not _nargs(atleast=1)()
        assert not _nargs(atleast=2)(1)

    def test_nargs_atmost_kw (self):
        assert _nargs(atmost=2)(jack=4, sawyer=8)
        assert _nargs(atmost=3)(jack=4, sawyer=8)

        assert not _nargs(atmost=0)(jack=4, sawyer=8)
        assert not _nargs(atmost=1)(jack=4, sawyer=8)

    def test_nargs_between_kw (self):
        assert _nargs(atleast=0, atmost=1)(jack=4)
        assert _nargs(atleast=1, atmost=2)(jack=4, sawyer=8)
        assert _nargs(atleast=1, atmost=3)(jack=4, sawyer=8)
        assert _nargs(atleast=2, atmost=3)(jack=4, sawyer=8)
        assert _nargs(atleast=2, atmost=3)(jack=4, sawyer=8, hurley=15)

        assert not _nargs(atleast=1, atmost=2)(jack=4, sawyer=8, hurley=15)

    def test_nargs_exactly_kw (self):
        assert _nargs(exactly=1)(jack=4)
        assert _nargs(exactly=2)(jack=4, sawyer=8)

        assert not _nargs(exactly=0)(jack=4)
        assert not _nargs(exactly=1)(jack=4, sawyer=8)
        assert not _nargs(exactly=2)(jack=4)

    def test_nargs_atleast_both (self):
        assert _nargs(atleast=0)(4, sawyer=8)
        assert _nargs(atleast=1)(4, sawyer=8)
        assert _nargs(atleast=2)(4, sawyer=8)

        assert not _nargs(atleast=3)(4, sawyer=8)

    def test_nargs_atmost_both (self):
        assert _nargs(atmost=2)(4, sawyer=8)
        assert _nargs(atmost=3)(4, sawyer=8)

        assert not _nargs(atmost=0)(4, sawyer=8)
        assert not _nargs(atmost=1)(4, sawyer=8)

    def test_nargs_between_both (self):
        assert _nargs(atleast=1, atmost=2)(4, sawyer=8)
        assert _nargs(atleast=1, atmost=3)(4, sawyer=8)
        assert _nargs(atleast=2, atmost=3)(4, sawyer=8)
        assert _nargs(atleast=2, atmost=3)(4, 8, hurley=15)

        assert not _nargs(atleast=1, atmost=2)(4, 8, hurley=15, kate=16)

    def test_nargs_exactly_both (self):
        assert _nargs(exactly=2)(4, sawyer=8)

        assert not _nargs(exactly=0)(4, sawyer=8)
        assert not _nargs(exactly=1)(4, sawyer=8)
        assert not _nargs(exactly=3)(4, sawyer=8)


class TestArgContentPredicates (object):
    @raises(ValueError)
    def test_args_call_none (self):
        _args()()

    def test_args_call_pos (self):
        assert _args(isstring)()
        assert _args(isstring)('dharma')
        assert _args(isstring)('dharma', 'miles')

        assert not _args(isstring)(4, "bad robot!")

        assert _and(_args(isstring),
                    _args(_not(isempty)))('jack', 'sawyer')
        assert not _and(_args(isstring),
                        _args(_not(isempty)))('jack', 'sawyer', '')

    def test_args_call_kw (self):
        assert _args(ricardo=isstring)(ricardo='#2')
        assert _args(ricardo=isstring)(ricardo='#2', hurley=16)
        assert _args(ricardo=isstring, hurley=isint)(ricardo='#2', hurley=16)

        assert _args(ricardo=isstring)(4, 8, ricardo='#2')
        assert _args(ricardo=isstring)(4, 8, ricardo='#2', hurley=16)
        assert _args(ricardo=isstring, hurley=isint)(4, 8, ricardo='#2', hurley=16)

        assert not _args(ricardo=isstring)()
        assert not _args(ricardo=isstring)(ricardo=2)
        assert not _args(ricardo=isstring)(ricardo=2, hurley=16)
        assert not _args(ricardo=isstring, hurley=isint)(ricardo=2, hurley=16)

        assert not _args(ricardo=isstring)(4, 8, ricardo=2)
        assert not _args(ricardo=isstring)(4, 8, ricardo=2, hurley=16)
        assert not _args(ricardo=isstring, hurley=isint)(4, 8, ricardo=2, hurley=16)

    def test_args_call_pos_and_kw (self):
        assert _args(isint, ricardo=isstring)(ricardo='#2')
        assert _args(isint, ricardo=isstring)(4, 8, ricardo='#2', hurley=16)
        assert _args(isint, ricardo=isstring, hurley=isint)(4, 8, ricardo='#2', hurley=16)

        assert not _args(isint, ricardo=isstring)()
        assert not _args(isint, ricardo=isstring)(ricardo=2)
        assert not _args(isint, ricardo=isstring)(4, 8, ricardo=2, hurley=16)
        assert not _args(isint, ricardo=isstring)(4, 8, 'kate', ricardo='#2', hurley=16)
        assert not _args(isint, ricardo=isstring, hurley=isint)(4, 8, ricardo=2, hurley=16)

    def test_args_mix_call_idx (self):
        assert _args[0](isstring, ricardo=isstring)("bad robot!", 4, 8, ricardo='#2')
        assert _args[-1](isint, ricardo=isstring)(4, (), 8, ricardo='#2')
        assert _and(_args[0](isstring),
                    _args[1](isnone))("bad robot!", None)

        assert not _args[0](isint, ricardo=isstring)("bad robot!", ricardo='#2')
        assert not _args[0](isint, ricardo=isstring)(4, "bad robot!", ricardo=2)

    def test_args_idx (self):
        assert _args[0](isstring)("bad robot!", 4, 8)
        assert _args[-1](isint)(4, (), 8)
        assert _and(_args[0](isstring),
                    _args[1](isnone))("bad robot!", None)

        assert not _args[0](isstring)(4, "bad robot!")

    def test_args_idx_slice (self):
        assert _args[:](isstring)()
        assert _args[:](isstring)('dharma')
        assert _args[:](isstring)('dharma', 'miles')
        assert _args[:2](isstring)('dharma', 'miles')
        assert _args[0:1](isstring)("bad robot!", 4, 8)
        assert _args[2:4](isstring)(4, 8, 'linus', 'juliet')
        assert _args[2:](isstring)(4, 8, 'linus', 'juliet')
        assert _args[1::2](isstring)(4, 'linus', 8, 'juliet', 15, 'hurley', 16)
        assert _args[1:2](isiterable)(4, (), 8)
        assert _args[:-1](isint)(4, 8, ())
        assert _args[-3:-1](isint)(4, 8, ())

        assert not _args[0:1](isstring)(4, "bad robot!")
        assert not _args[:](isstring)('dharma', 4, 8, 15, 16, 23, 42)

        assert _and(_args[0:1](isstring),
                    _args[1:2](isnone))("bad robot!", None)

    # ___TODO:___ string keys for `_args[...]`
    def todo_args_string (self):
        pass

    def todo_args_string_slice (self):
        pass

    # ___TODO:___ multi-dimensional slices for `_args[...]`
    def todo_args_multi_idx (self):
        pass

    def todo_args_multi_idx_slice (self):
        pass

    def todo_args_multi_string (self):
        pass

    def todo_args_multi_string_slice (self):
        pass

    def todo_args_multi_mixed (self):
        pass


class TestPositionalArgCountPredicates (object):
    @raises(ValueError)
    def test_npos_bad_spec (self):
        _npos(atleast=1, exactly=2)

    @raises(ValueError)
    def test_npos_bad_negative (self):
        _npos(atleast=-1)

    def test_npos_atleast_args (self):
        assert _npos(atleast=0)()
        assert _npos(atleast=0)(4)
        assert _npos(atleast=0)(4, 8)
        assert _npos(atleast=1)(4, 8)
        assert _npos(atleast=2)(4, 8)

        assert not _npos(atleast=1)()
        assert not _npos(atleast=2)(1)

    def test_npos_atmost_args (self):
        assert _npos(atmost=0)()
        assert _npos(atmost=1)()
        assert _npos(atmost=2)(4, 8)
        assert _npos(atmost=3)(4, 8)

        assert not _npos(atmost=0)(4, 8)
        assert not _npos(atmost=1)(4, 8)

    def test_npos_between_args (self):
        assert _npos(atleast=0, atmost=1)()
        assert _npos(atleast=0, atmost=1)(4)
        assert _npos(atleast=1, atmost=2)(4, 8)
        assert _npos(atleast=1, atmost=3)(4, 8)
        assert _npos(atleast=2, atmost=3)(4, 8)
        assert _npos(atleast=2, atmost=3)(4, 8, 15)

        assert not _npos(atleast=1, atmost=2)()
        assert not _npos(atleast=1, atmost=2)(4, 8, 15)

    def test_npos_exactly_args (self):
        assert _npos(exactly=0)()
        assert _npos(exactly=1)(4)
        assert _npos(exactly=2)(4, 8)

        assert not _npos(exactly=0)(4)
        assert not _npos(exactly=1)(4, 8)
        assert not _npos(exactly=2)(4)

    def test_npos_atleast_both (self):
        assert _npos(atleast=0)(4, sawyer=8)
        assert _npos(atleast=1)(4, sawyer=8)
        assert _npos(atleast=2)(4, 8, hurley=15)

        assert not _npos(atleast=3)(4, 8, hurley=15)

    def test_npos_atmost_both (self):
        assert _npos(atmost=2)(4, sawyer=8)
        assert _npos(atmost=3)(4, 8, hurley=15)

        assert not _npos(atmost=0)(4, sawyer=8)
        assert not _npos(atmost=1)(4, 8, hurley=15)

    def test_npos_between_both (self):
        assert _npos(atleast=1, atmost=2)(4, 8, hurley=15)
        assert _npos(atleast=1, atmost=3)(4, 8, 15, kate=16)
        assert _npos(atleast=2, atmost=3)(4, 8, hurley=15)
        assert _npos(atleast=2, atmost=3)(4, 8, 15, kate=16)

        assert not _npos(atleast=1, atmost=2)(4, 8, 15, kate=16)

    def test_npos_exactly_both (self):
        assert _npos(exactly=2)(4, 8, sawyer=8)

        assert not _npos(exactly=0)(4, sawyer=8)
        assert not _npos(exactly=1)(4, 8, hurley=15)
        assert not _npos(exactly=3)(4, sawyer=8)


class TestKeywordArgCountPredicates (object):
    @raises(ValueError)
    def test_nkw_bad_spec (self):
        _nkw(atleast=1, exactly=2)

    @raises(ValueError)
    def test_nkw_bad_negative (self):
        _nkw(atleast=-1)

    def test_nkw_atleast_kw (self):
        assert _nkw(atleast=0)()
        assert _nkw(atleast=0)(jack=4)
        assert _nkw(atleast=0)(jack=4, sawyer=8)
        assert _nkw(atleast=1)(jack=4, sawyer=8)
        assert _nkw(atleast=2)(jack=4, sawyer=8)

        assert not _nkw(atleast=1)()
        assert not _nkw(atleast=2)(1)

    def test_nkw_atmost_kw (self):
        assert _nkw(atmost=0)()
        assert _nkw(atmost=1)()
        assert _nkw(atmost=2)(jack=4, sawyer=8)
        assert _nkw(atmost=3)(jack=4, sawyer=8)

        assert not _nkw(atmost=0)(jack=4, sawyer=8)
        assert not _nkw(atmost=1)(jack=4, sawyer=8)

    def test_nkw_between_kw (self):
        assert _nkw(atleast=0, atmost=1)()
        assert _nkw(atleast=0, atmost=1)(jack=4)
        assert _nkw(atleast=1, atmost=2)(jack=4, sawyer=8)
        assert _nkw(atleast=1, atmost=3)(jack=4, sawyer=8)
        assert _nkw(atleast=2, atmost=3)(jack=4, sawyer=8)
        assert _nkw(atleast=2, atmost=3)(jack=4, sawyer=8, hurley=15)

        assert not _nkw(atleast=1, atmost=2)()
        assert not _nkw(atleast=1, atmost=2)(jack=4, sawyer=8, hurley=15)

    def test_nkw_exactly_kw (self):
        assert _nkw(exactly=0)()
        assert _nkw(exactly=1)(jack=4)
        assert _nkw(exactly=2)(jack=4, sawyer=8)

        assert not _nkw(exactly=0)(jack=4)
        assert not _nkw(exactly=1)()
        assert not _nkw(exactly=1)(jack=4, sawyer=8)
        assert not _nkw(exactly=2)(jack=4)

    def test_nkw_atleast_both (self):
        assert _nkw(atleast=0)(4)
        assert _nkw(atleast=0)(4, sawyer=8)
        assert _nkw(atleast=1)(4, sawyer=8)
        assert _nkw(atleast=2)(4, sawyer=8, hurley=15)

        assert not _nkw(atleast=1)(4)
        assert not _nkw(atleast=3)(4, sawyer=8)

    def test_nkw_atmost_both (self):
        assert _nkw(atmost=0)(4)
        assert _nkw(atmost=2)(4)
        assert _nkw(atmost=2)(4, sawyer=8)
        assert _nkw(atmost=2)(4, sawyer=8, hurley=15)

        assert not _nkw(atmost=0)(4, sawyer=8)
        assert not _nkw(atmost=1)(4, sawyer=8, hurley=15)

    def test_nkw_between_both (self):
        assert _nkw(atleast=1, atmost=2)(4, sawyer=8)
        assert _nkw(atleast=1, atmost=3)(4, sawyer=8, hurley=15)
        assert _nkw(atleast=2, atmost=3)(4, sawyer=8, hurley=15)
        assert _nkw(atleast=2, atmost=3)(4, 8, hurley=15, kate=16, locke=23)

        assert not _nkw(atleast=1, atmost=2)(4, 8, hurley=15, kate=16, locke=23)

    def test_nkw_exactly_both (self):
        assert _nkw(exactly=2)(4, sawyer=8, hurley=15)

        assert not _nkw(exactly=0)(4, sawyer=8)
        assert not _nkw(exactly=1)(4)
        assert not _nkw(exactly=1)(4, sawyer=8, hurley=15)
        assert not _nkw(exactly=3)(4, sawyer=8)

    @raises(ValueError)
    def test_nkw_bad_spec (self):
        _nkw(atleast=1, exactly=2)

    @raises(ValueError)
    def test_nkw_bad_negative (self):
        _nkw(atleast=-1)

    def test_nkw_atleast_kw (self):
        assert _nkw(atleast=0)()
        assert _nkw(atleast=0)(jack=4)
        assert _nkw(atleast=0)(jack=4, sawyer=8)
        assert _nkw(atleast=1)(jack=4, sawyer=8)
        assert _nkw(atleast=2)(jack=4, sawyer=8)

        assert not _nkw(atleast=1)()
        assert not _nkw(atleast=2)(1)

    def test_nkw_atmost_kw (self):
        assert _nkw(atmost=0)()
        assert _nkw(atmost=1)()
        assert _nkw(atmost=2)(jack=4, sawyer=8)
        assert _nkw(atmost=3)(jack=4, sawyer=8)

        assert not _nkw(atmost=0)(jack=4, sawyer=8)
        assert not _nkw(atmost=1)(jack=4, sawyer=8)

    def test_nkw_between_kw (self):
        assert _nkw(atleast=0, atmost=1)()
        assert _nkw(atleast=0, atmost=1)(jack=4)
        assert _nkw(atleast=1, atmost=2)(jack=4, sawyer=8)
        assert _nkw(atleast=1, atmost=3)(jack=4, sawyer=8)
        assert _nkw(atleast=2, atmost=3)(jack=4, sawyer=8)
        assert _nkw(atleast=2, atmost=3)(jack=4, sawyer=8, hurley=15)

        assert not _nkw(atleast=1, atmost=2)()
        assert not _nkw(atleast=1, atmost=2)(jack=4, sawyer=8, hurley=15)

    def test_nkw_exactly_kw (self):
        assert _nkw(exactly=0)()
        assert _nkw(exactly=1)(jack=4)
        assert _nkw(exactly=2)(jack=4, sawyer=8)

        assert not _nkw(exactly=0)(jack=4)
        assert not _nkw(exactly=1)()
        assert not _nkw(exactly=1)(jack=4, sawyer=8)
        assert not _nkw(exactly=2)(jack=4)

    def test_nkw_atleast_both (self):
        assert _nkw(atleast=0)(4)
        assert _nkw(atleast=0)(4, sawyer=8)
        assert _nkw(atleast=1)(4, sawyer=8)
        assert _nkw(atleast=2)(4, sawyer=8, hurley=15)

        assert not _nkw(atleast=1)(4)
        assert not _nkw(atleast=3)(4, sawyer=8)

    def test_nkw_atmost_both (self):
        assert _nkw(atmost=0)(4)
        assert _nkw(atmost=2)(4)
        assert _nkw(atmost=2)(4, sawyer=8)
        assert _nkw(atmost=2)(4, sawyer=8, hurley=15)

        assert not _nkw(atmost=0)(4, sawyer=8)
        assert not _nkw(atmost=1)(4, sawyer=8, hurley=15)

    def test_nkw_between_both (self):
        assert _nkw(atleast=1, atmost=2)(4, sawyer=8)
        assert _nkw(atleast=1, atmost=3)(4, sawyer=8, hurley=15)
        assert _nkw(atleast=2, atmost=3)(4, sawyer=8, hurley=15)
        assert _nkw(atleast=2, atmost=3)(4, 8, hurley=15, kate=16, locke=23)

        assert not _nkw(atleast=1, atmost=2)(4, 8, hurley=15, kate=16, locke=23)

    def test_nkw_exactly_both (self):
        assert _nkw(exactly=2)(4, sawyer=8, hurley=15)

        assert not _nkw(exactly=0)(4, sawyer=8)
        assert not _nkw(exactly=1)(4)
        assert not _nkw(exactly=1)(4, sawyer=8, hurley=15)
        assert not _nkw(exactly=3)(4, sawyer=8)


class TestKeywordArgPresencePredicates (object):
    @raises(ValueError)
    def test_inkw_bad_spec_atleast_exactly (self):
        _inkw(atleast={}, exactly={})

    @raises(ValueError)
    def test_inkw_bad_spec_atmost_exactly (self):
        _inkw(atmost={}, exactly={})

    @raises(ValueError)
    def test_inkw_no_spec (self):
        _inkw()

    def test_inkw_atleast_tuple (self):
        assert _inkw(atleast=())()
        assert _inkw(atleast=())(4, 8)
        assert _inkw(atleast=())(jack=True, kate=True)
        assert _inkw(atleast=('jack', 'kate'))(jack=True, kate=True)
        assert _inkw(atleast=('jack', 'kate'))(jack=True, kate=True, sawyer=True)
        assert _inkw(atleast=('jack', 'kate'))(4, 8, jack=True, kate=True, sawyer=True)
        assert _inkw(atleast=('jack',))(jack=True, kate=True)

        assert not _inkw(atleast=('sawyer', 'kate'))(jack=True, kate=True)

    def test_inkw_atleast_dict (self):
        assert _inkw(atleast={})(jack=True, kate=True)
        assert _inkw(atleast={'jack': 4, 'kate': 8})(jack=True, kate=True)
        assert _inkw(atleast={'jack': 4})(jack=True, kate=True)

        assert not _inkw(atleast={'sawyer': 16, 'kate': 8})(jack=True, kate=True)

    def test_inkw_atmost_tuple (self):
        assert _inkw(atmost=())()
        assert _inkw(atmost=())(4, 8)
        assert _inkw(atmost=('jack',))()
        assert _inkw(atmost=('jack',))(4, 8)
        assert _inkw(atmost=('jack', 'kate'))(jack=True)
        assert _inkw(atmost=('jack', 'kate'))(jack=True, kate=True)

        assert not _inkw(atmost=())(jack=True, kate=True)
        assert not _inkw(atmost=('sawyer', 'kate'))(jack=True, kate=True)
        assert not _inkw(atmost=('jack', 'kate'))(jack=True, kate=True, sawyer=True)
        assert not _inkw(atmost=('jack', 'kate'))(4, 8, jack=True, kate=True, sawyer=True)

    def test_inkw_atmost_dict (self):
        assert _inkw(atmost={})()
        assert _inkw(atmost={})(4, 8)
        assert _inkw(atmost={'jack': 4, 'kate': 8})()
        assert _inkw(atmost={'jack': 4, 'kate': 8})(jack=True, kate=True)

        assert not _inkw(atmost={})(jack=True, kate=True)
        assert not _inkw(atmost={'jack': 4})(jack=True, kate=True)
        assert not _inkw(atmost={'sawyer': 16, 'kate': 8})(jack=True, kate=True)
        assert not _inkw(atmost={'jack': 4, 'kate': 8})(jack=True, kate=True, sawyer=True)
        assert not _inkw(atmost={'jack': 4, 'kate': 8})(4, 8, jack=True, kate=True, sawyer=True)

    def test_inkw_exactly_tuple (self):
        assert _inkw(exactly=())()
        assert _inkw(exactly=())(4, 8)
        assert _inkw(exactly=('jack', 'kate'))(jack=True, kate=True)
        assert _inkw(exactly=('jack', 'kate'))(4, 8, jack=True, kate=True)

        assert not _inkw(exactly=())(jack=True, kate=True)
        assert not _inkw(exactly=())(4, 8, jack=True, kate=True)
        assert not _inkw(exactly=('jack',))(jack=True, kate=True)
        assert not _inkw(exactly=('sawyer', 'kate'))(jack=True, kate=True)
        assert not _inkw(exactly=('jack', 'kate'))(jack=True, kate=True, sawyer=True)

    def test_inkw_exactly_dict (self):
        assert _inkw(exactly={})()
        assert _inkw(exactly={})(4, 8)
        assert _inkw(exactly={'jack': 4, 'kate': 8})(jack=True, kate=True)
        assert _inkw(exactly={'jack': 4, 'kate': 8})(4, 8, jack=True, kate=True)

        assert not _inkw(exactly={})(jack=True, kate=True)
        assert not _inkw(exactly={})(4, 8, jack=True, kate=True)
        assert not _inkw(exactly={'jack': 4})(jack=True, kate=True)
        assert not _inkw(exactly={'sawyer': 16, 'kate': 8})(jack=True, kate=True)
        assert not _inkw(exactly={'jack': 4, 'kate': 8})(jack=True, kate=True, sawyer=True)
