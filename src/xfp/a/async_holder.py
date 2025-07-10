from typing import Iterable, Protocol

from xfp.functions import XF1, XFunc


class AsyncHolder(Protocol):
    # def gather[X](self, async_results: Iterable[Coroutine[Any, Any, X]]) -> Coroutine[Any, Any, Iterable[X]]: ...

    def ap[X, Y](
        self, async_process: Iterable[XF1[[X], Y]]
    ) -> XFunc[[Iterable[X]], Iterable[Y]]: ...

    def reduce[X](self, f: XF1[[X, X], X], xs: Iterable[X]) -> X: ...

    def distribute[X, Y](self, f: XF1[[X], Y], xs: Iterable[X]) -> Iterable[Y]:
        return self.ap([f for _ in xs]).collect(xs)
