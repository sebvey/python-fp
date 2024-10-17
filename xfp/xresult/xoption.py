from dataclasses import dataclass
from typing import Any
from xfp.xresult._xresult import Xresult, XRBranch
from xfp.xresult.xeither import Xeither


class Xopt:
    """Common tools to instantiate and pattern match Xresult[None, X].

    ### Provides

    - methods to formalize Optional values
    - value Empty and type Some, interpretables as Xresult, and usable as Xresult pattern matching

    ### Usage

    ```python
        regular_result: Xresult[None, Any] = Xresult(None, XRBranch.LEFT)
        optional_result: Xresult[None, Int] = Xopt.from_optional(3)

        match optional_result:
            case Xopt.Some(value):
                print(value)
            case Xopt.Empty:
                print("no value")

        # You can also pattern match regular Xresult with Some/Empty
        match regular_result:
            case Xopt.Some(value):
                print(value)
            case Xopt.Empty:
                print("no value")
    ```
    """

    @classmethod
    def from_optional[X](cls, value: None | X) -> Xresult[None, X]:
        """Return an Xresult from an optional value.

        value:
        - X    -- Return a Xopt.Some
        - None -- Return Xopt.Empty
        """
        match value:
            case None:
                return cls.Empty
            case _:
                return cls.Some(value)

    Empty: Xresult[None, Any] = Xeither.Left(None)

    class XresultMeta(type):
        """Metaclass to interprets Some as an Xresult[None, X].

        Overrides the instanceof in order to enable pattern matching between Some and Xresult.
        """

        def __instancecheck__(self, instance):
            return isinstance(instance, Xeither.Right)

    @dataclass(frozen=True, init=False, match_args=False, eq=False)
    class Some[X](Xresult[None, X], metaclass=XresultMeta):
        """Specific result holding a value, with alternate path being None.

        Can also act as an extractor in pattern matching.
        """

        __match_args__ = ("value",)  # type: ignore
        value: X

        def __init__(self, value):
            super().__init__(value, XRBranch.RIGHT)
