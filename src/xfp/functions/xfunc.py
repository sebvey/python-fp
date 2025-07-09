from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class XFunc[**X, Y]:
    """Encapsulate a native Python function.

    Used to enhance its behavior through the homogene XFP Api.

    ## Features:
    - functor behavior, both covariant (with the ouput) and contravariant (if a unique input parameter exists)
    """

    f: Callable[X, Y]

    def __call__(self, *args: X.args, **kwargs: X.kwargs) -> Y:
        """Uses the underlying f.__call__."""
        return self.f(*args, **kwargs)

    def map[U](self, g: Callable[[Y], U]) -> "XFunc[X, U]":
        """Pipe another function directly after self.f.

        ## Arguments

        - g: the function to be called after f resulted

        ## Usage

        ```python
            from typing import TYPE_CHECKING, reveal_type
            from xfp import XFunc

            def multiply(i: int, *, j: str) -> str:
                return j * i

            xfuncked = XFunc(multiply)
            mapped = xfuncked.map(len)
            if TYPE_CHECKING:
                reveal_type(xfuncked) # XFunc[(i: int, *, j: str), str]
                reveal_type(mapped) # XFunc[(i: int, *, j: str), int]

            # kwargs are preserved
            assert mapped(3, j = "abc") == XFunc(multiply).map(len)(3, j = "abc")
            assert mapped(3, j = "abc") == 9
        ```
        """

        def h(*args: X.args, **kwargs: X.kwargs) -> U:
            return g(self(*args, **kwargs))

        return XFunc(h)

    def contramap[**T, XX](self: "XFunc[[XX], Y]", g: Callable[T, XX]) -> "XFunc[T, Y]":
        """Pipe another function directly before self.f.

        ## Arguments

        - self: retrained on XFunc with a unique input parameter
        - g: the function to be called before f

        ## Usage

        ```python
            from typing import TYPE_CHECKING, reveal_type
            from xfp import XFunc

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
