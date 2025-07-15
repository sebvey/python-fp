from dataclasses import dataclass
import functools
from typing import override, Iterable
from xfp.a.async_handler import AsyncHandler

from xfp.functions import XFunc


@dataclass
class SequentialHandler(AsyncHandler):
    """Async Handler that processes elements one by one.

    Handles async function, but awaits them separately.

    ## Usage

    ```python
        from xfp import Xlist
        import asyncio

        sequential_list = Xlist([1, 2, 3, 4, 5], async_handler=SequentialHandler())

        async def multiply(i: int):
            await asyncio.sleep(0.01)
            return i*i

        # Should take ~= 0.01 * 5 = 0.05 second
        assert sequential_list.map(multiply) == Xlist([1, 4, 9, 16, 25])
    ```
    """

    @override
    def map[X, Y](self, f: XFunc[[X], Y], xs: Iterable[X]) -> Iterable[Y]:
        return list(map(f.collect, xs))

    @override
    def reduce[X](self, f: XFunc[[X, X], X], xs: Iterable[X]) -> X:
        """Specific implementation of the reduce operation."""
        return functools.reduce(f.collect, xs)
