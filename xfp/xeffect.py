<<<<<<< Updated upstream
from typing import Callable, Any, Self, cast
=======
from typing import Callable, Any, Literal, ParamSpec, cast
>>>>>>> Stashed changes
from enum import Enum
from dataclasses import dataclass
from .utils import E


P = ParamSpec("P")


XFXBranch = Enum("XFXBranch", ["LEFT", "RIGHT"])


@dataclass(frozen=True)
class Xeffect[X: E, Y: E]:
    """Encapsulate Union type in container.

    Semantically, Xeffect helps managing unpure types, such as :
    - nullable values (Xeffect[X, None])
    - tryable values (Xeffect[X, Error])
    Eventually using it for plain encapsulated Union type is fine.
    Attributes:
    branch -- XFXBranch (LEFT, RIGHT), semaphore telling if the value attribute is an X (LEFT) or a Y (RIGHT)
    value  -- X | Y, the content of the container
    bias   -- XFXBranch (LEFT, RIGHT), default = LEFT. Tells in which cases non specific operations (such as map and flat_map) applies
    It brings:
    Monadic behavior through :
    - map_left
    - map_right
    - map
    - flat_map_left
    - flat_map_right
    - flat_map
    - flatten
    - foreach_left
    - foreach_right
    Manual handling of the bias:
    - biased
    Class method to lift values to Xeffect:
    - lift
    - from_optional
    - from_unsafe
    Usages:
    - directly returns Xeffect in your own functions:
        def f_that_breaks(should_break: boolean) -> Xeffect[str, Error]:
            if should_break:
                return Xeffect(XFXBranch.RIGHT, Error("something went wrong"))
            else:
                return Xeffect(XFXBranch.LEFT, "Everything's fine")
    - catch common functions into Xeffect:
        effect_result: Xeffect[E, Error] = Xeffect.from_unsafe(some_function_that_raises)
    - powerful optional handling:
        optional_value: Int | None = 3
        option_value: Xeffect[int, None] = Xeffect.from_optional(optional_value)
    - rich union type:
        def returns_a_str_or_int(should_be_str: boolean) -> Xeffect[str, int]:
            if should_be_str:
                return Xeffect(XFXBranch.LEFT, "foo")
            else:
                return Xeffect(XFXBranch.RIGHT, 42)
    """

    branch: XFXBranch
    value: X | Y
    bias: XFXBranch = XFXBranch.LEFT

    @classmethod
    def lift(cls, value: X) -> "Xeffect[X, E]":
        """Return an Xeffect (always LEFT) from a value."""
        return Xeffect(XFXBranch.LEFT, value)

    @classmethod
    def from_optional(cls, value: X | None) -> "Xeffect[X, None]":
        """Return an Xeffect from an optional value.

        value:
        X -- Return a LEFT
        None -- Return a RIGHT
        """
        match value:
            case None:
                return Xeffect(XFXBranch.RIGHT, value)
            case _:
                return Xeffect(XFXBranch.LEFT, value)

    @classmethod
    def from_unsafe(cls, f: Callable[[], X]) -> "Xeffect[X, Exception]":
        """Return the result of a function as an Xeffect.

        Execute the callable and catch the result :
        Callable returns -- wrap the result in a LEFT
        Callable raises -- wrap the Exception in a RIGHT
        """
        try:
            return Xeffect(XFXBranch.LEFT, f())
        except Exception as e:
            return Xeffect(XFXBranch.RIGHT, e)

    @classmethod
    def safed(cls, f: Callable[P, E]) -> Callable[P, "Xeffect[E, Exception]"]:
        def inner(*args: P.args, **kwargs: P.kwargs):
            return Xeffect.from_unsafe(lambda: f(*args, **kwargs))
        return inner

    def __repr__(self) -> str:
        return f"{self.branch} : {self.value}"

    def __check_branch(
        self, branch: XFXBranch
    ) -> Callable[[Callable[[Self], "Xeffect[E, E]"]], "Xeffect[E, E]"]:
        def inner(f: Callable[[Self], "Xeffect[E, E]"]) -> "Xeffect[E, E]":
            if self.branch == branch:
                return f(self)
            else:
                return self

        return inner

    def set_bias(self, bias: XFXBranch) -> "Xeffect[X, Y]":
        """Return a new effect with the set bias."""
        return Xeffect(self.branch, self.value, bias)

    def map(self, f: Callable[[X | Y], E]) -> "Xeffect[E, E]":
        """Apply either map_left or map_right on f depending on the bias.

        Is mainly used to chain effect free operations.
        Return:
        if bias == branch -- a new Xeffect, with value = f(self.value)
        otherwise         -- self
        Usage:
        def add_three(i: float) -> float:
            return i + 3

        def pow(i: float) -> float:
            return i * i

        (
            Xeffect
                .lift(3)               # Xeffect(XFXBranch.LEFT, 3, XFXBranch.LEFT)
                .map(add_three)        # Xeffect(XFXBranch.LEFT, 6, XFXBranch.LEFT)
                .map(pow)              # Xeffect(XFXBranch.LEFT, 36, XFXBranch.LEFT)
                .map(lambda x: x - 4)  # Xeffect(XFXBranch.LEFT, 32, XFXBranch.LEFT)
        )
        """
        return self.__check_branch(self.bias)(
            lambda s: Xeffect(s.branch, f(s.value), s.bias)
        )

    def map_left(self, f: Callable[[X], E]) -> "Xeffect[E, Y]":
        """Return either itself or a new Xeffect (LEFT) containing the result of f.

        Return:
        if self is a RIGHT -- self
        if self is a LEFT  -- a new Xeffect, being a copy of the current effect with the
                              underlying value = f(self.value)
        Usage:
        see map
        """
        return (
            self.set_bias(XFXBranch.LEFT)
            .map(cast(Callable[[X | Y], E], f))
            .set_bias(self.bias)
        )

    def map_right(self, f: Callable[[Y], E]) -> "Xeffect[X, E]":
        """Return either itself or a new Xeffect (RIGHT) containing the result of f.

        Return:
        if self is a LEFT  -- self
        if self is a RIGHT -- a new Xeffect, being a copy of the current effect with the
                              underlying value = f(self.value)
        Usage:
        see map
        """
        return (
            self.set_bias(XFXBranch.RIGHT)
            .map(cast(Callable[[X | Y], E], f))
            .set_bias(self.bias)
        )

    def flatten(self) -> "Xeffect[E, E]":
        """Return either self or a new flat Xeffect if the underlying value is an Xeffect.

        Return:
        if self.value is an Xeffect -- a new Xeffect being a copy of the underlying value
        otherwise                   -- self
        Usage:
        assert Xeffect.lift(Xeffect.lift("example")).flatten() == Xeffect(XFXBranch.LEFT, "example", XFXBranch.LEFT)
        assert Xeffect.lift("example").flatten() == Xeffect(XFXBranch.LEFT, "example", XFXBranch.LEFT)
        assert Xeffect.lift(Xeffect.from_optional(None)) == Xeffect(XFXBranch.RIGHT, None, XFXBranch.LEFT)
        """
        return self.__check_branch(self.bias)(
            lambda x: x.value if isinstance(x.value, Xeffect) else x
        )

    def flatten_left(self) -> "Xeffect[E, E]":
        """Return either self or a new flat Xeffect if the underlying value is an Xeffect.

        Raise:
        TypeError -- when the underlying value is an Xeffect with a different bias from the wrapping Xeffect, and flattening should happen
        Return:
        if self.value is an Xeffect, and branch = bias = LEFT -- a new Xeffect being a copy of the underlying value
        otherwise                                             -- self
        Usage:
        see flatten
        """
        return self.set_bias(XFXBranch.LEFT).flatten().set_bias(self.bias)

    def flatten_right(self) -> "Xeffect[E, E]":
        """Return either self or a new flat Xeffect if the underlying value is an Xeffect.

        Raise:
        TypeError -- when the underlying value is an Xeffect with a different bias from the wrapping Xeffect, and flattening should happen
        Return:
        if self.value is an Xeffect, and branch = bias = RIGHT -- a new Xeffect being a copy of the underlying value
        otherwise                                              -- self
        Usage:
        see flatten
        """
        return self.set_bias(XFXBranch.RIGHT).flatten().set_bias(self.bias)

    def flat_map(self, f: Callable[[X | Y], E]) -> "Xeffect[E, E]":
        """Return the result of map then flatten.

        Is mainly used to chain effectful operations.
        Raise:
        TypeError -- if f(self.value) returns an effect with a LEFT bias
        Return:
        if bias == branch -- a new Xeffect, map then flatten
        otherwise         -- self
        Usage:
        def invert(i: float) -> Xeffect[float, Exception]:
            return Xeffect.from_unsafe(lambda _: 1 / i)

         def sqrt(i: float) -> Xeffect[float, Exception]:
            return Xeffect.from_unsafe(lambda _: math.sqrt(i))

        (
            Xeffect
                .lift(4)) # Xeffect(XFXBranch.LEFT, 4, XFXBranch.LEFT)
                .flat_map(invert) # Xeffect(XFXBranch.LEFT, 0.25, XFXBranch.LEFT)
                .flat_map(sqrt)   # Xeffect(XFXBranch.LEFT, 0.5, XFXBranch.LEFT)
        )
        (
            Xeffect
                .lift(0)) # Xeffect(XFXBranch.LEFT, 0, XFXBranch.LEFT)
                .flat_map(invert) # Xeffect(XFXBranch.RIGHT, ZeroDivisionError(...), XFXBranch.LEFT)
                .flat_map(sqrt)   # Xeffect(XFXBranch.RIGHT, ZeroDivisionError(...), XFXBranch.LEFT)
        )
        (
            Xeffect
                .lift(-4)) # Xeffect(XFXBranch.LEFT, -4, XFXBranch.LEFT)
                .flat_map(invert) # Xeffect(XFXBranch.LEFT, -0.25, XFXBranch.LEFT)
                .flat_map(sqrt)   # Xeffect(XFXBranch.RIGHT, ValueError(...), XFXBranch.LEFT)
        )
        """
        return self.map(f).flatten()

    def flat_map_left(self, f: Callable[[X], E]) -> "Xeffect[E, Y]":
        """Return the result of map_left then flatten.

        Raise:
        TypeError -- if f(self.value) returns an effect with a RIGHT bias
        Return:
        if self is a RIGHT -- self
        if self is a LEFT  -- a new Xeffect, map_right then flatten
        Usage:
        see flat_map
        """
        return self.map_left(f).flatten_left()

    def flat_map_right(self, f: Callable[[Y], E]) -> "Xeffect[X, E]":
        """Return the result of map_right then flatten.

        Raise:
        TypeError -- if f(self.value) returns an effect with a LEFT bias
        Return:
        if self is a LEFT  -- self
        if self is a RIGHT -- a new Xeffect, map_right then flatten
        Usage:
        see flat_map
        """
        return self.map_right(f).flatten_right()

    def fold(self, default: E) -> Callable[[Callable[[X | Y], E]], E]:
        """Return default if branch != bias, otherwise f(self.value).

        Exists as homogenisation with Xlist.fold
        Keyword Arguments:
        default -- output when the value does not exist on the bias side
        f       -- transformation to apply to the underlying value before returning
                   when the value is present on the bias side
        Usage:
        def load_dated_partition(self, partition_value: date) -> list(str):
            return ...

        def to_date(str_date: str) -> Xeffect[date, Exception]:
            return Xeffect.from_unsafe(lambda _: date.fromisoformat(str_date))

        data = to_date("2024-05-01").fold(list())(load_dated_partition)
        """

        def inner(f: Callable[[X | Y], E]) -> E:
            if self.bias == self.branch:
                return f(self.value)
            else:
                return default

        return inner

    def get_or_else(self, default: X | Y) -> X | Y:
        """Shorthand for self.fold(default)(id)

        Usage:
        def to_date(str_date: str) -> Xeffect[date, Exception]:
            return Xeffect.from_unsafe(lambda _: date.fromisoformat(str_date))

        date_or_now = to_date("2024-05-01").get_or_else(date.today())
        """
        return self.fold(default)(lambda x: x)

    def foreach(self, statement: Callable[[X | Y], E]) -> None:
        """Do either foreach_left or foreach_right on statement depending on the bias.

        Usage:
        (
            Effect
                .from_optional(25)
                .foreach(lambda x: print(f"This is the left element : $x))
        )
        # This is an element of the list : 25
        (
            Effect
                .from_optional(None)
                .foreach(lambda x: print(f"This is the left element : $x))
        )
        # doesn't output anything
        (
            Effect(XFXBranch.RIGHT, 25, XFXBranch.LEFT)
                .foreach(lambda x: print(f"This is the left element : $x))
        )
        # doesn't output anything
        (
            Effect(XFXBranch.RIGHT, 25)
                .set_bias(XFXBranch.RIGHT)
                .foreach(lambda x: print(f"This is the left element : $x))
        )
        # This is an element of the list : 25
        """
        # lift for typechecking
        self.__check_branch(self.bias)(lambda s: Xeffect.lift(statement(s.value)))

    def foreach_left(self, statement: Callable[[X], Any]) -> None:
        """Do the statement procedure to the underlying value if self is a LEFT.

        Usage:
        see foreach
        """
        (self.set_bias(XFXBranch.LEFT).foreach(cast(Callable[[X | Y], E], statement)))

    def foreach_right(self, statement: Callable[[Y], Any]) -> None:
        """Do the statement procedure to the underlying value if self is a RIGHT.

        Usage:
        see foreach
        """
        (self.set_bias(XFXBranch.RIGHT).foreach(cast(Callable[[X | Y], E], statement)))
