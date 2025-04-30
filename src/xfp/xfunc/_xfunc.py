from __future__ import annotations
from typing import Any, Callable, Generator

from xfp import Xtry, Xresult
from ._typing import PyCoXR, PyCo

# Coroutine Function - cofunc - (async def)
# description paramétrable d'un code à exécuter
# l'appel à la fonction produit une coroutine
#
# Dans le scope XFP peuvent être de plusieurs 'genres' :
# - décrive la production d'un XResult (XRFunc?)
# - plus générale : (XFunc?)
# - peuvent prendre un ou plusieurs paramètres ...

# XRFunc = objet qui porte la description d'un code produisant XResult
# __call__ renvoi XRCoroutine

# Coroutine object = objet 'résolu' (plus d'arguments à fournir, déjà injectés)
# représentant du code exécutable de manière asynchrone
# -> il ne reste plus qu'à await l'objet pour orchestrer l'exécution asynchrone
#
# Dans le scope XFP, les coroutines peuvent soit :
# - retourner un Xresult[L,R] => coroutine de type PyCoXR[L,R]
# - plus généralement retourner un type X => coroutine de type PyCo[X]


# XRCoroutine = XFP Result Coroutine
# Conteneur pour coroutines produisant un XResult
# -> va permettre de faire de la composition
#    = appliquer de nouveaux effets pour produire de nouvelle XRCoroutines

# TODO NEXT - pipe() - foreach() - map()


class XRfunc[**P, L, R]:
    def __init__(self, cofunc: Callable[P, PyCoXR[L, R]]) -> None:
        self._cofunc: Callable[P, PyCoXR[L, R]] = cofunc

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> XRCoroutine[L, R]:
        return XRCoroutine(self._cofunc(*args, **kwargs))

    @classmethod
    def from_unsafe[R](cls, func: Callable[P, R]) -> XRfunc[P, Exception, R]:
        async def effect(*args: P.args, **kwargs: P.kwargs) -> Xresult[Exception, R]:
            try:
                return Xtry.Success(func(*args, **kwargs))
            except Exception as e:
                return Xtry.Failure(e)

        return XRfunc(effect)


class XRCoroutine[L, R]:
    def __init__(self, coroutine: PyCoXR[L, R]) -> None:
        self._coroutine = coroutine

    def __await__(self) -> Generator[Any, Any, Xresult[L, R]]:
        return self._coroutine.__await__()

    def flat_map_right[PO, LO, RO](
        self, xeffect: XRfunc[PO, LO, RO]
    ) -> XRCoroutine[L | LO, RO]:
        async def cofunc() -> Xresult[L | LO, RO]:
            first_result: Xresult[L, R] = await self
            if first_result.is_right():
                return await xeffect(first_result.value)
            return first_result

        return XRCoroutine(cofunc())

    def flat_map_left[PO, LO, RO](
        self, xeffect: XRfunc[PO, LO, RO]
    ) -> XRCoroutine[LO, R | RO]:
        async def func() -> Xresult[LO, R]:
            result: Xresult[L, R] = await self
            if result.is_left():
                return await xeffect(result.value)
            return result

        return XRCoroutine(func())

    def flat_map[PO, LO, RO](
        self, xeffect: XRfunc[PO, LO, RO]
    ) -> XRCoroutine[L | LO, RO]:
        "Alias for .flat_map_right()"
        return self.flat_map_right(xeffect)

    def foreach_right(self, cofunc: Callable[[R], PyCo[Any]]) -> PyCo[None]:
        "Do the async statement procedure to the underlying value if self is a RIGHT"

        async def new_cofunc() -> None:
            result: Xresult[L, R] = await self
            if result.is_right():
                return await cofunc(result.value)

        return XRCoroutine(new_cofunc())

    def foreach_left(self, cofunc: Callable[[L], PyCo[Any]]) -> PyCo[None]:
        "Do the async statement procedure to the underlying value if self is a LEFT"

        async def new_cofunc() -> None:
            result: Xresult[L, R] = await self
            if result.is_left():
                return await cofunc(result.value)

        return XRCoroutine(new_cofunc())

    def foreach[PO, LO](self, cofunc: Callable[[R], PyCo[Any]]) -> PyCo[None]:
        "Alias for .foreach_right()"
        return self.foreach_right(cofunc)


# TODO - typing foireux, particulièrement en terme d'argument
