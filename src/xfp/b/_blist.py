from __future__ import annotations
from typing import Any, TypeVar
from collections.abc import Awaitable, Callable, Coroutine, Generator, Iterable
import trio

from xfp.xlist import Xlist

# typing vs abc Iterable :
# https://stackoverflow.com/questions/52827463/collections-iterable-vs-typing-iterable-in-type-annotation-and-checking-for-iter

# Blist =
# _iterable : (classique python) Iterable[X] sur lequel on va faire des transfo async
# _el_cofunc : cofunction qui décrit la transformation d'un élément de X vers Y
#
# Blist est awaitable:
# lorsqu'on l'await -> utilise self._cofunc() pour produire et retourner l'objet coroutine (l'awaitable)
#
# Blist est mappable:
# produit une nouvelle Blist en mettant à jour _el_cofunc

type CoFunc[A, B] = Callable[[A], Coroutine[Any, Any, B]]
X = TypeVar("X", covariant=True)


async def _identity[A](e: A) -> A:
    return e


class Blist[X, Y]:
    "Awaitable that produces list of elements."

    def __init__(
        self, iterable: Iterable[X], el_cofunc: CoFunc[X, Y], par: int
    ) -> None:
        self._iterable = iterable
        self._el_cofunc = el_cofunc
        self._par = par

    @staticmethod
    def from_iter(iterable: Iterable[X]) -> Blist[X, X]:
        "Only finite iterable should be used."
        match iterable:
            case Iterable():
                return Blist(iterable, _identity, float("inf"))
            case _:
                raise TypeError(
                    f"'{type(iterable).__name__}' not allowed to construct Blist"
                )

    @staticmethod
    def from_aiter(cls, aiterable: ...) -> Blist[X, X]: ...

    def __await__(self) -> Generator[Any, Any, Xlist[X]]:
        return self._cofunc().__await__()

    # TODO - parallelism not working as expected
    def par(self, parallelism: float) -> Blist[X, Y]:
        "set the parallelism (max number of elements transformed in parallel)"
        return Blist(self._iterable, self._el_cofunc, parallelism)

    async def _cofunc(self) -> Xlist[Y]:
        "cofunction describing the whole materialisation of the Blist to an Xlist"
        "producer / consumer pattern. In prevision of async iter compat"

        # producer: uses iterable to produce elements
        # - once ready, send them to the channel
        # - by now, standard iterable -> each iteration is blocking
        # - in the future, async iterable -> consumer is 'free to work' while other elements are produced

        async def iterable_consumer(send_channel: trio.MemorySendChannel) -> None:
            async with send_channel:
                for el in self._iterable:
                    print(f"                  PRODUCER -> {el}")
                    await send_channel.send(el)

        async def transformer(
            receive_channel: trio.MemoryReceiveChannel,
            results_holder: list[Y],
        ) -> None:
            async with receive_channel:
                async for el in receive_channel:
                    print(f"      TRANSFORMER - {el} -> transforming ...")
                    result: Y = await self._el_cofunc(el)
                    print(f"      TRANSFORMER - {el} -> DONE")
                    results_holder.append(result)

        results_holder: list[Y] = []
        async with trio.open_nursery() as n:
            send_channel, receive_channel = trio.open_memory_channel(float("inf"))
            n.start_soon(iterable_consumer, send_channel)
            n.start_soon(transformer, receive_channel, results_holder)

        return Xlist(results_holder)

    def map[Z](self, cofunc: CoFunc[Y, Z]) -> Blist[X, Z]:
        async def new_el_cofunc(el: X) -> Z:
            return await cofunc((await self._el_cofunc(el)))

        return Blist(self._iterable, new_el_cofunc, self._par)

    def foreach(self, cofunc: CoFunc[Y, Any]) -> Awaitable[None]:
        async def new_el_cofunc(el: X) -> None:
            await cofunc((await self._el_cofunc(el)))

        # We use Blist to construct the new cofunction
        # We use this cofunction to produce the coroutine object (awaitable)
        # We return the awaitable
        return Blist(self._iterable, new_el_cofunc, self._par)._cofunc()
