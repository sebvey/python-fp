from typing import Any, Generator, NoReturn
from xfp.xiter import Xiter


def infinite_gen() -> Generator[int, Any, NoReturn]:
    acc = 0
    while True:
        acc += 1
        acc %= 100
        yield acc


def test_xiter_from_generator() -> None:
    input = infinite_gen()
    xiter = Xiter(input)
    data = xiter.map(lambda x: x * 2)
    out = []
    for _, i in zip(range(10), data):
        out.append(i)

    expected = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
    assert out == expected
