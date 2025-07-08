from hypothesis import given, strategies as st
from xfp.functions import XFunc


def multiply(i: int, *, j: str) -> str:
    return j * i


def replace_dot(s: str) -> str:
    return s.replace(".", ",")


def float_to_string(i: float) -> str:
    return str(i)


@given(st.integers(min_value=1, max_value=5), st.text(max_size=5))
def test_xfunc_should_reproduce_callable_behavior(i, j) -> None:
    assert multiply(i, j=j) == XFunc(multiply)(i, j=j)


def test_xfunc_map_should_pipe_functions():
    assert XFunc(multiply).map(len)(3, j="abcd") == 12


def test_xfunc_contramap_should_revert_pipe_functions():
    assert XFunc(replace_dot).contramap(float_to_string)(3.14159265) == "3,14159265"
