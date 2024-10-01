from xfp import Xresult, XFXBranch, XresultError, Xlist


def test_xresult_map_left_do():
    input = Xresult(1, XFXBranch.LEFT)
    actual = input.map_left(lambda x: x + 2)
    expected = Xresult(3, XFXBranch.LEFT)

    assert actual == expected


def test_xresult_map_left_pass():
    input = Xresult(1, XFXBranch.RIGHT)
    actual = input.map_left(lambda x: x + 2)

    assert actual == input


def test_xresult_map_right_do():
    input = Xresult(1, XFXBranch.RIGHT)
    actual = input.map_right(lambda x: x + 2)
    expected = Xresult(3, XFXBranch.RIGHT)

    assert actual == expected


def test_xresult_map_right_pass():
    input = Xresult(1, XFXBranch.LEFT)
    actual = input.map_right(lambda x: x + 2)

    assert actual == input


def test_xresult_flatten():
    reduce = lambda x: x.value  # noqa: E731
    id = lambda x: x  # noqa: E731
    LEFT = XFXBranch.LEFT
    RIGHT = XFXBranch.RIGHT

    combinations = Xlist(
        [
            (Xresult(Xresult(3, RIGHT), LEFT), id),
            (Xresult(Xresult(3, LEFT), LEFT), id),
            (Xresult(Xresult(3, RIGHT), RIGHT), reduce),
            (Xresult(Xresult(3, LEFT), RIGHT), reduce),
            (Xresult(3, RIGHT), id),
            (Xresult(3, LEFT), id),
            (Xresult(3, RIGHT), id),
            (Xresult(3, LEFT), id),
        ]
    )

    result = combinations.map(
        lambda tuple: tuple[0].flatten() == tuple[1](tuple[0])
    ).reduce(lambda x, y: x and y)

    assert result


def test_xresult_flat_map_left_do():
    input = Xresult(1, XFXBranch.LEFT)
    actual = input.flat_map_left(lambda x: Xresult(x + 2, XFXBranch.LEFT))
    expected = Xresult(3, XFXBranch.LEFT)

    assert actual == expected


def test_xresult_flat_map_left_do_but_fail():
    input = Xresult(1, XFXBranch.LEFT)
    actual = input.flat_map_left(lambda x: Xresult(None, XFXBranch.RIGHT))
    expected = Xresult(None, XFXBranch.RIGHT)

    assert actual == expected


def test_xresult_flat_map_left_pass():
    input = Xresult(1, XFXBranch.RIGHT)
    actual = input.flat_map_left(lambda x: Xresult(x + 2, XFXBranch.LEFT))

    assert actual == input


def test_xresult_flat_map_right_do():
    input = Xresult(1, XFXBranch.RIGHT)
    actual = input.flat_map_right(lambda x: Xresult(x + 2, XFXBranch.RIGHT))
    expected = Xresult(3, XFXBranch.RIGHT)

    assert actual == expected


def test_xresult_flat_map_right_do_but_fail():
    input = Xresult(1, XFXBranch.RIGHT)
    actual = input.flat_map_right(lambda x: Xresult(None, XFXBranch.LEFT))
    expected = Xresult(None, XFXBranch.LEFT)

    assert actual == expected


def test_xresult_flat_map_right_pass():
    input = Xresult(1, XFXBranch.LEFT)
    actual = input.flat_map_right(lambda x: Xresult(x + 2, XFXBranch.RIGHT))

    assert actual == input


def test_xresult_fold_value():
    input = Xresult(1, XFXBranch.RIGHT)
    actual = input.fold(36)(lambda x: x + 2)
    expected = 3

    assert actual == expected


def test_xresult_fold_default():
    input = Xresult(1, XFXBranch.LEFT)
    actual = input.fold(36)(lambda x: x + 2)
    expected = 36

    assert actual == expected


def test_xresult_get_or_else_value():
    input = Xresult(1, XFXBranch.RIGHT)
    actual = input.get_or_else(36)
    expected = 1

    assert actual == expected


def test_xresult_get_or_else_default():
    input = Xresult(1, XFXBranch.LEFT)
    actual = input.get_or_else(36)
    expected = 36

    assert actual == expected


def test_xresult_recover_with_left_pass():
    input = Xresult(1, XFXBranch.LEFT)
    actual = input.recover_with_left(lambda _: Xresult(2, XFXBranch.RIGHT))

    assert actual == input


def test_xresult_recover_with_left_recover():
    input = Xresult(1, XFXBranch.RIGHT)
    expected = Xresult(2, XFXBranch.RIGHT)
    actual = input.recover_with_left(lambda _: expected)

    assert actual == expected


def test_xresult_recover_with_right_pass():
    input = Xresult(1, XFXBranch.RIGHT)
    actual = input.recover_with_right(lambda _: Xresult(2, XFXBranch.RIGHT))

    assert actual == input


def test_xresult_recover_with_right_recover():
    input = Xresult(1, XFXBranch.LEFT)
    expected = Xresult(2, XFXBranch.RIGHT)
    actual = input.recover_with_right(lambda _: expected)

    assert actual == expected


def test_xresult_recover_left_pass():
    input = Xresult(1, XFXBranch.LEFT)
    actual = input.recover_left(lambda _: 2)

    assert actual == input


def test_xresult_recover_left_do():
    input = Xresult(1, XFXBranch.RIGHT)
    expected = Xresult(2, XFXBranch.LEFT)
    actual = input.recover_left(lambda _: 2)

    assert actual == expected


def test_xresult_recover_right_pass():
    input = Xresult(1, XFXBranch.RIGHT)
    actual = input.recover_right(lambda _: 2)

    assert actual == input


def test_xresult_recover_right_do():
    input = Xresult(1, XFXBranch.LEFT)
    expected = Xresult(2, XFXBranch.RIGHT)
    actual = input.recover_right(lambda _: 2)

    assert actual == expected


def test_xresult_filter_left_pass():
    input = Xresult(3, XFXBranch.RIGHT)
    actual = input.filter_left(lambda x: x > 10)

    assert actual == input


def test_xresult_filter_left_do():
    input = Xresult(3, XFXBranch.LEFT)
    expected = Xresult(XresultError(input), XFXBranch.RIGHT)
    actual = input.filter_left(lambda x: x > 10)

    assert actual == expected


def test_xresult_filter_right_pass():
    input = Xresult(3, XFXBranch.LEFT)
    actual = input.filter_right(lambda x: x > 10)

    assert actual == input


def test_xresult_filter_right_do():
    input = Xresult(3, XFXBranch.RIGHT)
    expected = Xresult(XresultError(input), XFXBranch.LEFT)
    actual = input.filter_right(lambda x: x > 10)

    assert actual == expected
