from xfp import Xlist


def test_xlist_map():
    input = Xlist([1, 2, 3, 4])
    actual = input.map(lambda x: (x - 1) * -1)
    expected = Xlist([0, -1, -2, -3])

    assert actual == expected


def test_xlist_flat_map():
    input = Xlist([1, 2])
    actual = input.flat_map(lambda x: [x, x**2])
    expected = Xlist([1, 1, 2, 4])

    assert actual == expected


def test_xlist_filter():
    input = Xlist(range(1, 10, 1))
    actual = input.filter(lambda x: x % 2 == 0)
    expected = Xlist(range(2, 10, 2))

    assert actual == expected


def test_xlist_sorted():
    input = Xlist([4, 3, 1, 2])
    actual = input.sorted()
    expected = Xlist([1, 2, 3, 4])

    assert actual == expected


def test_xlist_min():
    input = Xlist([4, 3, -1, 2])
    actual = input.min()
    expected = -1

    assert actual == expected


def test_xlist_max():
    input = Xlist([4, 3, -1, 2])
    actual = input.max()
    expected = 4

    assert actual == expected
