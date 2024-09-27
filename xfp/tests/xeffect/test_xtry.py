from xfp import Xtry, Xeffect, XFXBranch


def test_from_unsafe_lift_success():
    def input():
        return 3

    expected = Xtry.Success(3)
    actual = Xtry.from_unsafe(input)

    assert actual == expected


def test_from_unsafe_lift_failure():
    def input():
        raise Exception("fail")

    actual = Xtry.from_unsafe(input)

    assert isinstance(actual.value, Exception)


def test_safed_lift_success():
    @Xtry.safed
    def actual():
        return 3

    expected = Xtry.Success(3)

    assert actual() == expected


def test_safed_lift_failure():
    @Xtry.safed
    def actual():
        raise Exception("fail")

    assert isinstance(actual().value, Exception)


def test_Xtry_instantiate_xeffect():
    success = Xtry.Success(3)
    failure = Xtry.Failure(Exception("fail"))

    assert isinstance(success, Xeffect)
    assert isinstance(failure, Xeffect)
    assert success == Xeffect(3, XFXBranch.RIGHT)
    assert failure.branch == XFXBranch.LEFT


def test_success_can_be_pattern_match():
    match Xeffect(3, XFXBranch.RIGHT):
        case Xtry.Success(v):
            assert v == 3
        case _:
            assert False


def test_failure_can_be_pattern_match():
    match Xeffect(Exception("fail"), XFXBranch.LEFT):
        case Xtry.Failure(e):
            assert isinstance(e, Exception) and e.args[0] == "fail"
        case _:
            assert False


def test_empty_do_not_false_positive():
    match Xeffect(None, XFXBranch.LEFT):
        case Xtry.Failure(_):
            assert False
        case _:
            assert True
