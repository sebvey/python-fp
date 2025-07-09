from dataclasses import dataclass
from xfp.a.functions import AF1
from xfp.a.functions import AFunc
from xfp.functions import F1


@dataclass(frozen=True)
class XFunc[**X, Y]:
    """Encapsulate a native Python function.

    Used to enhance its behavior through the homogene XFP Api.

    ## Features:
    - functor behavior, both covariant (with the ouput) and contravariant (if a unique input parameter exists)
    - linked asynchronous behaviour: chaining (co/contra-variant way) async functions, lifting synchronous function
    """

    f: F1[X, Y]

    def __call__(self, *args: X.args, **kwargs: X.kwargs) -> Y:
        """Uses the underlying f.__call__."""
        return self.f(*args, **kwargs)

    @property
    def a(self) -> "AFunc[X, Y]":
        """Lift the synchronous XFunc and return an AFunc equivalent.

        The resulting AFunc still has an synchronous behavior, but is wrapped into a Coroutine.

        ## Usage

        ```python
            from xfp.functions import XFunc
            import asyncio

            def multiply(i: int, *, j: str) -> str:
                return j * i

            xfuncked = XFunc(multiply)
            asyncked = xfuncked.a
            operated = asyncked.map(lambda resulting_str: resulting_str * 2) # work with your asynchronous lifted function

            assert asyncio.run(asyncked(2, "abc")) == xfuncked(2, "abc")
            assert operated(2, "abc") == "abcabcabcabc"
        ```
        """

        async def h(*args: X.args, **kwargs: X.kwargs) -> Y:
            return self(*args, **kwargs)

        return AFunc(h)

    def map[U](self, g: F1[[Y], U]) -> "XFunc[X, U]":
        """Pipe another function directly after self.f.

        ## Arguments

        - g: the function to be called after f resulted

        ## Usage

        ```python
            from typing import TYPE_CHECKING, reveal_type
            from xfp.functions import XFunc

            def multiply(i: int, *, j: str) -> str:
                return j * i

            xfuncked = XFunc(multiply)
            mapped = xfuncked.map(len)
            if TYPE_CHECKING:
                reveal_type(xfuncked) # XFunc[(i: int, *, j: str), str]
                reveal_type(mapped) # XFunc[(i: int, *, j: str), int]

            # kwargs are preserved
            assert mapped(3, j = "abc") == len(multiply(3, j = "abc"))
            assert mapped(3, j = "abc") == 9
        ```
        """

        # chaining two sync functions must never use AFunc because of notebook execution
        def h(*args: X.args, **kwargs: X.kwargs) -> U:
            return g(self(*args, **kwargs))

        return XFunc(h)

    def contramap[**T, XX](self: "XFunc[[XX], Y]", g: F1[T, XX]) -> "XFunc[T, Y]":
        """Pipe another function directly before self.f.

        ## Arguments

        - self: retrained on XFunc with a unique input parameter
        - g: the function to be called before f

        ## Usage

        ```python
            from typing import TYPE_CHECKING, reveal_type
            from xfp.functions import XFunc

            def replace_points(j: str) -> str:
                return j.replace(".", ",")

            def float_to_string(i: float) -> str:
                return str(i)

            xfuncked = XFunc(replace_points)
            contramapped = xfuncked.contramap(float_to_string)
            if TYPE_CHECKING:
                reveal_type(xfuncked) # XFunc[(j: str), str]
                reveal_type(contramapped) # XFunc[(i: float), str]

            assert contramapped(3.14159) == "3,14159"
        ```
        """
        return XFunc(g).map(self)

    def async_map[U](self, g: AF1[[Y], U]) -> "AFunc[X, U]":
        """Lift the synchronous XFunc and pipe another async function directly after.

        ## Arguments

        - g: the async function to be called after f resulted

        ## Usage

        ```python
            from typing import TYPE_CHECKING, reveal_type
            from xfp.functions import XFunc
            import asyncio

            def multiply(i: int, *, j: str) -> str:
                return j * i

            async def waited_len(s: str):
                await asyncio.sleep(5)
                return len(s)

            xfuncked = XFunc(multiply)
            mapped = xfuncked.async_map(waited_len)
            if TYPE_CHECKING:
                reveal_type(xfuncked) # XFunc[(i: int, *, j: str), str]
                reveal_type(mapped) # AFunc[(i: int, *, j: str), int]

            # after 5 seconds
            assert asyncio.run(mapped(3, j = "abc")) == 9
        ```
        """
        return self.a.async_map(g)

    def async_contramap[**T, XX](
        self: "XFunc[[XX], Y]", g: AF1[T, XX]
    ) -> "AFunc[T, Y]":
        """Lift the synchronous XFunc and pipe another async function directly before self.f.

        ## Arguments

        - self: retrained on XFunc with a unique input parameter
        - g: the async function to be called before f

        ## Usage

        ```python
            from typing import TYPE_CHECKING, reveal_type
            from xfp.functions import XFunc
            import asyncio

            def replace_points(j: str) -> str:
                return j.replace(".", ",")

            async def float_to_string(i: float) -> str:
                await asyncio.sleep(5)
                return str(i)

            xfuncked = XFunc(replace_points)
            contramapped = xfuncked.async_contramap(float_to_string)
            if TYPE_CHECKING:
                reveal_type(xfuncked) # XFunc[(j: str), str]
                reveal_type(contramapped) # AFunc[(i: float), str]

            # after 5 seconds
            assert asyncio.run(contramapped(3.14159)) == "3,14159"
        ```
        """
        return self.a.async_contramap(g)
