from hypothesis import given, strategies as st
from xfp.functions import XFunc
import asyncio


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
def test_xfunc_should_reproduce_callable_behavior(i, j) -> None:
    assert asyncio.run(multiply(i, j=j)) == asyncio.run(
        XFunc.from_async(multiply)(i, j=j)
    )


@given(st.integers(min_value=1, max_value=5), st.text(max_size=5))
def test_xfunc_collect_should_make_it_sync(i, j) -> None:
    assert XFunc.from_async(multiply).collect(i, j=j) == asyncio.run(
        XFunc.from_async(multiply)(i, j=j)
    )


def test_xfunc_map_should_pipe_functions() -> None:
    assert asyncio.run(XFunc.from_async(multiply).map(len)(3, j="abcd")) == 12


def test_xfunc_contramap_should_revert_pipe_functions() -> None:
    assert (
        asyncio.run(
            XFunc.from_async(replace_dot).contramap(
                XFunc.from_async(float_to_string).collect
            )(3.14159265)
        )
        == "3,14159265"
    )
