from typing import Callable, Any, cast
from enum import Enum
from dataclasses import dataclass
from utils import E, Unused


XFXBranch = Enum("XFXBranch", ["LEFT", "RIGHT"])


@dataclass(frozen=True)
class Xeffect[X: E, Y: E]:
    branch: XFXBranch
    value: X | Y
    bias: XFXBranch = XFXBranch.LEFT

    @classmethod
    def from_optional(cls, value: T | None) -> Self:
        return cls(cls.__key, value, None)

    @classmethod
    def from_unsafe(cls, f: Callable) -> Self:
        try:
            return cls(cls.__key, f(), None)
        except Exception as e:
            return cls(cls.__key, None, e)

    def __init__(self, key: object, left: T | None, right: E | None) -> None:
        if self.__key is not key:
            raise Exception("Constructor can only be accessible from inside Xeffect")
        self.left_value = left
        self.right_value = right

    # TODO: make it work
    def left(self) -> Iterator:
        return filter(lambda x: x is not None, [self.left_value])

    # TODO: make it work
    def right(self) -> Iterator:
        return filter(lambda x: x is not None, [self.right_value])

    # TODO: make it work
    def __iter__(self) -> Iterator:
        return self.left()

    def __repr__(self) -> str:
        return repr({"left": repr(self.left_value), "right": repr(self.right_value)})

    def map[U](self, f: Callable) -> "Xeffect":
        if self.left_value is not None:
            return Xeffect(self.__key, f(self.left_value), None)
        else:
            return Xeffect(self.__key, None, self.right_value)

    def flatMap(self, f: Callable) -> "Xeffect":
        if self.left_value is not None:
            return f(self.left_value)
        else:
            return Xeffect(self.__key, None, self.right_value)

    def foreach(self, statement: Callable) -> None:
        if self.left_value is not None:
            statement(self.left_value)

    # TODO : implements
    def mapErr[U](self, f: Callable):  # -> "Xeffect"
        pass

    # TODO : recover / recoverWith ?
    # TODO : implements
    def flatMapErr(self, f: Callable):  # -> "Xeffect"
        pass

    # TODO : implements
    def foreachErr(self, statement: Callable) -> None:
        pass

    # TODO : implements
    def transform(
        self, left_transform: Callable, right_transform: Callable
    ):  # -> Xeffect
        pass
