from dataclasses import dataclass
from typing import Any, Callable, ParamSpec, TypeVar
from xfp.xeffect._xeffect import Xeffect, XFXBranch
from xfp.xeffect.xeither import XEither

P = ParamSpec("P")
X = TypeVar("X")


class XTry:
    """Common tools to instantiate and pattern match Xeffect[Exception, X].

    ### Provides

    - methods to secure failable functions
    - types Success and Failure, instantiable as Xeffect, and usable as Xeffect pattern matching

    ### Usage

    ```python
        regular_effect: Xeffect[Exception, Any] = Xeffect(Exception("Something went wrong"), XFXBranch.LEFT)
        try_effect: Xeffect[Exception, Int] = XTry.Success(3)

        match try_effect:
            case XTry.Success(value):
                print(value)
            case XTry.Failure(e):
                raise e

        # You can also pattern match regular Xeffect with Success/Failure
        match regular_effect:
            case XTry.Success(value):
                print(value)
            case XTry.Failure(e):
                raise e
    ```
    """

    @classmethod
    def from_unsafe(cls, f: Callable[[], X]) -> Xeffect[Exception, X]:
        """Return the result of a function as an Xeffect.

        Execute the callable and catch the result :
        - Callable returns -- wrap the result in a RIGHT
        - Callable raises  -- wrap the Exception in a LEFT

        ### Usage

        ```python
            def unsafe_function(param: str) -> int:
                if param == "":
                    raise Exception("error")
                return 3

            a: Xeffect[Exception, int] = XTry.from_unsafe(lambda: unsafe_function("foo"))
        ```
        """
        try:
            return cls.Success(f())
        except Exception as e:
            return cls.Failure(e)

    @classmethod
    def safed(cls, f: Callable[P, X]) -> Callable[P, Xeffect[Exception, X]]:
        """Return a new function being f with the side effect wrapped.

        Used as a decorator for quickly converting unsafe code into safe one.
        Downside is there is no fine tuning over the caught exception.

        ### Usage

        ```python
            @XTry.safed
            def unsafe_function(param: str) -> int:
                if param == "":
                    raise Exception("error")
                return 3

            a: Xeffect[Exception, int] = unsafe_function("foo")
        ```
        """

        def inner(*args: P.args, **kwargs: P.kwargs) -> Xeffect[Exception, X]:
            return cls.from_unsafe(lambda: f(*args, **kwargs))

        return inner

    class XeffectFailureMeta(type):
        """Metaclass to interprets Failure as an Xeffect[Exception, Any].

        Overrides the instanceof in order to enable pattern matching between Failure and Xeffect.
        """

        def __instancecheck__(self, instance):
            return isinstance(instance, XEither.Left) and isinstance(
                instance.value, Exception
            )

    @dataclass(frozen=True, init=False, match_args=False, eq=False)
    class Failure[Y: Exception](Xeffect[Y, Any], metaclass=XeffectFailureMeta):
        """Specific effect holding an exception.

        Can also act as an extractor in pattern matching.
        """

        __match_args__ = ("value",)  # type: ignore
        value: Y

        def __init__(self, value):
            super().__init__(value, XFXBranch.LEFT)

    class XeffectSuccessMeta(type):
        """Metaclass to interprets Success as an Xeffect[Any, X].

        Overrides the instanceof in order to enable pattern matching between Success and Xeffect.
        """

        def __instancecheck__(self, instance):
            return isinstance(instance, XEither.Right)

    @dataclass(frozen=True, init=False, match_args=False, eq=False)
    class Success[X](Xeffect[Exception, X], metaclass=XeffectSuccessMeta):
        """Specific effect holding a value, with alternate path being an exception.

        Can also act as an extractor in pattern matching.
        """

        __match_args__ = ("value",)  # type: ignore
        value: X

        def __init__(self, value):
            super().__init__(value, XFXBranch.RIGHT)
