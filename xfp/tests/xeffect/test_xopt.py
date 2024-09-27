from xfp import XOpt, Xeffect, XFXBranch


def test_from_optional_lift_some():
    input = 3
    expected = XOpt.Some(3)
    actual = XOpt.from_optional(input)

    assert actual == expected


def test_from_optional_lift_none():
    input = None
    expected = XOpt.Empty
    actual = XOpt.from_optional(input)

    assert actual == expected


def test_xopt_instantiate_xeffect():
    some = XOpt.Some(3)
    empty = XOpt.Empty

    assert isinstance(some, Xeffect)
    assert isinstance(empty, Xeffect)
    assert some == Xeffect(3, XFXBranch.RIGHT)
    assert empty == Xeffect(None, XFXBranch.LEFT)


def test_some_can_be_pattern_match():
    match Xeffect(3, XFXBranch.RIGHT):
        case XOpt.Some(v):
            assert v == 3
        case _:
            assert False


def test_empty_can_be_pattern_match():
    match Xeffect(None, XFXBranch.LEFT):
        case XOpt.Empty:
            assert True
        case _:
            assert False


def test_empty_do_not_false_positive():
    match Xeffect(Exception("not empty"), XFXBranch.LEFT):
        case XOpt.Empty:
            assert False
        case _:
            assert True
