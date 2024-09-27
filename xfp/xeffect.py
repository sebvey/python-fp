from typing import Callable, Any, Self, ParamSpec
from enum import Enum, auto
from dataclasses import dataclass
from .utils import E, curry_method


P = ParamSpec("P")


class XFXBranch(Enum):
    LEFT = auto()
    RIGHT = auto()

    def invert(self) -> "XFXBranch":
        return XFXBranch.RIGHT if self == XFXBranch.LEFT else XFXBranch.LEFT


@dataclass(init=False)
class XeffectError(Exception):
    xeffect: "Xeffect[E, E]"

    def __init__(self, xeffect: "Xeffect[E, E]"):
        self.xeffect = xeffect
        super().__init__(f"Auto generated error for initial effect {self.xeffect}")


@dataclass(frozen=True)
class Xeffect[Y: E, X: E]:
    """Encapsulate Union type in container.

    Semantically, Xeffect helps managing unpure types, such as :
    - nullable values (Xeffect[None, X])
    - tryable values (Xeffect[Error, X])

    Eventually using it for plain encapsulated Union type is fine.

    ### Attributes

    - branch -- XFXBranch (LEFT, RIGHT), semaphore telling if the value attribute is an X (LEFT) or a Y (RIGHT)
    - value  -- Y | X, the content of the container

    ### Features

    - Monadic behavior
    - Manual handling of the bias
    - Class method to lift values to Xeffect

    ### Usages
    - directly returns Xeffect in your own functions:

    ```python
        def f_that_breaks(should_break: bool) -> Xeffect[Error, str]:
            if should_break:
                return Xeffect(XFXBranch.LEFT, Error("something went wrong"))
            else:
                return Xeffect(XFXBranch.RIGHT, "Everything's fine")
    ```

    - catch common functions into Xeffect:

    ```python
        effect_result: Xeffect[Error, E] = Xeffect.from_unsafe(some_function_that_raises)
    ```

    - powerful optional handling:

    ```python
        optional_value: int | None = 3
        option_value: Xeffect[None, int] = Xeffect.from_optional(optional_value)
    ```

    - rich union type:

    ```python
        def returns_a_str_or_int(should_be_str: boolean) -> Xeffect[str, int]:
            if should_be_str:
                return Xeffect(XFXBranch.LEFT, "foo")
            else:
                return Xeffect(XFXBranch.RIGHT, 42)
    ```
    """

    branch: XFXBranch
    value: Y | X

    @classmethod
    def right(cls, value: X) -> "Xeffect[E, X]":
        """Return an Xeffect (always RIGHT) from a value."""
        return Xeffect(XFXBranch.RIGHT, value)

    @classmethod
    def left(cls, value: Y) -> "Xeffect[Y, E]":
        """Return an Xeffect (always LEFT) from a value."""
        return Xeffect(XFXBranch.LEFT, value)

    @classmethod
    def from_optional(cls, value: None | X) -> "Xeffect[None, X]":
        """Return an Xeffect from an optional value.

        value:
        - X    -- Return a RIGHT
        - None -- Return a LEFT
        """
        match value:
            case None:
                return Xeffect.left(value)
            case _:
                return Xeffect.right(value)

    @classmethod
    def from_unsafe(cls, f: Callable[[], X]) -> "Xeffect[Exception, X]":
        """Return the result of a function as an Xeffect.

        Execute the callable and catch the result :
        - Callable returns -- wrap the result in a RIGHT
        - Callable raises  -- wrap the Exception in a LEFT
        """
        try:
            return Xeffect.right(f())
        except Exception as e:
            return Xeffect.left(e)

    @classmethod
    def safed(cls, f: Callable[P, X]) -> Callable[P, "Xeffect[Exception, X]"]:
        """Return a new function being f with the side effect wrapped.

        Used as a decorator for quickly converting unsafe code into safe one.
        Downside is there is no fine tuning over the caught exception.

        ### Usage

        ```python
            @Xeffect.safed
            def unsafe_function(param: str) -> int:
                if param == "":
                    raise Exception("error")
                return 3

            a: Xeffect[Exception, int] = unsafe_function("foo")
        ```
        """

        def inner(*args: P.args, **kwargs: P.kwargs) -> "Xeffect[Exception, X]":
            return Xeffect.from_unsafe(lambda: f(*args, **kwargs))

        return inner

    def __repr__(self) -> str:
        return f"{self.branch} : {self.value}"

    @curry_method
    def __check_branch(
        self, branch: XFXBranch, f: Callable[[Self], "Xeffect[E, E]"]
    ) -> "Xeffect[E, E]":
        if self.branch == branch:
            return f(self)
        else:
            return self

    def map(self, f: Callable[[X], E]) -> "Xeffect[Y, E]":
        """Alias for map_right."""
        return self.map_right(f)

    def map_left(self, f: Callable[[Y], E]) -> "Xeffect[E, X]":
        """Return either itself or a new Xeffect (LEFT) containing the result of f.

        Is mainly used to chain effect free operations.

        ### Return

        - if self is a RIGHT -- self
        - if self is a LEFT  -- a new Xeffect, being a copy of the current effect with the underlying value = f(self.value)

        ### Usage

        see map_right
        """
        return self.__check_branch(XFXBranch.LEFT)(
            lambda x: Xeffect(x.branch, f(x.value))
        )

    def map_right(self, f: Callable[[X], E]) -> "Xeffect[Y, E]":
        """Return either itself or a new Xeffect (RIGHT) containing the result of f.

        ### Return

        - if self is a LEFT  -- self
        - if self is a RIGHT -- a new Xeffect, being a copy of the current effect with the underlying value = f(self.value)

        ### Usage

        ```python
            def add_three(i: float) -> float:
                return i + 3

            def pow(i: float) -> float:
                return i * i

            (
                Xeffect
                    .from_optional(3)            # Xeffect(XFXBranch.RIGHT, 3)
                    .map_right(add_three)        # Xeffect(XFXBranch.RIGHT, 6)
                    .map_right(pow)              # Xeffect(XFXBranch.RIGHT, 36)
                    .map_right(lambda x: x - 4)  # Xeffect(XFXBranch.RIGHT, 32)
            )
        ```
        """
        return self.__check_branch(XFXBranch.RIGHT)(
            lambda x: Xeffect(x.branch, f(x.value))
        )

    def flatten(self) -> "Xeffect[E, E]":
        """Alias for flatten_right."""
        return self.flatten_right()

    def flatten_left(self) -> "Xeffect[E, E]":
        """Return either self or a new flat Xeffect if the underlying value is an Xeffect.

        ### Return

        - if self.value is an Xeffect, and branch = LEFT -- a new Xeffect being the underlying value
        - otherwise                                      -- self

        ### Usage

        see flatten_right
        """
        return self.__check_branch(XFXBranch.LEFT)(
            lambda x: x.value if isinstance(x.value, Xeffect) else x
        )

    def flatten_right(self) -> "Xeffect[E, E]":
        """Return either self or a new flat Xeffect if the underlying value is an Xeffect.

        ### Return

        - if self.value is an Xeffect, and branch = RIGHT -- a new Xeffect being the underlying value
        - otherwise                                       -- self

        ### Usage

        ```python
            assert Xeffect.right(Xeffect.right("example")).flatten_right() == Xeffect(XFXBranch.RIGHT, "example")
            assert Xeffect.right("example").flatten_right() == Xeffect(XFXBranch.RIGHT, "example")
            assert Xeffect.right(Xeffect.from_optional(None)).flatten_right() == Xeffect(XFXBranch.LEFT, None)
            assert Xeffect.right(Xeffect.left("example")).flatten_right() == Xeffect(XFXBranch.LEFT, "example")
        ```
        """
        return self.__check_branch(XFXBranch.RIGHT)(
            lambda x: x.value if isinstance(x.value, Xeffect) else x
        )

    def flat_map(self, f: Callable[[X], E]) -> "Xeffect[Y, E]":
        """Alias for flat_map_right."""
        return self.flat_map_right(f)

    def flat_map_left(self, f: Callable[[Y], E]) -> "Xeffect[E, X]":
        """Return the result of map_left then flatten.

        ### Return

        - if self is a RIGHT -- self
        - if self is a LEFT  -- a new Xeffect, map_left then flatten

        ### Usage

        see flat_map
        """
        return self.map_left(f).flatten_left()

    def flat_map_right(self, f: Callable[[X], E]) -> "Xeffect[Y, E]":
        """Return the result of map_right then flatten.

        ### Return

        - if self is a LEFT  -- self
        - if self is a RIGHT -- a new Xeffect, map_right then flatten

        ### Usage

        ```python
            @Xeffect.safed
            def invert(i: float) -> float:
                return 1 / i

            @Xeffect.safed
            def sqrt(i: float) -> float:
                return math.sqrt(i)

            (
                Xeffect
                    .right(4)               # Xeffect(XFXBranch.RIGHT, 4)
                    .flat_map_right(invert) # Xeffect(XFXBranch.RIGHT, 0.25)
                    .flat_map_right(sqrt)   # Xeffect(XFXBranch.RIGHT, 0.5)
            )
            (
                Xeffect
                    .right(0)               # Xeffect(XFXBranch.RIGHT, 0)
                    .flat_map_right(invert) # Xeffect(XFXBranch.LEFT, ZeroDivisionError(...))
                    .flat_map_right(sqrt)   # Xeffect(XFXBranch.LEFT, ZeroDivisionError(...))
            )
            (
                Xeffect
                    .right(-4)              # Xeffect(XFXBranch.RIGHT, -4)
                    .flat_map_right(invert) # Xeffect(XFXBranch.RIGHT, -0.25)
                    .flat_map_right(sqrt)   # Xeffect(XFXBranch.LEFT, ValueError(...))
            )
        """
        return self.map_right(f).flatten_right()

    @curry_method
    def fold(self, default: E, f: Callable[[Y | X], E]) -> E:
        """Return default if branch != RIGHT, otherwise f(self.value).

        Exists as homogenisation with Xlist.fold

        ### Keyword Arguments

        - default -- output when the value does not exist on the RIGHT side
        - f       -- transformation to apply to the underlying value before returning
                     when the value is present on the RIGHT side

        ### Usage

        ```python
            def load_dated_partition(partition_value: date) -> str:
                return "actual partition"


            @Xeffect.safed
            def to_date(str_date: str) -> date:
                print(date.fromisoformat(str_date))
                return date.fromisoformat(str_date)

            data = to_date("2024-05-01").fold("default partition")(load_dated_partition)
            # good date -> date parsed by to_date() -> fold() calls load_dated_partition

            data = to_date("2023-02-29").fold("default partition")(load_dated_partition)
            # wrong date -> LEFT bias returned by to_date() -> fold returns "default partition"
        ```
        """
        if self.branch == XFXBranch.RIGHT:
            return f(self.value)
        else:
            return default

    def get_or_else(self, default: Y | X) -> Y | X:
        """Shorthand for self.fold(default)(id)

        ### Usage
        ```python
            @Xeffect.safed
            def to_date(str_date: str) -> date:
                return date.fromisoformat(str_date)

            gotten_date = to_date("2024-05-01").get_or_else(date.today())
            else_date   = to_date("2023-02-29").get_or_else(date.today())
        ```
        """
        return self.fold(default)(lambda x: x)

    def foreach(self, statement: Callable[[X], Any]) -> None:
        """Alias for foreach_right."""
        self.foreach_right(statement)

    def foreach_left(self, statement: Callable[[Y], Any]) -> None:
        """Do the statement procedure to the underlying value if self is a LEFT.

        ### Usage

        see foreach_right
        """
        self.__check_branch(XFXBranch.LEFT)(lambda s: Xeffect.left(statement(s.value)))

    def foreach_right(self, statement: Callable[[X], Any]) -> None:
        """Do the statement procedure to the underlying value if self is a RIGHT.

        ### Usage
        ```python
            (
                Xeffect
                    .from_optional(25)
                    .foreach(lambda x: print(f"This is the left element : {x}"))
            )
            # This is an element of the list : 25

            (
                Xeffect
                    .from_optional(None)
                    .foreach(lambda x: print(f"This is the left element : {x}"))
            )
            # doesn't output anything

            (
                Xeffect(XFXBranch.RIGHT, 25)
                    .foreach(lambda x: print(f"This is the left element : {x}"))
            )
            # doesn't output anything
        ```
        """
        self.__check_branch(XFXBranch.RIGHT)(
            lambda s: Xeffect.right(statement(s.value))
        )

    def recover_with(self, f: Callable[[Y], E]) -> "Xeffect[E, X]":
        """Alias for recover_with_right."""
        return self.recover_with_right(f)

    def recover_with_left(self, f: Callable[[X], E]) -> "Xeffect[Y, E]":
        """Return the result of the flat_map on the opposite branch.

        See flat_map_right

        ### Usage

        See recover_with_right
        """
        return self.flat_map_right(f)

    def recover_with_right(self, f: Callable[[Y], E]) -> "Xeffect[E, X]":
        """Return the result of the flat_map on the opposite branch.

        See flat_map_left

        ### Usage

        ```python
            @Xeffect.safed
            def invert(i: float) -> float:
                return 1 / i

            @Xeffect.safed
            def sqrt(i: float) -> float:
                return math.sqrt(i)

            (
                sqrt(-4)                                      # Xeffect(XFXBranch.LEFT, ValueError(...))
                    .recover_with_right(lambda _: invert(-4)) # Xeffect(XFXBranch.RIGHT, -0.25)
            )

            (
                sqrt(4)                                       # Xeffect(XFXBranch.RIGHT, 2)
                    .recover_with_right(lambda _: invert(-4)) # Xeffect(XFXBranch.RIGHT, 2)
            )
        ```
        """
        return self.flat_map_left(f)

    def recover(self, f: Callable[[Y], E]) -> "Xeffect[None, E |X]":
        """Alias for recover_right."""
        return self.recover_right(f)

    def recover_left(self, f: Callable[[X], E]) -> "Xeffect[Y | E, None]":
        """Return a new effect with is always a LEFT.

        Used to convert a RIGHT effect into a LEFT using an effectless transformation.
        Semantically :
        Used to fallback on a potential failure with an effectless operation.
        This is a fallback that always ends up as a 'success'.

        ### Return

        - if branch == LEFT -- self
        - otherwise         -- a new effect, having branch = LEFT, with an inherent value of f(self.value)

        ### Usage

        See recover_right
        """
        return self.__check_branch(XFXBranch.RIGHT)(lambda s: Xeffect.left(f(s.value)))

    def recover_right(self, f: Callable[[Y], E]) -> "Xeffect[None, E | X]":
        """Return a new effect with is always a RIGHT.

        Used to convert a LEFT effect into a RIGHT using an effectless transformation.
        Semantically :
        Used to fallback on a potential failure with an effectless operation.
        This is a fallback that always ends up as a 'success'.

        ### Return

        - if branch == RIGHT -- self
        - otherwise          -- a new effect, having branch = RIGHT, with an inherent value of f(self.value)

        ### Usage

        ```python
            @Xeffect.safed
            def sqrt(i: float) -> float:
                return math.sqrt(i)

            (
                sqrt(-4)                        # Xeffect(XFXBranch.LEFT, ValueError(...))
                    .recover_right(lambda _: 0) # Xeffect(XFXBranch.RIGHT, 0)
            )
            (
                sqrt(4)                         # Xeffect(XFXBranch.RIGHT, 2)
                    .recover_right(lambda _: 0) # Xeffect(XFXBranch.RIGHT, 2)
            )
        ```
        """
        return self.__check_branch(XFXBranch.LEFT)(lambda s: Xeffect.right(f(s.value)))

    def filter(self, predicate: Callable[[X], bool]) -> "Xeffect[Y | XeffectError, X]":
        """Alias for filter_right."""
        return self.filter_right(predicate)

    def filter_left(
        self, predicate: Callable[[Y], bool]
    ) -> "Xeffect[Y, X | XeffectError]":
        """Return a new effect with the branch = RIGHT if the predicate is not met.

        Fill the effect with a default error mentioning the initial value in case of branch switching.

        ### Return

        - if branch != LEFT               -- self
        - if branch == LEFT and predicate -- self
        - otherwise                       -- a new effect, having branch = RIGHT, with value = XeffectError(self)

        ### Usage

        see filter_right
        """
        return self.__check_branch(XFXBranch.LEFT)(
            lambda s: s if predicate(s.value) else Xeffect.right(XeffectError(s))
        )

    def filter_right(
        self, predicate: Callable[[X], bool]
    ) -> "Xeffect[Y | XeffectError, X]":
        """Return a new effect with the branch = LEFT if the predicate is not met.

        Fill the effect with a default error mentioning the initial value in case of branch switching.

        ### Return

        - if branch != RIGHT               -- self
        - if branch == RIGHT and predicate -- self
        - otherwise                       -- a new effect, having branch = LEFT, with value = XeffectError(self)

        ### Usage

        ```python

            (
                Xeffect
                    .right(4)                 # Xeffect(XFXBranch.RIGHT, 4)
                    .filter(lambda x: x < 10) # Xeffect(XFXBranch.RIGHT, 4)
                    .filter(lambda x: x > 10) # Xeffect(XFXBranch.LEFT, XeffectError(Xeffect.right(4)))
                    .filter(lambda _: True)   # Xeffect(XFXBranch.LEFT, XeffectError(Xeffect.right(4)))
                    .filter(lambda _: False)  # Xeffect(XFXBranch.LEFT, XeffectError(Xeffect.right(4)))
            )
        ```
        """
        return self.__check_branch(XFXBranch.RIGHT)(
            lambda s: s if predicate(s.value) else Xeffect.left(XeffectError(s))
        )
