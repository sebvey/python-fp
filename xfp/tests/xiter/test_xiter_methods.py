from dataclasses import dataclass
from xfp import Xiter


def compare[X](actual: Xiter[X], expected: Xiter[X]) -> bool:
    for i, j in zip(actual, expected):
        if i != j:
            return False
    return True


def test_xiter_copy():
    r1 = Xiter([1, 2, 3])
    r2 = r1.copy()
    assert next(r1) == 1
    assert next(r2) == 1


def test_xiter_copy_is_shallow():
    @dataclass
    class A:
        text: str

    r1 = Xiter([A("hello")])
    r2 = r1.copy()

    value1 = next(r1)
    value2 = next(r2)
    value1.text = "world"
    assert value2.text == value1.text


def test_xiter_deepcopy():
    r1 = Xiter([1, 2, 3])
    r2 = r1.deepcopy()
    assert next(r1) == 1
    assert next(r2) == 1


def test_xiter_deepcopy_is_deep():
    @dataclass
    class A:
        text: str

    r1 = Xiter([A("hello")])
    r2 = r1.deepcopy()
    value1 = next(r1)
    value2 = next(r2)

    value1.text = "world"
    assert value2.text == "hello"


def test_xiter_map():
    input = Xiter([1, 2, 3, 4])
    actual = input.map(lambda x: (x - 1) * -1)
    expected = Xiter([0, -1, -2, -3])

    assert compare(actual, expected)


def test_xiter_flatten():
    input = Xiter([[1, 2], [3]])
    actual = input.flatten()
    expected = Xiter([1, 2, 3])

    assert compare(actual, expected)


def test_xiter_flatten_id():
    input = Xiter([1, 2, 3])
    actual = input.flatten()
    expected = Xiter([1, 2, 3])

    assert compare(actual, expected)


def test_xiter_flatten_mixed():
    input = Xiter([[1, 2], 3])
    actual = input.flatten()
    expected = Xiter([1, 2, 3])

    assert compare(actual, expected)


def test_xiter_flat_map():
    input = Xiter([1, 2])
    actual = input.flat_map(lambda x: [x, x**2])
    expected = Xiter([1, 1, 2, 4])

    assert compare(actual, expected)


def test_xiter_filter():
    input = Xiter(range(1, 10, 1))
    actual = input.filter(lambda x: x % 2 == 0)
    expected = Xiter(range(2, 10, 2))

    assert compare(actual, expected)
