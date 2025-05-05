from __future__ import annotations
from typing import Any, TypeVar, Iterable
from xfp import Xlist
from collections.abc import Generator, Iterable as ABCIterable
from xfp.xfunc import Xfunc
import trio


X = TypeVar("X", contravariant=True)


class Alist[X]:
    """'async list' = we need to be awaited to produce an Xlist."""

    def __init__(self, coroutines: list) -> None:
        "Construct an Alist from a list of coroutines. For private usage only"
        self._coroutines = coroutines

    def __await__(self) -> Generator[Any, Any, Xlist[X]]:
        return self._coroutine().__await__()

    @classmethod
    def from_iterable(cls, iterable: Iterable[X]) -> Alist[X]:
        """Construct an Alist from an iterable."""

        match iterable:
            case ABCIterable():
                data: list[X] = list(iterable)
            case _:
                raise TypeError(
                    f"'{type(iterable).__name__}' not allowed for Xlist constructor"
                )

        async def el_coroutine(el: X) -> Xlist[X]:
            return el

        return Alist([el_coroutine(el) for el in data])

    def map[Y](self, xfunc: Xfunc[X, Y]) -> Alist[Y]:
        async def new_coroutine(el_coroutine) -> Y:
            result = await el_coroutine
            return await xfunc(result)

        new_coroutines = [new_coroutine(c) for c in self._coroutines]

        return Alist(new_coroutines)

    async def _coroutine(self) -> Xlist[X]:
        results: Xlist[X] = []

        async def collector(coroutine) -> None:
            results.append(await coroutine)

        async with trio.open_nursery() as nursery:
            for coroutine in self._coroutines:
                nursery.start_soon(collector, coroutine)

        return Xlist(results)
