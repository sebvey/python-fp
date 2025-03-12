from . import Xdict, Xlist, Xiter


def count[X](xl: Xlist[X] | Xiter[X]) -> Xdict[X, int]:
    """Returns the count of each elements of the Xlist/Xiter as a Xdict."""

    return xl.fold_left(
        Xdict[X, int]({}), lambda acc, el: acc.updated(el, acc.get(el, 0) + 1)
    )
