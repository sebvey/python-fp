import asyncio
import time

import pytest

from xfp import Xlist
from xfp.a import (
    AsyncHandler,
    SequentialHandler,
    SimpleAsyncHandler,
    ThrottledAsyncHandler,
)
from xfp.functions import XFunc


@XFunc.from_async
async def multiply(i: int) -> int:
    await asyncio.sleep(0.01)
    return i * i


@XFunc.from_async
async def sum(i: int, j: int) -> int:
    await asyncio.sleep(0.01)
    return i + j


@pytest.mark.parametrize(
    "async_handler",
    [SequentialHandler(), SimpleAsyncHandler(), ThrottledAsyncHandler(5)],
)
def test_builtin_handlers_should_have_same_behavior(
    async_handler: AsyncHandler,
) -> None:
    input = Xlist([1, 2, 3, 4, 5], async_handler=async_handler)
    assert async_handler.map(multiply, input) == [1, 4, 9, 16, 25]


@pytest.mark.parametrize(
    "async_handler",
    [SequentialHandler(), SimpleAsyncHandler(), ThrottledAsyncHandler(5)],
)
def test_builtin_handlers_reduce_should_have_same_behavior(
    async_handler: AsyncHandler,
) -> None:
    input = Xlist([1, 2, 3, 4, 5], async_handler=async_handler)
    assert async_handler.reduce(sum, input) == 15


def test_async_handler_should_be_faster() -> None:
    input: Xlist[int] = Xlist(range(1, 1000))
    sync_list: Xlist[int] = Xlist(input, async_handler=SequentialHandler())
    tsync_list: Xlist[int] = Xlist(input, async_handler=ThrottledAsyncHandler(5))
    async_list: Xlist[int] = Xlist(input, async_handler=SimpleAsyncHandler())
    start: float = time.perf_counter()
    result1: Xlist[int] = sync_list.map(multiply)
    middle1: float = time.perf_counter()
    result2: Xlist[int] = tsync_list.map(multiply)
    middle2: float = time.perf_counter()
    result3: Xlist[int] = async_list.map(multiply)
    end: float = time.perf_counter()
    assert result1 == result2
    assert result2 == result3

    assert (middle1 - start) > (middle2 - middle1)
    assert (middle2 - middle1) > (end - middle2)
