from xfp import Xeffect, XFXBranch, XeffectError, Xlist


def test_xeffect_map_left_do():
    input = Xeffect(1, XFXBranch.LEFT)
    actual = input.map_left(lambda x: x + 2)
    expected = Xeffect(3, XFXBranch.LEFT)

    assert actual == expected


def test_xeffect_map_left_pass():
    input = Xeffect(1, XFXBranch.RIGHT)
    actual = input.map_left(lambda x: x + 2)

    assert actual == input


def test_xeffect_map_right_do():
    input = Xeffect(1, XFXBranch.RIGHT)
    actual = input.map_right(lambda x: x + 2)
    expected = Xeffect(3, XFXBranch.RIGHT)

    assert actual == expected


def test_xeffect_map_right_pass():
    input = Xeffect(1, XFXBranch.LEFT)
    actual = input.map_right(lambda x: x + 2)

    assert actual == input


def test_xeffect_flatten():
    reduce = lambda x: x.value  # noqa: E731
    id = lambda x: x  # noqa: E731
    LEFT = XFXBranch.LEFT
    RIGHT = XFXBranch.RIGHT

    combinations = Xlist(
        [
            (Xeffect(Xeffect(3, RIGHT), LEFT), id),
            (Xeffect(Xeffect(3, LEFT), LEFT), id),
            (Xeffect(Xeffect(3, RIGHT), RIGHT), reduce),
            (Xeffect(Xeffect(3, LEFT), RIGHT), reduce),
            (Xeffect(3, RIGHT), id),
            (Xeffect(3, LEFT), id),
            (Xeffect(3, RIGHT), id),
            (Xeffect(3, LEFT), id),
        ]
    )

    result = combinations.map(
        lambda tuple: tuple[0].flatten() == tuple[1](tuple[0])
    ).reduce(lambda x, y: x and y)

    assert result


def test_xeffect_flat_map_left_do():
    input = Xeffect(1, XFXBranch.LEFT)
    actual = input.flat_map_left(lambda x: Xeffect(x + 2, XFXBranch.LEFT))
    expected = Xeffect(3, XFXBranch.LEFT)

    assert actual == expected


def test_xeffect_flat_map_left_do_but_fail():
    input = Xeffect(1, XFXBranch.LEFT)
    actual = input.flat_map_left(lambda x: Xeffect(None, XFXBranch.RIGHT))
    expected = Xeffect(None, XFXBranch.RIGHT)

    assert actual == expected


def test_xeffect_flat_map_left_pass():
    input = Xeffect(1, XFXBranch.RIGHT)
    actual = input.flat_map_left(lambda x: Xeffect(x + 2, XFXBranch.LEFT))

    assert actual == input


def test_xeffect_flat_map_right_do():
    input = Xeffect(1, XFXBranch.RIGHT)
    actual = input.flat_map_right(lambda x: Xeffect(x + 2, XFXBranch.RIGHT))
    expected = Xeffect(3, XFXBranch.RIGHT)

    assert actual == expected


def test_xeffect_flat_map_right_do_but_fail():
    input = Xeffect(1, XFXBranch.RIGHT)
    actual = input.flat_map_right(lambda x: Xeffect(None, XFXBranch.LEFT))
    expected = Xeffect(None, XFXBranch.LEFT)

    assert actual == expected


def test_xeffect_flat_map_right_pass():
    input = Xeffect(1, XFXBranch.LEFT)
    actual = input.flat_map_right(lambda x: Xeffect(x + 2, XFXBranch.RIGHT))

    assert actual == input


def test_xeffect_fold_value():
    input = Xeffect(1, XFXBranch.RIGHT)
    actual = input.fold(36)(lambda x: x + 2)
    expected = 3

    assert actual == expected


def test_xeffect_fold_default():
    input = Xeffect(1, XFXBranch.LEFT)
    actual = input.fold(36)(lambda x: x + 2)
    expected = 36

    assert actual == expected


def test_xeffect_get_or_else_value():
    input = Xeffect(1, XFXBranch.RIGHT)
    actual = input.get_or_else(36)
    expected = 1

    assert actual == expected


def test_xeffect_get_or_else_default():
    input = Xeffect(1, XFXBranch.LEFT)
    actual = input.get_or_else(36)
    expected = 36

    assert actual == expected


def test_xeffect_recover_with_left_pass():
    input = Xeffect(1, XFXBranch.LEFT)
    actual = input.recover_with_left(lambda _: Xeffect(2, XFXBranch.RIGHT))

    assert actual == input


def test_xeffect_recover_with_left_recover():
    input = Xeffect(1, XFXBranch.RIGHT)
    expected = Xeffect(2, XFXBranch.RIGHT)
    actual = input.recover_with_left(lambda _: expected)

    assert actual == expected


def test_xeffect_recover_with_right_pass():
    input = Xeffect(1, XFXBranch.RIGHT)
    actual = input.recover_with_right(lambda _: Xeffect(2, XFXBranch.RIGHT))

    assert actual == input


def test_xeffect_recover_with_right_recover():
    input = Xeffect(1, XFXBranch.LEFT)
    expected = Xeffect(2, XFXBranch.RIGHT)
    actual = input.recover_with_right(lambda _: expected)

    assert actual == expected


def test_xeffect_recover_left_pass():
    input = Xeffect(1, XFXBranch.LEFT)
    actual = input.recover_left(lambda _: 2)

    assert actual == input


def test_xeffect_recover_left_do():
    input = Xeffect(1, XFXBranch.RIGHT)
    expected = Xeffect(2, XFXBranch.LEFT)
    actual = input.recover_left(lambda _: 2)

    assert actual == expected


def test_xeffect_recover_right_pass():
    input = Xeffect(1, XFXBranch.RIGHT)
    actual = input.recover_right(lambda _: 2)

    assert actual == input


def test_xeffect_recover_right_do():
    input = Xeffect(1, XFXBranch.LEFT)
    expected = Xeffect(2, XFXBranch.RIGHT)
    actual = input.recover_right(lambda _: 2)

    assert actual == expected


def test_xeffect_filter_left_pass():
    input = Xeffect(3, XFXBranch.RIGHT)
    actual = input.filter_left(lambda x: x > 10)

    assert actual == input


def test_xeffect_filter_left_do():
    input = Xeffect(3, XFXBranch.LEFT)
    expected = Xeffect(XeffectError(input), XFXBranch.RIGHT)
    actual = input.filter_left(lambda x: x > 10)

    assert actual == expected


def test_xeffect_filter_right_pass():
    input = Xeffect(3, XFXBranch.LEFT)
    actual = input.filter_right(lambda x: x > 10)

    assert actual == input


def test_xeffect_filter_right_do():
    input = Xeffect(3, XFXBranch.RIGHT)
    expected = Xeffect(XeffectError(input), XFXBranch.LEFT)
    actual = input.filter_right(lambda x: x > 10)

    assert actual == expected
