from xfp import Xeffect, XFXBranch, Xlist


def test_xeffect_set_bias():
    input = Xeffect(XFXBranch.LEFT, None, XFXBranch.LEFT)
    actual = input.set_bias(XFXBranch.RIGHT)
    expected = Xeffect(XFXBranch.LEFT, None, XFXBranch.RIGHT)

    assert actual == expected


def test_xeffect_map_left_do():
    input = Xeffect(XFXBranch.LEFT, 1, XFXBranch.LEFT)
    actual = input.map_left(lambda x: x + 2)
    expected = Xeffect(XFXBranch.LEFT, 3, XFXBranch.LEFT)

    assert actual == expected


def test_xeffect_map_left_pass():
    input = Xeffect(XFXBranch.RIGHT, 1, XFXBranch.LEFT)
    actual = input.map_left(lambda x: x + 2)

    assert actual == input


def test_xeffect_map_right_do():
    input = Xeffect(XFXBranch.RIGHT, 1, XFXBranch.RIGHT)
    actual = input.map_right(lambda x: x + 2)
    expected = Xeffect(XFXBranch.RIGHT, 3, XFXBranch.RIGHT)

    assert actual == expected


def test_xeffect_map_right_pass():
    input = Xeffect(XFXBranch.LEFT, 1, XFXBranch.RIGHT)
    actual = input.map_right(lambda x: x + 2)

    assert actual == input


def test_xeffect_flatten():
    reduce = lambda x: x.value  # noqa: E731
    id = lambda x: x  # noqa: E731
    LEFT = XFXBranch.LEFT
    RIGHT = XFXBranch.RIGHT

    combinations = Xlist(
        [
            (Xeffect(LEFT, Xeffect(RIGHT, 3, RIGHT), RIGHT), id),
            (Xeffect(LEFT, Xeffect(RIGHT, 3, LEFT), RIGHT), id),
            (Xeffect(LEFT, Xeffect(LEFT, 3, RIGHT), RIGHT), id),
            (Xeffect(LEFT, Xeffect(LEFT, 3, LEFT), RIGHT), id),
            (Xeffect(RIGHT, Xeffect(RIGHT, 3, RIGHT), LEFT), id),
            (Xeffect(RIGHT, Xeffect(RIGHT, 3, LEFT), LEFT), id),
            (Xeffect(RIGHT, Xeffect(LEFT, 3, RIGHT), LEFT), id),
            (Xeffect(RIGHT, Xeffect(LEFT, 3, LEFT), LEFT), id),
            (Xeffect(LEFT, Xeffect(RIGHT, 3, LEFT), LEFT), reduce),
            (Xeffect(LEFT, Xeffect(LEFT, 3, LEFT), LEFT), reduce),
            (Xeffect(RIGHT, Xeffect(RIGHT, 3, RIGHT), RIGHT), reduce),
            (Xeffect(RIGHT, Xeffect(LEFT, 3, RIGHT), RIGHT), reduce),
            (Xeffect(RIGHT, 3, RIGHT), id),
            (Xeffect(LEFT, 3, RIGHT), id),
            (Xeffect(RIGHT, 3, LEFT), id),
            (Xeffect(LEFT, 3, LEFT), id),
        ]
    )

    result = combinations.map(
        lambda tuple: tuple[0].flatten() == tuple[1](tuple[0])
    ).reduce(lambda x, y: x and y)

    assert result


def test_xeffect_flat_map_left_do():
    input = Xeffect(XFXBranch.LEFT, 1, XFXBranch.LEFT)
    actual = input.flat_map_left(lambda x: Xeffect.left(x + 2))
    expected = Xeffect(XFXBranch.LEFT, 3, XFXBranch.RIGHT)

    assert actual == expected


def test_xeffect_flat_map_left_do_but_fail():
    input = Xeffect(XFXBranch.LEFT, 1, XFXBranch.LEFT)
    actual = input.flat_map_left(lambda x: Xeffect.right(None))
    expected = Xeffect.right(None)

    assert actual == expected


def test_xeffect_flat_map_left_pass():
    input = Xeffect(XFXBranch.RIGHT, 1, XFXBranch.LEFT)
    actual = input.flat_map_left(lambda x: Xeffect.left(x + 2))

    assert actual == input


