from hypothesis import given, strategies as st
from xfp.a.functions import AFunc
import asyncio

from xfp.functions import XFunc


async def multiply(i: int, *, j: str) -> str:
    await asyncio.sleep(0.001)
    return j * i


async def replace_dot(s: str) -> str:
    await asyncio.sleep(0.001)
    return s.replace(".", ",")


async def float_to_string(i: float) -> str:
    await asyncio.sleep(0.001)
    return str(i)


@given(st.integers(min_value=1, max_value=5), st.text(max_size=5))
def test_afunc_should_reproduce_callable_behavior(i, j) -> None:
    assert asyncio.run(multiply(i, j=j)) == asyncio.run(AFunc(multiply)(i, j=j))


@given(st.integers(min_value=1, max_value=5), st.text(max_size=5))
def test_afunc_x_prop_should_make_it_sync(i, j) -> None:
    assert AFunc(multiply).x(i, j=j) == asyncio.run(AFunc(multiply)(i, j=j))


# TODO
@given(st.integers(min_value=1, max_value=5), st.text(max_size=5))
def test_afunc_x_prop_should_be_a_prop_invert(i, j) -> None:
    assert asyncio.run(AFunc(multiply).x.a(i, j=j)) == asyncio.run(
        AFunc(multiply)(i, j=j)
    )


def test_afunc_map_should_pipe_functions() -> None:
    assert asyncio.run(AFunc(multiply).map(len)(3, j="abcd")) == 12


def test_afunc_contramap_should_revert_pipe_functions() -> None:
    assert (
        asyncio.run(AFunc(replace_dot).contramap(AFunc(float_to_string).x)(3.14159265))
        == "3,14159265"
    )


@given(st.integers(min_value=1, max_value=5), st.text(max_size=5))
def test_afunc_async_map_should_pipe_async_functions(i, j) -> None:
    aafunc = AFunc(multiply).async_map(XFunc(len).a)
    afunc = AFunc(multiply).map(len)
    assert asyncio.run(aafunc(i, j=j)) == asyncio.run(afunc(i, j=j))


@given(st.floats(min_value=1, max_value=10))
def test_afunc_async_contramap_should_revert_pipe_async_functions(i) -> None:
    aafunc = AFunc(replace_dot).async_contramap(float_to_string)
    afunc = AFunc(replace_dot).contramap(AFunc(float_to_string).x)
    assert asyncio.run(aafunc(i)) == asyncio.run(afunc(i))


def to_async(f):
    async def g(*args, **kwargs):
        return f(*args, **kwargs)

    return g


def to_sync(f):
    def g(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return g
