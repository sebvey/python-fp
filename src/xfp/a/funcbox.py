from typing import Any

import trio
from . import ARfunc, Afunc
from .. import Xresult, XRBranch

print_stdlib = print
type Sec = int


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


@Afunc
async def background_tick(duration: Sec) -> None:
    n = 0
    while n <= duration:
        print_stdlib("-")
        n += 1
        await trio.sleep(1)
