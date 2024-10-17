import functools
from xfp import Xlist, Xtry, XRBranch
from xfp.utils import tupled

print("@@@ EXPLORE Object @@@")


def f(a, b):
    return a + b


print("@@@ PYTHONIC STYLE @@@")

for g in dir(f):
    try:
        print((getattr(f, g)(), g))
    except Exception:
        pass


print("@@@ FUNCTIONAL STYLE @@@")

(
    Xlist(dir(f))
    .map(functools.partial(getattr, f))
    .map(Xtry.from_unsafe)
    .zip(dir(f))
    .filter(tupled(lambda result, _: result.branch == XRBranch.RIGHT))
    .foreach(print)
)
