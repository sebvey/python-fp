from typing import Any
from . import XRfunc, Xfunc
from .. import Xresult, XRBranch


@XRfunc
async def print_xr(o: Any) -> Xresult[Exception, None]:
    "Print xrfunc (returning Xresult)"
    try:
        print(o)
        return Xresult(None, XRBranch.RIGHT)
    except Exception as e:
        return Xresult(e, XRBranch.LEFT)


@Xfunc
async def print_x(o: Any) -> None:
    "Print xfunc (returning None)"
    print(o)
