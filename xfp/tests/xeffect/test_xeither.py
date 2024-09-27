from xfp import XEither, Xeffect, XFXBranch


def test_xeither_instantiate_xeffect():
    right = XEither.Right(3)
    left = XEither.Left(2)

    assert isinstance(right, Xeffect)
    assert isinstance(left, Xeffect)
    assert right == Xeffect(3, XFXBranch.RIGHT)
    assert left == Xeffect(2, XFXBranch.LEFT)


def test_right_can_be_pattern_match():
    match Xeffect(3, XFXBranch.RIGHT):
        case XEither.Right(v):
            assert v == 3
        case _:
            assert False


def test_left_can_be_pattern_match():
    match Xeffect(2, XFXBranch.LEFT):
        case XEither.Left(v):
            assert v == 2
        case _:
            assert False
