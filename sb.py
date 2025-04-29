import random
import time
from typing import Never
from xfp import XRBranch, Xresult, Xtry, Xeffect
import trio
import math

################ IN USE ######################


class NetworkError(Exception):
    pass


@Xeffect
def api_call(id: int) -> Xresult[Exception, str]:
    "This is a documented function - how to get doc on wrapped Xeffect"
    names: dict[int, str] = {1: "bob", 2: "jack", 3: "john", 4: "mike"}
    random_delay = random.randrange(100) / 100
    time.sleep(random_delay)

    if random.randrange(100) < 80:
        return Xtry.Failure(NetworkError("Network Error"))

    name: str | None = names.get(id)
    if not name:
        return Xtry.Failure(ValueError("id not found"))

    return Xtry.Success(name)


##


async def parse(s: str) -> Xresult[ValueError, int]:
    await trio.sleep(0.5)
    return Xtry.from_unsafe(lambda: int(s))


async def recover(e: ValueError) -> Xresult[Never, int]:
    await trio.sleep(0.5)
    return Xtry.Success(42)


async def factorial(i: int) -> Xresult[ValueError, int]:
    await trio.sleep(0.5)
    return Xtry.from_unsafe(lambda: math.factorial(i))


# TODO - JE VEUX :
async def main() -> None:
    result: Xresult[ValueError, int] = parse("34").map_left(recover).map(factorial)

    if result.branch == XRBranch.LEFT:
        print("problem")
    else:
        print("All good")


trio.run(main)
