from xfp import Xiter


def test_xiter_map():
    input = Xiter([1, 2, 3, 4])
    actual = input.map(lambda x: (x - 1) * -1)
    expected = Xiter([0, -1, -2, -3])

    assert actual == expected


def test_xiter_flatten():
    input = Xiter([[1, 2], [3]])
    actual = input.flatten()
    expected = Xiter([1, 2, 3])

    assert actual == expected


def test_xiter_flatten_id():
    input = Xiter([1, 2, 3])
    actual = input.flatten()
    expected = Xiter([1, 2, 3])

    assert actual == expected


def test_xiter_flatten_mixed():
    input = Xiter([[1, 2], 3])
    actual = input.flatten()
    expected = Xiter([1, 2, 3])

    assert actual == expected


def test_xiter_flat_map():
    input = Xiter([1, 2])
    actual = input.flat_map(lambda x: [x, x**2])
    expected = Xiter([1, 1, 2, 4])

    assert actual == expected


def test_xiter_filter():
    input = Xiter(range(1, 10, 1))
    actual = input.filter(lambda x: x % 2 == 0)
    expected = Xiter(range(2, 10, 2))

    assert actual == expected
