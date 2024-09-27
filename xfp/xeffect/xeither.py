from dataclasses import dataclass
from typing import Any, ParamSpec, TypeVar
from xfp.xeffect._xeffect import Xeffect, XFXBranch

P = ParamSpec("P")
X = TypeVar("X")


class XEither:
    """Common tools to instantiate and pattern match Xeffect.

    ### Provides

    Proxy classes to quickly instantiate LEFT and RIGHT.
    Approximately makes Xeffect(..., XFXBranch.LEFT) and Xeffect(..., XFXBranch.RIGHT) independent classes.

    ### Usage

    ```python
        regular_effect: Xeffect[None, Any] = Xeffect(None, XFXBranch.LEFT)
        either_effect: Xeffect[Any, Int] = XEither.Right(3)

        match either_effect:
            case XEither.Right(value):
                print(value)
            case XEither.Left(_):
                print("no value")

        # You can also pattern match regular Xeffect with Left/Right
        match regular_effect:
            case XEither.Right(value):
                print(value)
            case XEither.Left(_):
                print("no value")
    ```
    """

    class XeffectLeftMeta(type):
        """Metaclass to interprets Left as an Xeffect[Any, X].

        Overrides the instanceof in order to enable pattern matching between Left and Xeffect.
        """

        def __instancecheck__(self, instance):
            return isinstance(instance, Xeffect) and instance.branch == XFXBranch.LEFT

    @dataclass(frozen=True, init=False, match_args=False, eq=False)
    class Left[Y](Xeffect[Y, Any], metaclass=XeffectLeftMeta):
        """Specific effect holding a LEFT.

        Can also act as an extractor in pattern matching.
        """

        __match_args__ = ("value",)  # type: ignore
        value: Y

        def __init__(self, value):
            super().__init__(value, XFXBranch.LEFT)

    class XeffectRightMeta(type):
        """Metaclass to interprets Right as an Xeffect[Any, X].

        Overrides the instanceof in order to enable pattern matching between Right and Xeffect.
        """

        def __instancecheck__(self, instance):
            return isinstance(instance, Xeffect) and instance.branch == XFXBranch.RIGHT

    @dataclass(frozen=True, init=False, match_args=False, eq=False)
    class Right[X](Xeffect[Any, X], metaclass=XeffectRightMeta):
        """Specific effect holding a RIGHT.

        Can also act as an extractor in pattern matching.
        """

        __match_args__ = ("value",)  # type: ignore
        value: X

        def __init__(self, value):
            super().__init__(value, XFXBranch.RIGHT)
