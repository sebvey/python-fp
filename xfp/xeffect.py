from typing import Callable, Any, cast
from enum import Enum
from dataclasses import dataclass
from .utils import E, Unused


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
    def lift(cls, value: X) -> "Xeffect[X, Unused]":
        return cls(XFXBranch.LEFT, value)

    @classmethod
    def from_optional(cls, value: X | None) -> "Xeffect[X, None]":
        match value:
            case None:
                return cls(XFXBranch.RIGHT, value)
            case _:
                return cls(XFXBranch.LEFT, value)

    @classmethod
    def from_unsafe(cls, f: Callable[[], X]) -> "Xeffect[X, Exception]":
        try:
            return cls(XFXBranch.LEFT, f())
        except Exception as e:
            return cls(XFXBranch.RIGHT, e)

    def __repr__(self) -> str:
        return f"${self.branch} : ${self.value}"

    def biased(self, bias: XFXBranch) -> "Xeffect[X, Y]":
        return Xeffect(self.branch, self.value, bias)

    def map_left(self, f: Callable[[X], E]) -> "Xeffect[E, Y]":
        match self.branch:
            case XFXBranch.LEFT:
                return Xeffect(self.branch, f(cast(X, self.value)), self.bias)
            case XFXBranch.RIGHT:
                return self

    def map_right(self, f: Callable[[Y], E]) -> "Xeffect[X, E]":
        match self.branch:
            case XFXBranch.RIGHT:
                return Xeffect(self.branch, f(cast(Y, self.value)), self.bias)
            case XFXBranch.LEFT:
                return self

    def map(self, f: Callable[[X | Y], E]) -> "Xeffect[E, E]":
        match self.bias:
            case XFXBranch.LEFT:
                return self.map_left(f)
            case XFXBranch.RIGHT:
                return self.map_right(f)

    def flatten(self) -> "Xeffect[E, E]":
        match self:
            case Xeffect(
                _, Xeffect(branch, value, in_bias), out_bias
            ) if in_bias == out_bias:
                return Xeffect(branch, value, out_bias)
            case Xeffect(_, Xeffect(_, _, _), _):
                raise TypeError(
                    f"Effect flattening can only work within same bias. Found ${self}"
                )
            case default:  # same bias, either plain value or wrong branch to flatten
                return default

    def flat_map_left(self, f: Callable[[X], E]) -> "Xeffect[E, Y]":
        match self.branch:
            case XFXBranch.LEFT:
                return (
                    Xeffect(self.branch, f(cast(X, self.value)), XFXBranch.LEFT)
                    .flatten()
                    .biased(self.bias)
                )
            case XFXBranch.RIGHT:
                return self

    def flat_map_right(self, f: Callable[[Y], E]) -> "Xeffect[X, E]":
        match self.branch:
            case XFXBranch.RIGHT:
                return (
                    Xeffect(self.branch, f(cast(Y, self.value)), XFXBranch.RIGHT)
                    .flatten()
                    .biased(self.bias)
                )
            case XFXBranch.LEFT:
                return self

    def flat_map(self, f: Callable[[X | Y], E]) -> "Xeffect[E, E]":
        match self.bias:
            case XFXBranch.LEFT:
                return self.flat_map_left(f)
            case XFXBranch.RIGHT:
                return self.flat_map_right(f)

    def fold(self, default: E) -> Callable[[Callable[[X | Y], E]], E]:
        def inner(f: Callable[[X | Y], E]) -> E:
            if self.bias == self.branch:
                return f(self.value)
            else:
                return default

        return inner

    def foreach_left(self, f: Callable[[X], Any]) -> None:
        match self.branch:
            case XFXBranch.LEFT:
                f(cast(X, self.value))
            case XFXBranch.RIGHT:
                pass

    def foreach_right(self, f: Callable[[Y], Any]) -> None:
        match self.branch:
            case XFXBranch.RIGHT:
                f(cast(Y, self.value))
            case XFXBranch.LEFT:
                pass
