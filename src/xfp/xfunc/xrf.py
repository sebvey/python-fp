from . import XRfunc
from .. import Xresult, XRBranch

print_stdlib = print


@XRfunc
async def print(i: int) -> Xresult[Exception, None]:
    "Print effect"
    try:
        print_stdlib(i)
        return Xresult(None, XRBranch.RIGHT)
    except Exception as e:
        return Xresult(e, XRBranch.LEFT)
