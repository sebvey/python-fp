from typing import Callable, Any, Self, cast, ParamSpec
from enum import Enum, auto
from dataclasses import dataclass
from .utils import E, curry_method


P = ParamSpec("P")


class XFXBranch(Enum):
    LEFT = auto()
    RIGHT = auto()

    def invert(self) -> "XFXBranch":
        return XFXBranch.RIGHT if self == XFXBranch.LEFT else XFXBranch.LEFT


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
    - bias   -- XFXBranch (LEFT, RIGHT), default = RIGHT. Tells in which cases non specific operations (such as map and flat_map) applies

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
    bias: XFXBranch = XFXBranch.RIGHT

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
        - Callable raises -- wrap the Exception in a LEFT
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

    @curry_method
    def __with_bias(
        self, bias: XFXBranch, f: Callable[[Self], "Xeffect[E, E]"]
    ) -> "Xeffect[E, E]":
        self_with_bias = self.set_bias(bias)
        result: "Xeffect[E, E]" = f(cast(Self, self_with_bias))
        return self if result is self_with_bias else result

    def set_bias(self, bias: XFXBranch) -> "Xeffect[Y, X]":
        """Return a new effect with the set bias."""
        return Xeffect(self.branch, self.value, bias)

    def map(self, f: Callable[[Y | X], E]) -> "Xeffect[E, E]":
        """Apply either map_left or map_right on f depending on the bias.

        Is mainly used to chain effect free operations.

        ### Return

        - if bias == branch -- a new Xeffect, with value = f(self.value)
        - otherwise         -- self

        ### Usage

        ```python
            def add_three(i: float) -> float:
                return i + 3

            def pow(i: float) -> float:
                return i * i

            (
                Xeffect
                    .from_optional(3)      # Xeffect(XFXBranch.RIGHT, 3, XFXBranch.RIGHT)
                    .map(add_three)        # Xeffect(XFXBranch.RIGHT, 6, XFXBranch.RIGHT)
                    .map(pow)              # Xeffect(XFXBranch.RIGHT, 36, XFXBranch.RIGHT)
                    .map(lambda x: x - 4)  # Xeffect(XFXBranch.RIGHT, 32, XFXBranch.RIGHT)
            )
        ```
        """
        return self.__check_branch(self.bias)(
            lambda s: Xeffect(s.branch, f(s.value), s.bias)
        )

    def map_left(self, f: Callable[[Y], E]) -> "Xeffect[E, X]":
        """Return either itself or a new Xeffect (LEFT) containing the result of f.

        ### Return

        - if self is a RIGHT -- self
        - if self is a LEFT  -- a new Xeffect, being a copy of the current effect with the underlying value = f(self.value)

        ### Usage

        see map
        """
        return self.__with_bias(XFXBranch.LEFT)(
            lambda s: s.map(cast(Callable[[Y | X], E], f))
        )

    def map_right(self, f: Callable[[X], E]) -> "Xeffect[Y, E]":
        """Return either itself or a new Xeffect (RIGHT) containing the result of f.

        ### Return

        - if self is a LEFT  -- self
        - if self is a RIGHT -- a new Xeffect, being a copy of the current effect with the underlying value = f(self.value)

        ### Usage

        see map
        """
        return self.__with_bias(XFXBranch.RIGHT)(
            lambda s: s.map(cast(Callable[[Y | X], E], f))
        )

    def flatten(self) -> "Xeffect[E, E]":
        """Return either self or a new flat Xeffect if the underlying value is an Xeffect.

        ### Return

        - if self.value is an Xeffect and bias == branch -- a new Xeffect being the underlying value
        - otherwise                   -- self

        ### Usage

        ```python
            assert Xeffect.right(Xeffect.right("example")).flatten() == Xeffect(XFXBranch.RIGHT, "example", XFXBranch.RIGHT)
            assert Xeffect.right("example").flatten() == Xeffect(XFXBranch.RIGHT, "example", XFXBranch.RIGHT)
            assert Xeffect.right(Xeffect.from_optional(None)).flatten() == Xeffect(XFXBranch.LEFT, None, XFXBranch.RIGHT)
            assert Xeffect.right(Xeffect(XFXBranch.LEFT, "example", XFXBranch.LEFT)).flatten() == Xeffect(XFXBranch.LEFT, "example", XFXBranch.LEFT)
        ```
        """
        return self.__check_branch(self.bias)(
            lambda x: x.value if isinstance(x.value, Xeffect) else x
        )

    def flatten_left(self) -> "Xeffect[E, E]":
        """Return either self or a new flat Xeffect if the underlying value is an Xeffect.

        ### Return

        - if self.value is an Xeffect, and branch = bias = LEFT -- a new Xeffect being the underlying value
        - otherwise                                             -- self

        ### Usage

        see flatten
        """
        return self.__with_bias(XFXBranch.LEFT)(lambda s: s.flatten())

    def flatten_right(self) -> "Xeffect[E, E]":
        """Return either self or a new flat Xeffect if the underlying value is an Xeffect.

        ### Return

        - if self.value is an Xeffect, and branch = bias = RIGHT -- a new Xeffect being the underlying value
        - otherwise                                              -- self

        ### Usage

        see flatten
        """
        return self.__with_bias(XFXBranch.LEFT)(lambda s: s.flatten())

    def flat_map(self, f: Callable[[Y | X], E]) -> "Xeffect[E, E]":
        """Return the result of map then flatten.

        Is mainly used to chain effectful operations.

        ### Return

        - if bias == branch -- a new Xeffect, map then flatten
        - otherwise         -- self

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
                    .right(4)         # Xeffect(XFXBranch.RIGHT, 4, XFXBranch.RIGHT)
                    .flat_map(invert) # Xeffect(XFXBranch.RIGHT, 0.25, XFXBranch.RIGHT)
                    .flat_map(sqrt)   # Xeffect(XFXBranch.RIGHT, 0.5, XFXBranch.RIGHT)
            )
            (
                Xeffect
                    .right(0) # Xeffect(XFXBranch.RIGHT, 0, XFXBranch.RIGHT)
                    .flat_map(invert) # Xeffect(XFXBranch.LEFT, ZeroDivisionError(...), XFXBranch.RIGHT)
                    .flat_map(sqrt)   # Xeffect(XFXBranch.LEFT, ZeroDivisionError(...), XFXBranch.RIGHT)
            )
            (
                Xeffect
                    .right(-4) # Xeffect(XFXBranch.RIGHT, -4, XFXBranch.RIGHT)
                    .flat_map(invert) # Xeffect(XFXBranch.RIGHT, -0.25, XFXBranch.RIGHT)
                    .flat_map(sqrt)   # Xeffect(XFXBranch.LEFT, ValueError(...), XFXBranch.RIGHT)
            )
        ```
        """
        return self.map(f).flatten()

    def flat_map_left(self, f: Callable[[Y], E]) -> "Xeffect[E, X]":
        """Return the result of map_left then flatten.

        ### Return

        - if self is a RIGHT -- self
        - if self is a LEFT  -- a new Xeffect, map_left then flatten

        ### Usage

        see flat_map
        """
        return self.__with_bias(XFXBranch.LEFT)(
            lambda s: s.flat_map(cast(Callable[[Y | X], E], f))
        )

    def flat_map_right(self, f: Callable[[X], E]) -> "Xeffect[Y, E]":
        """Return the result of map_right then flatten.

        ### Return

        - if self is a LEFT  -- self
        - if self is a RIGHT -- a new Xeffect, map_right then flatten

        ### Usage

        see flat_map
        """
        return self.__with_bias(XFXBranch.RIGHT)(
            lambda s: s.flat_map(cast(Callable[[Y | X], E], f))
        )

    @curry_method
    def fold(self, default: E, f: Callable[[Y | X], E]) -> E:
        """Return default if branch != bias, otherwise f(self.value).

        Exists as homogenisation with Xlist.fold

        ### Keyword Arguments

        - default -- output when the value does not exist on the bias side
        - f       -- transformation to apply to the underlying value before returning
                     when the value is present on the bias side

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
        if self.bias == self.branch:
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

    def foreach(self, statement: Callable[[Y | X], Any]) -> None:
        """Do either foreach_left or foreach_right on statement depending on the bias.

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
                Xeffect(XFXBranch.RIGHT, 25, XFXBranch.LEFT)
                    .foreach(lambda x: print(f"This is the left element : {x}"))
            )
            # doesn't output anything

            (
                Xeffect(XFXBranch.LEFT, 25)
                    .set_bias(XFXBranch.LEFT)
                    .foreach(lambda x: print(f"This is the left element : {x}"))
            )
            # This is an element of the list : 25
        ```
        """
        # lift for typechecking
        self.__check_branch(self.bias)(lambda s: Xeffect.right(statement(s.value)))

    def foreach_left(self, statement: Callable[[Y], Any]) -> None:
        """Do the statement procedure to the underlying value if self is a LEFT.

        ### Usage

        see foreach
        """
        self.set_bias(XFXBranch.LEFT).foreach(cast(Callable[[Y | X], E], statement))

    def foreach_right(self, statement: Callable[[X], Any]) -> None:
        """Do the statement procedure to the underlying value if self is a RIGHT.

        ### Usage

        see foreach
        """
        self.set_bias(XFXBranch.RIGHT).foreach(cast(Callable[[Y | X], E], statement))

    def recover_with(self, f: Callable[[Y | X], E]) -> "Xeffect[E, E]":
        return self.__with_bias(self.bias.invert())(lambda s: s.flat_map(f))

    def recover_with_left(self, f: Callable[[X], E]) -> "Xeffect[E, E]":
        return self.__with_bias(XFXBranch.LEFT)(
            lambda s: s.recover_with(cast(Callable[[X | Y], E], f))
        )

    def recover_with_right(self, f: Callable[[Y], E]) -> "Xeffect[E, E]":
        return self.__with_bias(XFXBranch.RIGHT)(
            lambda s: s.recover_with(cast(Callable[[X | Y], E], f))
        )
