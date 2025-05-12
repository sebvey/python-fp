from __future__ import annotations
from typing import Any, TypeVar
from collections.abc import Awaitable, Generator, Iterable
from ._typing import CoFunc1

import trio

from xfp.xlist import Xlist

# typing vs abc Iterable :
# https://stackoverflow.com/questions/52827463/collections-iterable-vs-typing-iterable-in-type-annotation-and-checking-for-iter

# Alist =
# _iterable : (classique python) Iterable[X] sur lequel on va faire des transfo async
# _el_cofunc : cofunction qui décrit la transformation d'un élément de X vers Y
#
# Alist est awaitable:
# lorsqu'on l'await -> utilise self._cofunc() pour produire l'objet coroutine (l'awaitable)
# et l'awaiter
#
# Alist est mappable:
# produit une nouvelle Alist en mettant à jour _el_cofunc

X = TypeVar("X", covariant=True)


async def _identity[A](e: A) -> A:
    return e


class Alist[X, Y]:
    "Awaitable that produces list of elements."

    def __init__(
        self, iterable: Iterable[X], el_cofunc: CoFunc1[X, Y], par: int
    ) -> None:
        "for private use. TODO: protect from outside call"
        self._iterable = iterable
        self._el_cofunc = el_cofunc
        self._par: int | None = par

    @staticmethod
    def _parse_par(par: Any) -> int | None:
        try:
            if par is None:
                return None
            if (parsed := int(par)) <= 0:
                raise ValueError("'par' must be a positive integer or None")
            return parsed
        except ValueError:
            raise ValueError("'par' must be a positive integer or None")

    @staticmethod
    def from_iterable(iterable: Iterable[X], par: int | None = None) -> Alist[X, X]:
        """
        Only finite iterable should be used.
        par (PositiveInt | None): parallelism. None -> 'infinite' parallelism
        """

        match iterable:
            case Iterable():
                return Alist(iterable, _identity, Alist._parse_par(par))
            case _:
                raise TypeError(
                    f"'{type(iterable).__name__}' not allowed to construct Alist"
                )

    def __await__(self) -> Generator[Any, Any, Xlist[X]]:
        return self._cofunc().__await__()

    def par(self, par: int | None) -> Alist[X, Y]:
        "returns a new Alist with parallelism set to 'par' (max number of elements transformed in parallel)"
        return Alist(self._iterable, self._el_cofunc, self._parse_par(par))

    async def _cofunc(self) -> Xlist[Y]:
        "cofunction describing the whole materialisation of the Alist to an Xlist"

        results: list[Y] = []
        semaphore: trio.Semaphore | None = (
            trio.Semaphore(self._par) if self._par else None
        )

        async def transform_closure(
            item: X,
        ) -> None:
            results.append(await self._el_cofunc(item))
            if semaphore:
                semaphore.release()

        async with trio.open_nursery() as nursery:
            for item in self._iterable:
                if semaphore:
                    await semaphore.acquire()
                nursery.start_soon(transform_closure, item)

        return Xlist(results)

    def map[Z](self, CoFunc1: CoFunc1[Y, Z]) -> Alist[X, Z]:
        async def new_el_cofunc(el: X) -> Z:
            return await CoFunc1((await self._el_cofunc(el)))

        return Alist(self._iterable, new_el_cofunc, self._par)

    def foreach(self, CoFunc1: CoFunc1[Y, Any]) -> Awaitable[None]:
        async def new_el_cofunc(el: X) -> None:
            await CoFunc1((await self._el_cofunc(el)))

        # We use Alist to construct the new cofunction
        # We use this cofunction to produce the coroutine object (awaitable)
        # We return the awaitable
        return Alist(self._iterable, new_el_cofunc, self._par)._cofunc()
