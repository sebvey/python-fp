from typing import Any
from hypothesis import given, strategies as st
import pytest

from xfp import Xdict, Xlist
from ...xdict import ABCDict

st_dict = st.dictionaries(st.text(), st.integers())
st_xdict = st.builds(Xdict, st_dict)


@given(st_dict)
def test_abcdict_should_match_dict(dictlike: dict):
    assert isinstance(dictlike, ABCDict)


@given(st_xdict)
def test_abcdict_should_match_dictlike(dictlike: Xdict):
    assert isinstance(dictlike, ABCDict)


@pytest.mark.parametrize("anything", [3, "a", Xlist([1, 2, 3])])
def test_abcdict_should_ignore_everythingelse(anything: Any):
    assert not isinstance(anything, ABCDict)


@given(st_dict)
def test_xdict_should_instantiate_from_list_or_dict(raw_dict: dict):
    assert Xdict.from_list(raw_dict.items()) == Xdict(raw_dict)


@given(st_xdict)
def test_xdict_should_have_invert_from_list_and_items(xdict):
    assert Xdict.from_list(xdict.items()) == xdict


@given(st_dict)
def test_xdict_should_instantiate_idempotent(raw_dict: Xdict):
    assert Xdict(Xdict(raw_dict)) == Xdict(raw_dict)