def test_xeffect_flat_map_right_do():
    input = Xeffect(XFXBranch.RIGHT, 1, XFXBranch.RIGHT)
    actual = input.flat_map_right(lambda x: Xeffect.right(x + 2))
    expected = Xeffect(XFXBranch.RIGHT, 3, XFXBranch.RIGHT)

    assert actual == expected


def test_xeffect_flat_map_right_do_but_fail():
    input = Xeffect(XFXBranch.RIGHT, 1, XFXBranch.RIGHT)
    actual = input.flat_map_right(lambda x: Xeffect.left(None))
    expected = Xeffect.left(None)

    assert actual == expected


def test_xeffect_flat_map_right_pass():
    input = Xeffect(XFXBranch.LEFT, 1, XFXBranch.RIGHT)
    actual = input.flat_map_right(lambda x: Xeffect.right(x + 2))

    assert actual == input


def test_xeffect_fold_value():
    input = Xeffect(XFXBranch.LEFT, 1, XFXBranch.LEFT)
    actual = input.fold(36)(lambda x: x + 2)
    expected = 3

    assert actual == expected


def test_xeffect_fold_default():
    input = Xeffect(XFXBranch.RIGHT, 1, XFXBranch.LEFT)
    actual = input.fold(36)(lambda x: x + 2)
    expected = 36

    assert actual == expected


def test_xeffect_get_or_else_value():
    input = Xeffect(XFXBranch.LEFT, 1, XFXBranch.LEFT)
    actual = input.get_or_else(36)
    expected = 1

    assert actual == expected


def test_xeffect_get_or_else_default():
    input = Xeffect(XFXBranch.RIGHT, 1, XFXBranch.LEFT)
    actual = input.get_or_else(36)
    expected = 36

    assert actual == expected


def test_xeffect_recover_with_pass():
    input = Xeffect.right(1)
    actual = input.recover_with(lambda _: Xeffect.right(2))

    assert actual == input


def test_xeffect_recover_with_recover_do():
    input = Xeffect(XFXBranch.LEFT, 1, XFXBranch.RIGHT)
    expected = Xeffect.right(2)
    actual = input.recover_with(lambda _: expected)

    assert actual == expected


def test_xeffect_recover_with_left_pass_br():
    input = Xeffect(XFXBranch.LEFT, 1, XFXBranch.RIGHT)
    actual = input.recover_with_left(lambda _: Xeffect.right(2))

    assert actual == input


def test_xeffect_recover_with_left_recover_br():
    input = Xeffect(XFXBranch.RIGHT, 1, XFXBranch.RIGHT)
    expected = Xeffect.right(2)
    actual = input.recover_with_left(lambda _: expected)

    assert actual == expected


def test_xeffect_recover_with_left_pass_bl():
    input = Xeffect(XFXBranch.LEFT, 1, XFXBranch.LEFT)
    actual = input.recover_with_left(lambda _: Xeffect.right(2))

    assert actual == input


def test_xeffect_recover_with_left_recover_bl():
    input = Xeffect(XFXBranch.RIGHT, 1, XFXBranch.LEFT)
    expected = Xeffect.right(2)
    actual = input.recover_with_left(lambda _: expected)

    assert actual == expected


def test_xeffect_recover_with_right_pass_br():
    input = Xeffect(XFXBranch.RIGHT, 1, XFXBranch.RIGHT)
    actual = input.recover_with_right(lambda _: Xeffect.right(2))

    assert actual == input


def test_xeffect_recover_with_right_recover_br():
    input = Xeffect(XFXBranch.LEFT, 1, XFXBranch.RIGHT)
    expected = Xeffect.right(2)
    actual = input.recover_with_right(lambda _: expected)

    assert actual == expected


def test_xeffect_recover_with_right_pass_bl():
    input = Xeffect(XFXBranch.RIGHT, 1, XFXBranch.LEFT)
    actual = input.recover_with_right(lambda _: Xeffect.right(2))

    assert actual == input


def test_xeffect_recover_with_right_recover_bl():
    input = Xeffect(XFXBranch.LEFT, 1, XFXBranch.LEFT)
    expected = Xeffect.right(2)
    actual = input.recover_with_right(lambda _: expected)

    assert actual == expected


def test_xeffect_recover_pass():
    input = Xeffect.right(1)
    actual = input.recover(lambda _: 2)

    assert actual == input


def test_xeffect_recover_do():
    input = Xeffect(XFXBranch.LEFT, 2, XFXBranch.RIGHT)
    expected = Xeffect.right(10)
    actual = input.recover(lambda x: x * 5)

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
