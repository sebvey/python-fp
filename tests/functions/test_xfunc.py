from hypothesis import given, strategies as st
from xfp.functions import XFunc
import asyncio


def multiply(i: int, *, j: str) -> str:
    return j * i


def replace_dot(s: str) -> str:
    return s.replace(".", ",")


def float_to_string(i: float) -> str:
    return str(i)


@given(st.integers(min_value=1, max_value=5), st.text(max_size=5))
def test_xfunc_should_reproduce_callable_behavior(i, j) -> None:
    assert multiply(i, j=j) == XFunc(multiply)(i, j=j)


@given(st.integers(min_value=1, max_value=5), st.text(max_size=5))
def test_xfunc_a_prop_should_make_it_async(i, j) -> None:
    assert asyncio.run(XFunc(multiply).a(i, j=j)) == XFunc(multiply)(i, j=j)


@given(st.integers(min_value=1, max_value=5), st.text(max_size=5))
def test_xfunc_a_prop_should_be_x_prop_invert(i, j) -> None:
    assert XFunc(multiply).a.x(i, j=j) == XFunc(multiply)(i, j=j)


def test_xfunc_map_should_pipe_functions() -> None:
    assert XFunc(multiply).map(len)(3, j="abcd") == 12


def test_xfunc_contramap_should_revert_pipe_functions() -> None:
    assert XFunc(replace_dot).contramap(float_to_string)(3.14159265) == "3,14159265"


@given(st.integers(min_value=1, max_value=5), st.text(max_size=5))
def test_xfunc_async_map_should_pipe_async_functions(i, j) -> None:
    afunc = XFunc(multiply).async_map(XFunc(len).a)
    xfunc = XFunc(multiply).map(len)
    assert asyncio.run(afunc(i, j=j)) == xfunc(i, j=j)


@given(st.floats(min_value=1, max_value=10))
def test_xfunc_async_contramap_should_revert_pipe_async_functions(i) -> None:
    afunc = XFunc(replace_dot).async_contramap(XFunc(float_to_string).a)
    xfunc = XFunc(replace_dot).contramap(float_to_string)
    assert asyncio.run(afunc(i)) == xfunc(i)
