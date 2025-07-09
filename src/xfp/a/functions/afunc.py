from dataclasses import dataclass
import threading
from xfp.a.functions import AF1
from xfp.functions import F1
import asyncio
from asyncio import AbstractEventLoop


@dataclass(frozen=True)
class AFunc[**X, Y]:
    """Encapsulate a native async Python function.

    Used to enhance its behavior through the homogene XFP Api.

    ## Features:
    - functor behavior, both covariant (with the ouput) and contravariant (if a unique input parameter exists)
    - interfaced with synchroned function: ad-hoc resynchronization of the function
    """

    f: AF1[X, Y]

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

    @property
    def x(self) -> "XFunc[X, Y]":  # type: ignore # noqa: F821
        """Resynchronize the function and return an XFunc equivalent.

        Works as a transparent-er asyncio.run, since you don't have to worry at all about the event loop you're in.

        ## Usage

        ```python
            from xfp import AFunc
            import asyncio

            async def multiply(i: int, *, j: str) -> str:
                await asyncio.sleep(5)
                return j * i

            afuncked = AFunc(multiply)
            resyncked = afuncked.x
            operated = resyncked.map(lambda resulting_str: resulting_str * 2) # work with your resynchronous function

            assert asyncio.run(afuncked(2, "abc")) == resyncked(2, "abc")
            assert operated(2, "abc") == "abcabcabcabc"
        ```
        """
        from xfp.functions import XFunc

        def h(*args: X.args, **kwargs: X.kwargs) -> Y:
            try:
                loop: AbstractEventLoop = asyncio.get_running_loop()
            except RuntimeError:
                return self.__materialize_run(*args, **kwargs)
            else:
                # handle .x.a.x.a ...
                return self.__materialize_thread(loop, *args, **kwargs)

        return XFunc(h)

    def map[U](self, g: F1[[Y], U]) -> "AFunc[X, U]":
        """Pipe another function directly after self.f.

        ## Arguments

        - g: the function to be called after f resulted

        ## Usage

        ```python
            from typing import TYPE_CHECKING, reveal_type
            from xfp.a.functions import AFunc
            import asyncio

            async def multiply(i: int, *, j: str) -> str:
            await asyncio.sleep(5)
                return j * i

            afuncked = AFunc(multiply)
            mapped = afuncked.map(len)
            if TYPE_CHECKING:
                reveal_type(afuncked) # AFunc[(i: int, *, j: str), str]
                reveal_type(mapped) # AFunc[(i: int, *, j: str), int]

            # kwargs are preserved
            assert asyncio.run(mapped(3, j = "abc")) == len(asyncio.run(multiply(3, j = "abc")))
            assert asyncio.run(mapped(3, j = "abc")) == 9
        ```
        """
        from xfp.functions import XFunc

        return self.async_map(XFunc(g).a)

    def contramap[**T, XX](self: "AFunc[[XX], Y]", g: F1[T, XX]) -> "AFunc[T, Y]":
        """Pipe another function directly before self.f.

        ## Arguments

        - self: retrained on AFunc with a unique input parameter
        - g: the function to be called before f

        ## Usage

        ```python
            from typing import TYPE_CHECKING, reveal_type
            from xfp.a.functions import AFunc
            import asyncio

            async def replace_points(j: str) -> str:
                await asyncio.sleep(5)
                return j.replace(".", ",")

            def float_to_string(i: float) -> str:
                return str(i)

            afuncked = AFunc(replace_points)
            contramapped = afuncked.contramap(float_to_string)
            if TYPE_CHECKING:
                reveal_type(afuncked) # AFunc[(j: str), str]
                reveal_type(contramapped) # AFunc[(i: float), str]

            assert asyncio.run(contramapped(3.14159)) == "3,14159"
        ```
        """
        from xfp.functions import XFunc

        return self.async_contramap(XFunc(g).a)

    def async_map[U](self, g: AF1[[Y], U]) -> "AFunc[X, U]":
        """Pipe another async function directly after self.f.

        ## Arguments

        - g: the async function to be called after f resulted

        ## Usage

        ```python
            from typing import TYPE_CHECKING, reveal_type
            from xfp.functions import XFunc
            import asyncio

            async def multiply(i: int, *, j: str) -> str:
                await asyncio.sleep(5)
                return j * i

            async def waited_len(s: str):
                await asyncio.sleep(5)
                return len(s)

            afuncked = AFunc(multiply)
            mapped = afuncked.async_map(waited_len)
            if TYPE_CHECKING:
                reveal_type(afuncked) # AFunc[(i: int, *, j: str), str]
                reveal_type(mapped) # AFunc[(i: int, *, j: str), int]

            # after 10 seconds
            assert asyncio.run(mapped(3, j = "abc")) == 9
        ```
        """

        async def h(*args: X.args, **kwargs: X.kwargs) -> U:
            y = await self(*args, **kwargs)
            return await g(y)

        return AFunc(h)

    def async_contramap[**T, XX](
        self: "AFunc[[XX], Y]", g: AF1[T, XX]
    ) -> "AFunc[T, Y]":
        """Pipe another async function directly before self.f.

        ## Arguments

        - self: retrained on AFunc with a unique input parameter
        - g: the async function to be called before f

        ## Usage

        ```python
            from typing import TYPE_CHECKING, reveal_type
            from xfp.functions import XFunc
            import asyncio

            async def replace_points(j: str) -> str:
                await asyncio.sleep(5)
                return j.replace(".", ",")

            async def float_to_string(i: float) -> str:
                await asyncio.sleep(5)
                return str(i)

            afuncked = AFunc(replace_points)
            contramapped = afuncked.async_contramap(float_to_string)
            if TYPE_CHECKING:
                reveal_type(afuncked) # AFunc[(j: str), str]
                reveal_type(contramapped) # AFunc[(i: float), str]

            # after 10 seconds
            assert asyncio.run(contramapped(3.14159)) == "3,14159"
        ```
        """
        return AFunc(g).async_map(self)
