import functools
from xfp import Xlist, Xeffect, XFXBranch
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
    .map(Xeffect.from_unsafe)
    .zip(dir(f))
    .filter(tupled(lambda effect, _: effect.branch == XFXBranch.RIGHT))
    .foreach(print)
)
