from typing import Any, Iterator, Never, cast
from enum import Enum, auto
from dataclasses import dataclass
from xfp.functions import F0, F1, curry_method2


class XRBranch(Enum):
    LEFT = auto()
    RIGHT = auto()

    def invert(self) -> "XRBranch":
        return XRBranch.RIGHT if self == XRBranch.LEFT else XRBranch.LEFT


@dataclass(init=False)
class XresultError[Y, X](Exception):
    xresult: "Xresult[Y, X]"

    def __init__(self, xresult: "Xresult[Y, X]"):
        self.xresult = xresult
        super().__init__(f"Auto generated error for initial result {self.xresult}")


@dataclass(frozen=True)
class Xresult[Y, X]:
    """Encapsulate Union type in container.

    Semantically, Xresult helps managing unpure types, such as :
    - nullable values (Xresult[None, X])
    - tryable values (Xresult[Error, X])

    Eventually using it for plain encapsulated Union type is fine.

    ### Attributes

    - branch -- XRBranch (LEFT, RIGHT), semaphore telling if the value attribute is an X (LEFT) or a Y (RIGHT)
    - value  -- Y | X, the content of the container

    ### Features

    - Monadic behavior
    - Manual handling of the bias
    - Class method to lift values to Xresult

    ### Helper classes

    Helper classes are provided to semantically instantiate / pattern match your Xresults.
    See Xeither, Xtry, Xopt for more information.

    ### Usages
    - directly returns Xresult in your own functions:

    ```python
        def f_that_breaks(should_break: bool) -> Xresult[Exception, str]:
            if should_break:
                return Xresult(Exception("something went wrong"), XRBranch.LEFT)
            else:
                return Xresult("Everything's fine", XRBranch.RIGHT)
    ```

    - catch common functions into Xresult:

    ```python
        effect_result: Xresult[Exception, E] = Xtry.from_unsafe(some_function_that_raises)
    ```

    - powerful optional handling:

    ```python
        optional_value: int | None = 3
        option_value: Xresult[None, int] = Xopt.from_optional(optional_value)
    ```

    - rich union type:

    ```python
        def returns_a_str_or_int(should_be_str: boolean) -> Xresult[str, int]:
            if should_be_str:
                return Xresult("foo", XRBranch.LEFT)
            else:
                return Xresult(42, XRBranch.RIGHT)
    ```
    """

    value: Y | X
    branch: XRBranch

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, Xresult)
            and self.value == value.value
            and self.branch == value.branch
        )

    def __repr__(self) -> str:
        return f"{self.branch} : {self.value}"

    def __iter__(self) -> Iterator[X]:
        """Return a tri-state iterator of this Xresult.

        Exists as a syntax enhancer in co-usage with `Xresult.fors`.
        No usage of this iterator should be done outside of it since empty iterator will raise instead of stop.
        Used to compose right pathes together.

        ### Next values

        - if branch = LEFT : raise an Exception wrapping the Xresult to be caught in `Xresult.fors`
        - if branch = RIGHT : return self.value
        - if branch = RIGHT (next already called) : raise StopIteration
        """

        class Internal(Iterator[X]):
            def __init__(self):
                self.called = False

            def __next__(selff) -> X:
                if selff.called:
                    raise StopIteration
                if self.branch == XRBranch.RIGHT:
                    selff.called = True
                    return cast(X, self.value)
                raise XresultError(self)

        return Internal()

    @staticmethod
    def fors[T](els: "F0[list[T]]") -> "Xresult[XresultError, T]":
        """Return the Xresult computed in a list comprehension of zipped Xresult.

        Used as a complement of __iter__ to compose multiple results together.

        ### Keyword Arguments

        - els: lazy list of zero or one element. To be mecanically useful, should be computed as a list comprehension.

        ### Usage

        ```python
            # Return Xresult(6, XRBranch.RIGHT)
            Xresult.fors(lambda:          # lambda to make the computation lazy
                [
                    x + y + z             # put here your algorithm for composing effect results
                    for x, y, z
                    in zip(               # Chain your effects results in a zip
                        Xeither.Right(1),
                        Xeither.Right(2),
                        Xeither.Right(3)
                    )
                ]
            )

            # If at least one XResult has a different branch than requested, stop at the first encountered
            # Return Xresult(2, XRBranch.LEFT)
            Xresult.fors(lambda:
                [
                    x + y + z
                    for x, y, z
                    in zip(
                        Xeither.Right(1),
                        Xeither.Left(2),
                        Xeither.Right(3)
                    )
                ]
            )
        ```
        """
        try:
            if isinstance(value := els()[0], Xresult):
                return value
            else:
                return Xresult(value, XRBranch.RIGHT)
        except XresultError as e:
            return Xresult(e, XRBranch.LEFT)

    def map[T](self, f: F1[[X], T]) -> "Xresult[Y, T]":
        """Alias for map_right."""
        return self.map_right(f)

    def map_left[U](self, f: F1[[Y], U]) -> "Xresult[U, X]":
        """Return either itself or a new Xresult (LEFT) containing the result of f.

        Is mainly used to chain effect free operations.

        ### Return

        - if self is a RIGHT -- self
        - if self is a LEFT  -- a new Xresult, being a copy of the current result with the underlying value = f(self.value)

        ### Usage

        see map_right
        """
        match self:
            case Xresult(value, XRBranch.LEFT):
                return Xresult[U, Never](f(cast(Y, value)), XRBranch.LEFT)
            case _:
                return cast(Xresult[Never, X], self)

    def map_right[T](self, f: F1[[X], T]) -> "Xresult[Y, T]":
        """Return either itself or a new Xresult (RIGHT) containing the result of f.

        ### Return

        - if self is a LEFT  -- self
        - if self is a RIGHT -- a new Xresult, being a copy of the current result with the underlying value = f(self.value)

        ### Usage

        ```python
            def add_three(i: float) -> float:
                return i + 3

            def pow(i: float) -> float:
                return i * i

            (
                Xopt
                    .from_optional(3)            # Xresult(3, XRBranch.RIGHT)
                    .map_right(add_three)        # Xresult(6, XRBranch.RIGHT)
                    .map_right(pow)              # Xresult(36, XRBranch.RIGHT)
                    .map_right(lambda x: x - 4)  # Xresult(32, XRBranch.RIGHT)
            )
        ```
        """
        match self:
            case Xresult(value, XRBranch.RIGHT):
                return Xresult[Never, T](f(cast(X, value)), XRBranch.RIGHT)
            case _:
                return cast(Xresult[Y, Never], self)

    def flatten[YS, U, XS](
        self: "Xresult[YS, Xresult[U, XS]]",
    ) -> "Xresult[YS, Never] | Xresult[U, XS]":
        """Alias for flatten_right."""
        return self.flatten_right()

    def flatten_left[YS, T, XS](
        self: "Xresult[Xresult[YS, T], XS]",
    ) -> "Xresult[YS, T] | Xresult[Never, XS]":
        """Return either self or a new flat Xresult if the underlying value is an Xresult.

        ### Return

        - if self.value is an Xresult, and branch = LEFT -- a new Xresult being the underlying value
        - otherwise                                      -- self

        ### Usage

        see flatten_right
        """
        match self:
            case Xresult(value, XRBranch.LEFT):
                return cast(Xresult[YS, T], value)
            case _:
                return cast(Xresult[Never, XS], self)

    def flatten_right[YS, U, XS](
        self: "Xresult[YS, Xresult[U, XS]]",
    ) -> "Xresult[YS, Never] | Xresult[U, XS]":
        """Return either self or a new flat Xresult if the underlying value is an Xresult.

        ### Return

        - if self.value is an Xresult, and branch = RIGHT -- a new Xresult being the underlying value
        - otherwise                                       -- self

        ### Usage

        ```python
            assert Xresult.right(Xresult.right("example")).flatten_right() == Xresult("example", XRBranch.RIGHT)
            assert Xresult.right("example").flatten_right() == Xresult("example", XRBranch.RIGHT)
            assert Xresult.right(Xopt.from_optional(None)).flatten_right() == Xresult(None, XRBranch.LEFT)
            assert Xresult.right(Xresult.left("example")).flatten_right() == Xresult("example", XRBranch.LEFT)
        ```
        """
        match self:
            case Xresult(value, XRBranch.RIGHT):
                return cast(Xresult[U, XS], value)
            case _:
                return cast(Xresult[YS, Never], self)

    def flat_map[T, U](
        self, f: "F1[[X], Xresult[U, T]]"
    ) -> "Xresult[Y, Never] | Xresult[U, T]":
        """Alias for flat_map_right."""
        return self.flat_map_right(f)

    def flat_map_left[T, U](
        self, f: "F1[[Y], Xresult[U, T]]"
    ) -> "Xresult[U, T] | Xresult[Never, X]":
        """Return the result of map_left then flatten.

        ### Return

        - if self is a RIGHT -- self
        - if self is a LEFT  -- a new Xresult, map_left then flatten

        ### Usage

        see flat_map
        """
        return self.map_left(f).flatten_left()

    def flat_map_right[T, U](
        self, f: "F1[[X], Xresult[U, T]]"
    ) -> "Xresult[Y, Never] | Xresult[U, T]":
        """Return the result of map_right then flatten.

        ### Return

        - if self is a LEFT  -- self
        - if self is a RIGHT -- a new Xresult, map_right then flatten

        ### Usage

        ```python
            from xfp import Xtry
            import math

            @Xtry.safed
            def invert(i: float) -> float:
                return 1 / i

            @Xtry.safed
            def sqrt(i: float) -> float:
                return math.sqrt(i)

            (
                Xtry
                    .Success(4)             # Xresult(4, XRBranch.RIGHT)
                    .flat_map_right(invert) # Xresult(0.25, XRBranch.RIGHT)
                    .flat_map_right(sqrt)   # Xresult(0.5, XRBranch.RIGHT)
            )
            (
                Xtry
                    .Success(0)              # Xresult(0, XRBranch.RIGHT)
                    .flat_map_right(invert) # Xresult(ZeroDivisionError(..., XRBranch.LEFT))
                    .flat_map_right(sqrt)   # Xresult(ZeroDivisionError(..., XRBranch.LEFT))
            )
            (
                Xtry
                    .Success(-4)            # Xresult(-4, XRBranch.RIGHT)
                    .flat_map_right(invert) # Xresult(-0.25, XRBranch.RIGHT)
                    .flat_map_right(sqrt)   # Xresult(ValueError(..., XRBranch.LEFT))
            )
        """
        return self.map_right(f).flatten_right()

    @curry_method2
    def fold[T, TT](self, default: TT, f: F1[[X], T]) -> T | TT:
        """Return default if branch != RIGHT, otherwise f(self.value).

        Exists as homogenisation with Xlist.fold

        ### Keyword Arguments

        - default -- output when the value does not exist on the RIGHT side
        - f       -- transformation to apply to the underlying value before returning
                     when the value is present on the RIGHT side

        ### Usage

        ```python
            from xfp import Xtry
            from datetime import date

            def load_dated_partition(partition_value: date) -> str:
                return "actual partition"


            @Xtry.safed
            def to_date(str_date: str) -> date:
                print(date.fromisoformat(str_date))
                return date.fromisoformat(str_date)

            data = to_date("2024-05-01").fold("default partition")(load_dated_partition)
            # good date -> date parsed by to_date() -> fold() calls load_dated_partition

            data = to_date("2023-02-29").fold("default partition")(load_dated_partition)
            # wrong date -> LEFT bias returned by to_date() -> fold returns "default partition"
        ```
        """
        if self.branch == XRBranch.RIGHT:
            return f(cast(X, self.value))
        else:
            return default

    def get_or_else[T](self, default: T) -> X | T:
        """Shorthand for self.fold(default)(id)

        ### Usage
        ```python
            from xfp import Xtry
            from datetime import date

            @Xtry.safed
            def to_date(str_date: str) -> date:
                return date.fromisoformat(str_date)

            gotten_date = to_date("2024-05-01").get_or_else(date.today())
            else_date   = to_date("2023-02-29").get_or_else(date.today())
        ```
        """
        return self.fold(default)(lambda x: x)

    def foreach(self, statement: F1[[X], Any]) -> None:
        """Alias for foreach_right."""
        self.foreach_right(statement)

    def foreach_left(self, statement: F1[[Y], Any]) -> None:
        """Do the statement procedure to the underlying value if self is a LEFT.

        ### Usage

        see foreach_right
        """
        if self.branch == XRBranch.LEFT:
            statement(cast(Y, self.value))

    def foreach_right(self, statement: F1[[X], Any]) -> None:
        """Do the statement procedure to the underlying value if self is a RIGHT.

        ### Usage
        ```python
            from xfp import Xresult,XRBranch,Xopt

            (
                Xopt
                    .from_optional(25)
                    .foreach(lambda x: print(f"This is an element of the list : {x}"))
            )
            # This is an element of the list : 25

            (
                Xopt
                    .from_optional(None)
                    .foreach(lambda x: print(f"This is the element : {x}"))
            )
            # doesn't output anything

            (
                Xresult(42, XRBranch.RIGHT)
                    .foreach(lambda x: print(f"This is the right element : {x}"))
            )
            # This is the right element : 42

            (
                Xresult(666, XRBranch.LEFT)
                    .foreach(lambda x: print(f"This is the right element : {x}"))
            )
            # doesn't output anything
        ```
        """
        if self.branch == XRBranch.RIGHT:
            statement(cast(X, self.value))

    def recover_with[T, U](
        self, f: "F1[[Y], Xresult[U, T]]"
    ) -> "Xresult[U, T] | Xresult[Never, X]":
        """Alias for recover_with_right."""
        return self.recover_with_right(f)

    def recover_with_left[T, U](
        self, f: "F1[[X], Xresult[U, T]]"
    ) -> "Xresult[Y, Never] | Xresult[U, T]":
        """Return itself, mapped on the right side, flattened on the left side.

        See flat_map_right

        ### Usage

        See recover_with_right
        """
        match self:
            case Xresult(v, XRBranch.RIGHT):
                return f(cast(X, v))
            case _:
                return cast(Xresult[Y, Never], self)

    def recover_with_right[T, U](
        self, f: "F1[[Y], Xresult[U, T]]"
    ) -> "Xresult[U, T] | Xresult[Never, X]":
        """Return itself, mapped on the left side, flattened on the right side.

        See flat_map_left

        ### Usage

        ```python
            from xfp import Xtry
            import math

            @Xtry.safed
            def invert(i: float) -> float:
                return 1 / i

            @Xtry.safed
            def sqrt(i: float) -> float:
                return math.sqrt(i)

            (
                sqrt(-4)                                      # Xresult(ValueError(...), XRBranch.LEFT)
                    .recover_with_right(lambda _: invert(-4)) # Xresult(-0.25, XRBranch.RIGHT)
            )

            (
                sqrt(4)                                       # Xresult(2, XRBranch.RIGHT)
                    .recover_with_right(lambda _: invert(-4)) # Xresult(2, XRBranch.RIGHT)
            )
        ```
        """
        match self:
            case Xresult(v, XRBranch.LEFT):
                return f(cast(Y, v))
            case _:
                return cast(Xresult[Never, X], self)

    def recover[T](self, f: F1[[Y], T]) -> "Xresult[Never, X | T]":
        """Alias for recover_right."""
        return self.recover_right(f)

    def recover_left[U](self, f: F1[[X], U]) -> "Xresult[Y | U, Never]":
        """Return a new Xresult with is always a LEFT.

        Used to convert a RIGHT result into a LEFT using an effectless transformation.
        Semantically :
        Used to fallback from a potential success with an effectless operation.
        This is a fallback that always ends up as a 'failure'.

        ### Return

        - if branch == LEFT -- self
        - otherwise         -- a new Xresult, having branch = LEFT, with an inherent value of f(self.value)

        ### Usage

        See recover_right
        """
        match self:
            case Xresult(v, XRBranch.RIGHT):
                return Xresult(f(cast(X, v)), XRBranch.LEFT)
            case _:
                return cast(Xresult[Y, Never], self)

    def recover_right[T](self, f: F1[[Y], T]) -> "Xresult[Never, T | X]":
        """Return a new Xresult with is always a RIGHT.

        Used to convert a LEFT result into a RIGHT using an effectless transformation.
        Semantically :
        Used to fallback from a potential failure with an effectless operation.
        This is a fallback that always ends up as a 'success'.

        ### Return

        - if branch == RIGHT -- self
        - otherwise          -- a new Xresult, having branch = RIGHT, with an inherent value of f(self.value)

        ### Usage

        ```python
            from xfp import Xtry
            import math

            @Xtry.safed
            def sqrt(i: float) -> float:
                return math.sqrt(i)

            (
                sqrt(-4)                        # Xresult(ValueError(...), XRBranch.LEFT)
                    .recover_right(lambda _: 0) # Xresult(0, XRBranch.RIGHT)
            )
            (
                sqrt(4)                         # Xresult(2, XRBranch.RIGHT)
                    .recover_right(lambda _: 0) # Xresult(2.0, XRBranch.RIGHT)
            )
        ```
        """
        match self:
            case Xresult(v, XRBranch.LEFT):
                return Xresult(f(cast(Y, v)), XRBranch.RIGHT)
            case _:
                return cast(Xresult[Never, X], self)

    def filter(
        self, predicate: F1[[X], bool]
    ) -> "Xresult[Y, Never] | Xresult[XresultError, X]":
        """Alias for filter_right."""
        return self.filter_right(predicate)

    def filter_left(
        self, predicate: F1[[Y], bool]
    ) -> "Xresult[Y, XresultError] | Xresult[Never, X]":
        """Return a new Xresult with the branch = RIGHT if the predicate is not met.

        Fill the result with a default error mentioning the initial value in case of branch switching.

        ### Return

        - if branch != LEFT               -- self
        - if branch == LEFT and predicate -- self
        - otherwise                       -- a new Xresult, having branch = RIGHT, with value = XresultError(self)

        ### Usage

        see filter_right
        """
        match self.map_left(predicate):
            case Xresult(True, XRBranch.LEFT) | Xresult(_, XRBranch.RIGHT):
                return cast(Xresult[Never, X], self)
            case _:
                return Xresult[Y, XresultError](XresultError(self), XRBranch.RIGHT)

    def filter_right(
        self, predicate: F1[[X], bool]
    ) -> "Xresult[Y, Never] | Xresult[XresultError, X]":
        """Return a new Xresult with the branch = LEFT if the predicate is not met.

        Fill the result with a default error mentioning the initial value in case of branch switching.

        ### Return

        - if branch != RIGHT               -- self
        - if branch == RIGHT and predicate -- self
        - otherwise                       -- a new Xresult, having branch = LEFT, with value = XresultError(self)

        ### Usage

        ```python

            (
                Xresult
                    .right(4)                 # Xresult(4, XRBranch.RIGHT)
                    .filter(lambda x: x < 10) # Xresult(4, XRBranch.RIGHT)
                    .filter(lambda x: x > 10) # Xresult(
                                              #   XresultError(Xresult(4,XRBranch.RIGHT)),
                                              #   XRBranch.LEFT
                                              # )
                    .filter(lambda _: True)   # no change, we are now on the LEFT branch
            )
        ```
        """
        match self.map_right(predicate):
            case Xresult(True, XRBranch.RIGHT) | Xresult(_, XRBranch.LEFT):
                return cast(Xresult[Y, Never], self)
            case _:
                return Xresult[XresultError, X](XresultError(self), XRBranch.LEFT)
