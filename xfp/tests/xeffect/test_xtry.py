from xfp import XTry, Xeffect, XFXBranch


def test_from_unsafe_lift_success():
    def input():
        return 3

    expected = XTry.Success(3)
    actual = XTry.from_unsafe(input)

    assert actual == expected


def test_from_unsafe_lift_failure():
    def input():
        raise Exception("fail")

    actual = XTry.from_unsafe(input)

    assert isinstance(actual.value, Exception)


def test_safed_lift_success():
    @XTry.safed
    def actual():
        return 3

    expected = XTry.Success(3)

    assert actual() == expected


def test_safed_lift_failure():
    @XTry.safed
    def actual():
        raise Exception("fail")

    assert isinstance(actual().value, Exception)


def test_xtry_instantiate_xeffect():
    success = XTry.Success(3)
    failure = XTry.Failure(Exception("fail"))

    assert isinstance(success, Xeffect)
    assert isinstance(failure, Xeffect)
    assert success == Xeffect(3, XFXBranch.RIGHT)
    assert failure.branch == XFXBranch.LEFT


def test_success_can_be_pattern_match():
    match Xeffect(3, XFXBranch.RIGHT):
        case XTry.Success(v):
            assert v == 3
        case _:
            assert False


def test_failure_can_be_pattern_match():
    match Xeffect(Exception("fail"), XFXBranch.LEFT):
        case XTry.Failure(e):
            assert isinstance(e, Exception) and e.args[0] == "fail"
        case _:
            assert False


def test_empty_do_not_false_positive():
    match Xeffect(None, XFXBranch.LEFT):
        case XTry.Failure(_):
            assert False
        case _:
            assert True
