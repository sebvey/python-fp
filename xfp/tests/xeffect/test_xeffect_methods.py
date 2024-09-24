from xfp import Xeffect, XFXBranch, XeffectError, Xlist


def test_xeffect_map_left_do():
    input = Xeffect(XFXBranch.LEFT, 1)
    actual = input.map_left(lambda x: x + 2)
    expected = Xeffect(XFXBranch.LEFT, 3)

    assert actual == expected


def test_xeffect_map_left_pass():
    input = Xeffect(XFXBranch.RIGHT, 1)
    actual = input.map_left(lambda x: x + 2)

    assert actual == input


def test_xeffect_map_right_do():
    input = Xeffect(XFXBranch.RIGHT, 1)
    actual = input.map_right(lambda x: x + 2)
    expected = Xeffect(XFXBranch.RIGHT, 3)

    assert actual == expected


def test_xeffect_map_right_pass():
    input = Xeffect(XFXBranch.LEFT, 1)
    actual = input.map_right(lambda x: x + 2)

    assert actual == input


def test_xeffect_flatten():
    reduce = lambda x: x.value  # noqa: E731
    id = lambda x: x  # noqa: E731
    LEFT = XFXBranch.LEFT
    RIGHT = XFXBranch.RIGHT

    combinations = Xlist(
        [
            (Xeffect(LEFT, Xeffect(RIGHT, 3)), id),
            (Xeffect(LEFT, Xeffect(LEFT, 3)), id),
            (Xeffect(RIGHT, Xeffect(RIGHT, 3)), reduce),
            (Xeffect(RIGHT, Xeffect(LEFT, 3)), reduce),
            (Xeffect(RIGHT, 3), id),
            (Xeffect(LEFT, 3), id),
            (Xeffect(RIGHT, 3), id),
            (Xeffect(LEFT, 3), id),
        ]
    )

    result = combinations.map(
        lambda tuple: tuple[0].flatten() == tuple[1](tuple[0])
    ).reduce(lambda x, y: x and y)

    assert result


def test_xeffect_flat_map_left_do():
    input = Xeffect(XFXBranch.LEFT, 1)
    actual = input.flat_map_left(lambda x: Xeffect.left(x + 2))
    expected = Xeffect(XFXBranch.LEFT, 3)

    assert actual == expected


def test_xeffect_flat_map_left_do_but_fail():
    input = Xeffect(XFXBranch.LEFT, 1)
    actual = input.flat_map_left(lambda x: Xeffect.right(None))
    expected = Xeffect.right(None)

    assert actual == expected


def test_xeffect_flat_map_left_pass():
    input = Xeffect(XFXBranch.RIGHT, 1)
    actual = input.flat_map_left(lambda x: Xeffect.left(x + 2))

    assert actual == input


def test_xeffect_flat_map_right_do():
    input = Xeffect(XFXBranch.RIGHT, 1)
    actual = input.flat_map_right(lambda x: Xeffect.right(x + 2))
    expected = Xeffect(XFXBranch.RIGHT, 3)

    assert actual == expected


def test_xeffect_flat_map_right_do_but_fail():
    input = Xeffect(XFXBranch.RIGHT, 1)
    actual = input.flat_map_right(lambda x: Xeffect.left(None))
    expected = Xeffect.left(None)

    assert actual == expected


def test_xeffect_flat_map_right_pass():
    input = Xeffect(XFXBranch.LEFT, 1)
    actual = input.flat_map_right(lambda x: Xeffect.right(x + 2))

    assert actual == input


def test_xeffect_fold_value():
    input = Xeffect(XFXBranch.RIGHT, 1)
    actual = input.fold(36)(lambda x: x + 2)
    expected = 3

    assert actual == expected


def test_xeffect_fold_default():
    input = Xeffect(XFXBranch.LEFT, 1)
    actual = input.fold(36)(lambda x: x + 2)
    expected = 36

    assert actual == expected


def test_xeffect_get_or_else_value():
    input = Xeffect(XFXBranch.RIGHT, 1)
    actual = input.get_or_else(36)
    expected = 1

    assert actual == expected


def test_xeffect_get_or_else_default():
    input = Xeffect(XFXBranch.LEFT, 1)
    actual = input.get_or_else(36)
    expected = 36

    assert actual == expected


def test_xeffect_recover_with_left_pass():
    input = Xeffect(XFXBranch.LEFT, 1)
    actual = input.recover_with_left(lambda _: Xeffect.right(2))

    assert actual == input


def test_xeffect_recover_with_left_recover():
    input = Xeffect(XFXBranch.RIGHT, 1)
    expected = Xeffect.right(2)
    actual = input.recover_with_left(lambda _: expected)

    assert actual == expected


def test_xeffect_recover_with_right_pass():
    input = Xeffect(XFXBranch.RIGHT, 1)
    actual = input.recover_with_right(lambda _: Xeffect.right(2))

    assert actual == input


def test_xeffect_recover_with_right_recover():
    input = Xeffect(XFXBranch.LEFT, 1)
    expected = Xeffect.right(2)
    actual = input.recover_with_right(lambda _: expected)

    assert actual == expected


def test_xeffect_recover_left_pass():
    input = Xeffect.left(1)
    actual = input.recover_left(lambda _: 2)

    assert actual == input


def test_xeffect_recover_left_do():
    input = Xeffect.right(1)
    expected = Xeffect.left(2)
    actual = input.recover_left(lambda _: 2)

    assert actual == expected


def test_xeffect_recover_right_pass():
    input = Xeffect.right(1)
    actual = input.recover_right(lambda _: 2)

    assert actual == input


def test_xeffect_recover_right_do():
    input = Xeffect.left(1)
    expected = Xeffect.right(2)
    actual = input.recover_right(lambda _: 2)

    assert actual == expected


def test_xeffect_filter_left_pass():
    input = Xeffect(XFXBranch.RIGHT, 3)
    actual = input.filter_left(lambda x: x > 10)

    assert actual == input


def test_xeffect_filter_left_do():
    input = Xeffect(XFXBranch.LEFT, 3)
    expected = Xeffect(XFXBranch.RIGHT, XeffectError(input))
    actual = input.filter_left(lambda x: x > 10)

    assert actual == expected


def test_xeffect_filter_right_pass():
    input = Xeffect(XFXBranch.LEFT, 3)
    actual = input.filter_right(lambda x: x > 10)

    assert actual == input


def test_xeffect_filter_right_do():
    input = Xeffect(XFXBranch.RIGHT, 3)
    expected = Xeffect(XFXBranch.LEFT, XeffectError(input))
    actual = input.filter_right(lambda x: x > 10)

    assert actual == expected
