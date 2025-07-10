import threading
from typing import cast
from xfp.functions import AF1, F1, XF1
import asyncio
from asyncio import AbstractEventLoop
import inspect


class XFunc[**X, Y]:
    """Encapsulate a native async Python function.

    Used to enhance its behavior through the homogene XFP Api.

    ## Features:
    - functor behavior, both covariant (with the ouput) and contravariant (if a unique input parameter exists)
    - interfaced with synchroned function:
        - ad-hoc resynchronization of the function
        - ad-hoc lifting of synchrone function
    """

    def __init__(self, f: XF1[X, Y]) -> None:
        if isinstance(f, XFunc):
            self.f: AF1[X, Y] = f.f
        elif inspect.iscoroutinefunction(f):
            self.f: AF1[X, Y] = f
        else:

            async def h(*args: X.args, **kwargs: X.kwargs) -> Y:
                return cast(Y, f(*args, **kwargs))

            self.f: AF1[X, Y] = h
        inspect.markcoroutinefunction(self)

    async def __call__(self, *args: X.args, **kwargs: X.kwargs) -> Y:
        """Uses the underlying f.__call__."""
        return await self.f(*args, **kwargs)

    def __materialize_run(self, *args: X.args, **kwargs: X.kwargs) -> Y:
        return asyncio.run(self(*args, **kwargs))

    def __materialize_thread(
        self, loop: AbstractEventLoop, *args: X.args, **kwargs: X.kwargs
    ) -> Y:
        fut: asyncio.Future[Y] = loop.create_future()

        def run_in_thread() -> None:
            try:
                new_loop: AbstractEventLoop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                result: Y = new_loop.run_until_complete(self(*args, **kwargs))
                fut.set_result(result)
            except Exception as e:
                fut.set_exception(e)
            finally:
                new_loop.close()

        t = threading.Thread(target=run_in_thread)
        t.start()
        t.join()
        return fut.result()

    def collect(self, *args: X.args, **kwargs: X.kwargs) -> F1[X, Y]:
        """Return the raw synchrone function equivalent.

        Works as a transparent-er asyncio.run, since you don't have to worry at all about the event loop you're in.

        ## Usage

        ```python
            from xfp.functions XFunc
            import asyncio

            async def multiply(i: int, *, j: str) -> str:
                await asyncio.sleep(5)
                return j * i

            xfuncked = XFunc(multiply)
            resyncked = xfuncked.collect

            assert asyncio.run(xfuncked(2, "abc")) == resyncked(2, "abc")
        ```
        """
        try:
            loop: AbstractEventLoop = asyncio.get_running_loop()
        except RuntimeError:
            return self.__materialize_run(*args, **kwargs)
        else:
            return self.__materialize_thread(loop, *args, **kwargs)

    def map[U](self, g: XF1[[Y], U]) -> "XFunc[X, U]":
        """Pipe another function directly after self.f.

        ## Arguments

        - g: the function to be called after f resulted

        ## Usage

        ```python
            from typing import TYPE_CHECKING, reveal_type
            from xfp.functions import XFunc
            import asyncio

            async def multiply(i: int, *, j: str) -> str:
            await asyncio.sleep(5)
                return j * i

            xfuncked = XFunc(multiply)
            mapped = xfuncked.map(len)
            if TYPE_CHECKING:
                reveal_type(xfuncked) # XFunc[(i: int, *, j: str), str]
                reveal_type(mapped) # XFunc[(i: int, *, j: str), int]

            # kwargs are preserved
            assert asyncio.run(mapped(3, j = "abc")) == len(asyncio.run(multiply(3, j = "abc")))
            assert asyncio.run(mapped(3, j = "abc")) == 9
        ```
        """

        async def h(*args: X.args, **kwargs: X.kwargs) -> U:
            y: Y = await self(*args, **kwargs)
            return await XFunc(g)(y)

        return XFunc(h)

    def contramap[**T, XX](self: "XFunc[[XX], Y]", g: XF1[T, XX]) -> "XFunc[T, Y]":
        """Pipe another function directly before self.f.

        ## Arguments

        - self: retrained on XFunc with a unique input parameter
        - g: the function to be called before f

        ## Usage

        ```python
            from typing import TYPE_CHECKING, reveal_type
            from xfp.functions import XFunc
            import asyncio

            async def replace_points(j: str) -> str:
                await asyncio.sleep(5)
                return j.replace(".", ",")

            def float_to_string(i: float) -> str:
                return str(i)

            xfuncked = XFunc(replace_points)
            contramapped = xfuncked.contramap(float_to_string)
            if TYPE_CHECKING:
                reveal_type(xfuncked) # XFunc[(j: str), str]
                reveal_type(contramapped) # XFunc[(i: float), str]

            assert asyncio.run(contramapped(3.14159)) == "3,14159"
        ```
        """
        return XFunc(g).map(self)
