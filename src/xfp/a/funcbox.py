from typing import Any
from . import ARfunc, Afunc
from .. import Xresult, XRBranch

print_stdlib = print


@ARfunc
async def print_ar(o: Any) -> Xresult[Exception, None]:
    "Print ARfunc (returning Xresult)"
    try:
        print(o)
        return Xresult(None, XRBranch.RIGHT)
    except Exception as e:
        return Xresult(e, XRBranch.LEFT)


@Afunc
async def print(o: Any) -> None:
    "Print Afunc (returning None)"
    print_stdlib(o)
