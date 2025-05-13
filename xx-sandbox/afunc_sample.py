import trio

from dataclasses import dataclass, replace

from xfp import Xresult, XRBranch
from xfp.a import funcbox, Afunc, ARfunc


@dataclass
class Sample:
    db: str
    id: int


class ProcessError(Exception):
    pass


@ARfunc
async def get_sample(db: str, id: int) -> Xresult[Exception, Sample]:
    print(f"Getting ({db=},{id=})...")
    await trio.sleep(1)
    if 0 <= id < 50:
        return Xresult(Sample(db, id), XRBranch.RIGHT)
    return Xresult(ValueError(f"({db=},{id=}) not found"), XRBranch.LEFT)


@ARfunc
async def process_sample(s: Sample) -> Xresult[Exception, Sample]:
    "dummy process that fail for even ids"
    print(f"Processing {s} ...")
    await trio.sleep(1)
    if s.id % 2:
        return Xresult(ProcessError(f"process error for {s.id=}"), XRBranch.LEFT)
    return Xresult(replace(s), XRBranch.RIGHT)


@Afunc
async def get_default(e: Exception) -> Sample:
    print(f"Recovering {e} ...")
    await trio.sleep(1)
    return Sample("DEFAULT_DB", 0)


async def functional_task(db: str, id: int) -> None:
    result = await get_sample(db, id).flat_map(process_sample).recover(get_default)
    print(f"FUNCTIONAL TASK({db=},{id=}) -> {result}")


async def main() -> None:
    async with trio.open_nursery() as nursery:
        nursery.start_soon(funcbox.background_tick, 6)
        await trio.sleep(0.5)
        nursery.start_soon(functional_task, "MY_DB", 42)
        nursery.start_soon(functional_task, "MY_DB", 13)


trio.run(main)
