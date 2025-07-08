from hypothesis import assume, given, strategies as st
import pytest

from xfp import Xdict, Xlist, Xtry
from xfp.functions import tupled2

st_dict = st.dictionaries(st.text(), st.integers())
st_xdict = st.builds(Xdict, st_dict)


def test_xdict_should_be_iterable() -> None:
    input = Xdict({"a": 1})
    iterable = iter(input)

    assert next(iterable) == ("a", 1)


@given(st_xdict)
def test_len_should_return_the_number_of_keys(xdict) -> None:
    assert len(xdict) == len(xdict.keys())


def test_contains_should_be_true_if_key_is_in_keyset() -> None:
    assert "a" in Xdict({"a": 1})


def test_contains_should_be_false_otherwise() -> None:
    assert "a" not in Xdict({"b": 1})


def test_contains_should_be_false_if_uncomparable() -> None:
    assert 34 not in Xdict({"b": 1})


def test_getitem_should_return_the_value_associated() -> None:
    input = Xdict({"a": 1})
    assert input["a"] == 1


def test_get_should_return_the_value_associated() -> None:
    input = Xdict({"a": 1})
    assert input.get("a") == 1


def test_get_should_return_a_default_value_if_not_found() -> None:
    input = Xdict({"a": 1})
    assert input.get("b", 2) == 2


def test_get_should_raise_index_error_if_default_not_set() -> None:
    input = Xdict({"a": 1})
    with pytest.raises(IndexError):
        input.get("b")


def test_get_should_raise_attribute_error_if_called_inappropriately() -> None:
    input = Xdict({"a": 1})
    with pytest.raises(AttributeError):
        input.get("b", 1, 2, 3)  # type: ignore


def test_get_fr_should_wrap_success() -> None:
    input = Xdict({"a": 1})
    assert input.get_fr("a") == Xtry.Success(1)


def test_get_fr_should_wrap_failure() -> None:
    input = Xdict({"a": 1})
    assert isinstance(input.get_fr("b").value, IndexError)


@given(st_xdict, st.characters(), st.integers())
def test_set_and_del_should_be_invert(xdict, key, value) -> None:
    assume(key not in xdict.keys())
    result = xdict.updated(key, value).removed(key)
    assert result == xdict


def test_updated_should_union_a_single_element() -> None:
    input = Xdict({"a": 1, "b": 4})
    result = input.updated("b", 2)
    expected = Xdict({"a": 1, "b": 2})

    assert result == expected


def test_removed_should_filter_using_equality_predicate() -> None:
    input = Xdict({"a": 1, "b": 2})
    result = input.removed("b")
    expected = Xdict({"a": 1})

    assert result == expected


def test_union_should_merge_dicts() -> None:
    left = Xdict({"a": 1, "b": 2})
    right = Xdict({"a": 3, "c": 4})
    result = left.union(right)
    expected = Xdict({"a": 3, "b": 2, "c": 4})
    assert result == expected


@given(st.builds(Xlist, st.lists(st.tuples(st.text(), st.integers()))))
def test_items_should_be_from_list_invert(xlist) -> None:
    xdict = Xdict.from_list(xlist)
    # assume element uniqueness
    assume(len(xlist) == len(xdict))

    assert xdict.items() == xlist


# this test is relevant since effective implementation is a proxy for dict.keys()
@given(st_xdict)
def test_keys_should_be_a_list_of_lefts(xdict) -> None:
    equivalent = xdict.items().map(tupled2(lambda x, _: x))
    assert equivalent == xdict.keys()


# this test is relevant since effective implementation is a proxy for dict.values()
@given(st_xdict)
def test_values_should_be_a_list_of_rights(xdict) -> None:
    equivalent = xdict.items().map(tupled2(lambda _, y: y))
    assert equivalent == xdict.values()


def test_map_should_transform_items() -> None:
    xdict = Xdict({"a": "a", "b": "c", "c": "c"})
    expected = Xdict({"aa": "aa", "bc": "cb", "cc": "cc"})

    assert xdict.map(lambda x, y: (x + y, y + x)) == expected


# Which value should be associated is an unenforced behavior and may be subject to change
# However, consistence is key (pun intended) and the same value should be returned each time
def test_map_should_keep_only_one_key_if_collision() -> None:
    xdict = Xdict({"a": "a", "b": "c", "c": "c"})
    iterations = range(0, 20)
    transformations = Xlist(iterations).map(lambda _: xdict.map(lambda _, y: ("e", y)))

    # check consistency
    assert all(transformations.tail().map(lambda x: x == transformations.head()))
    # check unicity
    assert len(transformations.head()) == 1


def test_map_keys_proxy_map(mocker) -> None:
    patch = mocker.patch("xfp.Xdict.map")
    Xdict({"a": 1}).map_keys(lambda k: k)
    assert patch.called


def test_map_values_proxy_map(mocker):
    patch = mocker.patch("xfp.Xdict.map")
    Xdict({"a": 1}).map_values(lambda k: k)
    assert patch.called


def test_filter_should_keep_true_predicate():
    xdict = Xdict({"a": "a", "b": "c", "c": "c"})
    expected = Xdict({"a": "a", "c": "c"})
    assert xdict.filter(lambda x, y: x == y) == expected


def test_filter_keys_should_keep_true_predicate():
    xdict = Xdict({"a": "b", "b": "c", "c": "c"})
    expected = Xdict({"a": "b"})
    assert xdict.filter_keys(lambda x: x == "a") == expected


def test_filter_values_should_keep_true_predicate():
    xdict = Xdict({"a": "a", "b": "c", "c": "c"})
    expected = Xdict({"b": "c", "c": "c"})
    assert xdict.filter_values(lambda y: y == "c") == expected


@given(st_xdict)
def test_foreach_calls(xdict):
    assume(len(xdict) > 0)
    called = False

    def call():
        nonlocal called
        called = True

    xdict.foreach(lambda x, y: call())
    assert called


def test_foreach_ignore_empty():
    xdict = Xdict({})
    called = False

    def call():
        nonlocal called
        called = True

    xdict.foreach(lambda x, y: call())
    assert not called


def test_foreach_keys_proxy_foreach(mocker):
    patch = mocker.patch("xfp.Xdict.foreach")
    Xdict({"a": 1}).foreach_keys(lambda k: print(k))
    assert patch.called


def test_foreach_values_proxy_foreach(mocker):
    patch = mocker.patch("xfp.Xdict.foreach")
    Xdict({"a": 1}).foreach_values(lambda k: print(k))
    assert patch.called
