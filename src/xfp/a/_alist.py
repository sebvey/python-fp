from __future__ import annotations
from typing import Any
from collections.abc import Awaitable, Generator, Iterable

import trio

from xfp.xlist import Xlist
from ._afunc import Afunc

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


@Afunc
async def _identity[A](e: A) -> A:
    return e


# I : input type
# R : result type


class Alist[I, R]:
    """Awaitable that produces list of elements.
    We can map Afunc
    (no runtime enforcement -> we can also map standard cofunc
    TODO: should be enforced ?
    TODO: should be allowed, signature adapted ?
    )
    """

    def __init__(
        self, iterable: Iterable[I], el_afunc: Afunc[[I], R], par: int
    ) -> None:
        "for private use. TODO: protect from outside call"
        self._iterable: Iterable[I] = iterable
        self._el_afunc: Afunc[[I], R] = el_afunc
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
    def from_iterable[E](iterable: Iterable[E], par: int | None = None) -> Alist[E, E]:
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

    def __await__(self) -> Generator[Any, Any, Xlist[I]]:
        return self._cofunc().__await__()

    def par(self, par: int | None) -> Alist[I, R]:
        "returns a new Alist with parallelism set to 'par' (max number of elements transformed in parallel)"
        return Alist(self._iterable, self._el_afunc, self._parse_par(par))

    async def _cofunc(self) -> Xlist[R]:
        "cofunction describing the whole materialisation of the Alist to an Xlist"

        results: list[R] = []
        semaphore: trio.Semaphore | None = (
            trio.Semaphore(self._par) if self._par else None
        )

        async def transform_closure(
            item: I,
        ) -> None:
            results.append(await self._el_afunc(item))
            if semaphore:
                semaphore.release()

        async with trio.open_nursery() as nursery:
            for item in self._iterable:
                if semaphore:
                    await semaphore.acquire()
                nursery.start_soon(transform_closure, item)

        return Xlist(results)

    def map[Ro](self, afunc: Afunc[[R], Ro]) -> Alist[I, Ro]:
        @Afunc
        async def new_el_afunc(el: I) -> Ro:
            return await afunc((await self._el_afunc(el)))

        return Alist(self._iterable, new_el_afunc, self._par)

    def foreach(self, afunc: Afunc[[R], Any]) -> Awaitable[None]:
        async def new_el_afunc(el: I) -> None:
            await afunc((await self._el_afunc(el)))

        # We use Alist to construct the new cofunction
        # We use this cofunction to produce the coroutine object (awaitable)
        # We return the awaitable
        return Alist(self._iterable, new_el_afunc, self._par)._cofunc()
