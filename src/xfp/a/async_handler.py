from abc import ABC, abstractmethod
from typing import Iterable

from xfp.functions import XFunc


class AsyncHandler(ABC):
    """Generic tool handle asynchronism.

    Used in composition in collections to delegate in which order operations are executed.
    Can be configurable through the async_handler parameter.

    ## Usage

    ```python
        from xfp import Xlist
        import asyncio

        sequential_list = Xlist([1, 2, 3, 4, 5], async_handler=SequentialHandler())
        async_list = Xlist([1, 2, 3, 4, 5], async_handler=SimpleAsyncHandler())

        async def multiply(i: int):
            await asyncio.sleep(0.01)
            return i*i

        # however async_list computes faster
        assert sequential_list.map(multiply) == async_list.map(multiply)
    ```
    """

    @abstractmethod
    def reduce[X](self, f: XFunc[[X, X], X], xs: Iterable[X]) -> X: ...

    @abstractmethod
    def map[X, Y](self, f: XFunc[[X], Y], xs: Iterable[X]) -> Iterable[Y]: ...
