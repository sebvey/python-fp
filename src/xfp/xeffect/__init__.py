from __future__ import annotations
from typing import Any, Callable, Coroutine, Generator

from xfp import Xresult


# Coroutine = function 'résolu' (les arguments sont définis)
# -> il ne reste plus qu'à await déclencher l'exécution asynchrone
# Dans le cas XFP, les coroutines sont toutes du même type, elle retourne un
# Xresult[L,R]
# => Appelé coro
type PyXRCo[L, R] = Coroutine[Any, Any, Xresult[L, R]]

# XCoro = XFP Coroutine
# Conteneur pour la PyXRCo
# -> va permettre de faire de la composition
#    = appliquer de nouveaux effets pour produire de nouvelle coroutines
#    - map()


# cfunc : function python qui produit une coroutine

# Xeffect = objet qui porte la description de l'effet (la fonction qui produit la coroutine)


class Xeffect[**P, L, R]:
    def __init__(self, cfunc: Callable[P, PyXRCo[L, R]]) -> None:
        self._func = cfunc

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> XCoroutine[L, R]:
        return XCoroutine(self._func(*args, **kwargs))


class XCoroutine[L, R]:
    def __init__(self, coroutine: PyXRCo[L, R]) -> None:
        self._coroutine = coroutine

    def __await__(self) -> Generator[Any, Any, Xresult[L, R]]:
        return self._coroutine.__await__()

    def map_right[PO, LO, RO](self, xeffect: Xeffect[PO, LO, RO]) -> XCoroutine[LO, RO]:
        async def func() -> Xresult[L, RO]:
            first_result: Xresult[L, R] = await self._coroutine
            if first_result.is_right():
                return await xeffect(first_result.value)._coroutine
            return first_result

        return XCoroutine(func())

    def map_left[PO, LO, RO](self, xeffect: Xeffect[PO, LO, RO]) -> XCoroutine[LO, R]:
        async def func() -> Xresult[LO, R]:
            first_result: Xresult[L, R] = await self._coroutine
            if first_result.is_left():
                return await xeffect(first_result.value)._coroutine
            return first_result

        return XCoroutine(func())

    def map[PO, LO, RO](self, xeffect: Xeffect[PO, LO, RO]) -> XCoroutine[LO, RO]:
        "Alias for .map_right()"
        return self.map_right(xeffect)


# TODO - map* - xeffect with one arg (left|right type of the coroutine)
