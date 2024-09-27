from dataclasses import dataclass
from typing import Any
from xfp.xeffect._xeffect import Xeffect, XFXBranch
from xfp.xeffect.xeither import XEither


class XOpt:
    """Common tools to instantiate and pattern match Xeffect[None, X].

    ### Provides

    - methods to formalize Optional values
    - value Empty and type Some, interpretables as Xeffect, and usable as Xeffect pattern matching

    ### Usage

    ```python
        regular_effect: Xeffect[None, Any] = Xeffect(None, XFXBranch.LEFT)
        optional_effect: Xeffect[None, Int] = XOpt.from_optional(3)

        match optional_effect:
            case XOpt.Some(value):
                print(value)
            case XOpt.Empty:
                print("no value")

        # You can also pattern match regular Xeffect with Some/Empty
        match regular_effect:
            case XOpt.Some(value):
                print(value)
            case XOpt.Empty:
                print("no value")
    ```
    """

    @classmethod
    def from_optional[X](cls, value: None | X) -> Xeffect[None, X]:
        """Return an Xeffect from an optional value.

        value:
        - X    -- Return a XOpt.Some
        - None -- Return XOpt.Empty
        """
        match value:
            case None:
                return cls.Empty
            case _:
                return cls.Some(value)

    Empty: Xeffect[None, Any] = XEither.Left(None)

    class XeffectMeta(type):
        """Metaclass to interprets Some as an Xeffect[None, X].

        Overrides the instanceof in order to enable pattern matching between Some and Xeffect.
        """

        def __instancecheck__(self, instance):
            return isinstance(instance, XEither.Right)

    @dataclass(frozen=True, init=False, match_args=False, eq=False)
    class Some[X](Xeffect[None, X], metaclass=XeffectMeta):
        """Specific effect holding a value, with alternate path being None.

        Can also act as an extractor in pattern matching.
        """

        __match_args__ = ("value",)  # type: ignore
        value: X

        def __init__(self, value):
            super().__init__(value, XFXBranch.RIGHT)
