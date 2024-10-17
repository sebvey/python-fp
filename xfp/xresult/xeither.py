from dataclasses import dataclass
from typing import Any, ParamSpec, TypeVar
from xfp.xresult._xresult import Xresult, XRBranch

P = ParamSpec("P")
X = TypeVar("X")


class Xeither:
    """Common tools to instantiate and pattern match Xresult.

    ### Provides

    Proxy classes to quickly instantiate LEFT and RIGHT.
    Approximately makes Xresult(..., XRBranch.LEFT) and Xresult(..., XRBranch.RIGHT) independent classes.

    ### Usage

    ```python
        regular_result: Xresult[None, Any] = Xresult(None, XRBranch.LEFT)
        either_result: Xresult[Any, Int] = Xeither.Right(3)

        match either_result:
            case Xeither.Right(value):
                print(value)
            case Xeither.Left(_):
                print("no value")

        # You can also pattern match regular Xresult with Left/Right
        match regular_result:
            case Xeither.Right(value):
                print(value)
            case Xeither.Left(_):
                print("no value")
    ```
    """

    class XresultLeftMeta(type):
        """Metaclass to interprets Left as an Xresult[Any, X].

        Overrides the instanceof in order to enable pattern matching between Left and Xresult.
        """

        def __instancecheck__(self, instance):
            return isinstance(instance, Xresult) and instance.branch == XRBranch.LEFT

    @dataclass(frozen=True, init=False, match_args=False, eq=False)
    class Left[Y](Xresult[Y, Any], metaclass=XresultLeftMeta):
        """Specific result holding a LEFT.

        Can also act as an extractor in pattern matching.
        """

        __match_args__ = ("value",)  # type: ignore
        value: Y

        def __init__(self, value):
            super().__init__(value, XRBranch.LEFT)

    class XresultRightMeta(type):
        """Metaclass to interprets Right as an Xresult[Any, X].

        Overrides the instanceof in order to enable pattern matching between Right and Xresult.
        """

        def __instancecheck__(self, instance):
            return isinstance(instance, Xresult) and instance.branch == XRBranch.RIGHT

    @dataclass(frozen=True, init=False, match_args=False, eq=False)
    class Right[X](Xresult[Any, X], metaclass=XresultRightMeta):
        """Specific result holding a RIGHT.

        Can also act as an extractor in pattern matching.
        """

        __match_args__ = ("value",)  # type: ignore
        value: X

        def __init__(self, value):
            super().__init__(value, XRBranch.RIGHT)
