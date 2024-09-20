from abc import ABC, abstractmethod
from typing import override

from xfp import Xiter, Xlist, curry


class Sink[T](ABC):
    def __init__(self) -> None:
        self.value = None

    @abstractmethod
    def fill(self, value: T) -> None:
        pass


class Appender[T](Sink[T]):
    def __init__(self) -> None:
        self.value: list[T] = []

    @override
    def fill(self, value: T) -> None:
        self.value.append(value)


@curry
def forced_side_effect[T](sink: Sink[T], value: T) -> T:
    sink.fill(value)
    return value


def test_xlist_eager():
    sink = Appender()
    eager_value = forced_side_effect(sink)
    assert sink.value == []
    r1 = Xlist([1, 2, 3]).map(lambda x: eager_value(x))
    assert sink.value == [1, 2, 3]
    _ = r1.flat_map(lambda x: eager_value([eager_value(x)]))
    assert sink.value == [1, 2, 3, 1, [1], 2, [2], 3, [3]]


def test_xiter_lazy():
    sink = Appender()
    eager_value = forced_side_effect(sink)
    assert sink.value == []
    r1 = Xiter([1, 2, 3]).map(lambda x: eager_value(x))
    assert sink.value == []
    r2 = r1.flat_map(lambda x: eager_value([eager_value(x)]))
    assert sink.value == []
    r2.foreach(print)
    assert sink.value == [1, 1, [1], 2, 2, [2], 3, 3, [3]]
    r2.foreach(print)
    assert sink.value == [1, 1, [1], 2, 2, [2], 3, 3, [3]]
