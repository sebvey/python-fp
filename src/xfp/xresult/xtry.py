from dataclasses import dataclass
from typing import Any, Callable, ParamSpec, TypeVar
from xfp.xresult._xresult import Xresult, XRBranch
from xfp.xresult.xeither import Xeither

P = ParamSpec("P")
X = TypeVar("X")


class Xtry:
    """Common tools to instantiate and pattern match Xresult[Exception, X].

    ### Provides

    - methods to secure failable functions
    - types Success and Failure, instantiable as Xresult, and usable as Xresult pattern matching

    ### Usage

    ```python
        regular_result: Xresult[Exception, Any] = Xresult(Exception("Something went wrong"), XRBranch.LEFT)
        try_result: Xresult[Exception, Int] = Xtry.Success(3)

        match try_result:
            case Xtry.Success(value):
                print(value)
            case Xtry.Failure(e):
                raise e

        # You can also pattern match regular Xresult with Success/Failure
        match regular_result:
            case Xtry.Success(value):
                print(value)
            case Xtry.Failure(e):
                raise e
    ```
    """

    @classmethod
    def from_unsafe(cls, f: Callable[[], X]) -> Xresult[Exception, X]:
        """Return the result of a function as an Xresult.

        Execute the callable and catch the result :
        - Callable returns -- wrap the result in a RIGHT
        - Callable raises  -- wrap the Exception in a LEFT

        ### Usage

        ```python
            def unsafe_function(param: str) -> int:
                if param == "":
                    raise Exception("error")
                return 3

            a: Xresult[Exception, int] = Xtry.from_unsafe(lambda: unsafe_function("foo"))
        ```
        """
        try:
            return cls.Success(f())
        except Exception as e:
            return cls.Failure(e)

    @classmethod
    def safed(cls, f: Callable[P, X]) -> Callable[P, Xresult[Exception, X]]:
        """Return a new function being f with the side effect wrapped.

        Used as a decorator for quickly converting unsafe code into safe one.
        Downside is there is no fine tuning over the caught exception.

        ### Usage

        ```python
            @Xtry.safed
            def unsafe_function(param: str) -> int:
                if param == "":
                    raise Exception("error")
                return 3

            a: Xresult[Exception, int] = unsafe_function("foo")
        ```
        """

        def inner(*args: P.args, **kwargs: P.kwargs) -> Xresult[Exception, X]:
            return cls.from_unsafe(lambda: f(*args, **kwargs))

        return inner

    class XresultFailureMeta(type):
        """Metaclass to interprets Failure as an Xresult[Exception, Any].

        Overrides the instanceof in order to enable pattern matching between Failure and Xresult.
        """

        def __instancecheck__(self, instance):
            return isinstance(instance, Xeither.Left) and isinstance(
                instance.value, Exception
            )

    @dataclass(frozen=True, init=False, match_args=False, eq=False)
    class Failure[Y: Exception](Xresult[Y, Any], metaclass=XresultFailureMeta):
        """Specific result holding an exception.

        Can also act as an extractor in pattern matching.
        """

        __match_args__ = ("value",)  # type: ignore
        value: Y

        def __init__(self, value):
            super().__init__(value, XRBranch.LEFT)

    class XresultSuccessMeta(type):
        """Metaclass to interprets Success as an Xresult[Any, X].

        Overrides the instanceof in order to enable pattern matching between Success and Xresult.
        """

        def __instancecheck__(self, instance):
            return isinstance(instance, Xeither.Right)

    @dataclass(frozen=True, init=False, match_args=False, eq=False)
    class Success[X](Xresult[Exception, X], metaclass=XresultSuccessMeta):
        """Specific result holding a value, with alternate path being an exception.

        Can also act as an extractor in pattern matching.
        """

        __match_args__ = ("value",)  # type: ignore
        value: X

        def __init__(self, value):
            super().__init__(value, XRBranch.RIGHT)
