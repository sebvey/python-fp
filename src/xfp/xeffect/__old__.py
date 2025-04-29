from dataclasses import dataclass
import functools
import time
from typing import Callable, ParamSpec
from xfp import XRBranch, Xresult
from abc import ABC, abstractmethod

P = ParamSpec("P")
type XEF[L, R] = Callable[P, Xresult[L, R]]

### RETRIER ###############################


class Retrier(ABC):
    @abstractmethod
    def retried_xef[L, R](
        self,
        f: XEF[L, R],
    ) -> XEF[L, R]:
        pass


@dataclass
class SimpleRetrier[L](Retrier):
    retries: int
    delay: int
    left_filter: Callable[[L], bool] = lambda _: True

    def __post_init__(self) -> None:
        if self.retries < 1:
            raise ValueError("Retries must be one or more")
        if self.delay <= 0:
            raise ValueError("Delay must be > 0")

    def retried_xef[R](self, f: XEF[L, R]) -> XEF[L, R]:
        @functools.wraps(f)
        def _retried_xef(*args, **kwargs) -> Xresult[L, R]:
            def loop(attempt: int, f: XEF[L, R]) -> Xresult[L, R]:
                print(f"attempt {attempt} ...")
                result: Xresult[L, R] = f(*args, **kwargs)
                print(f"loop result: {repr(result)}")

                if result.branch == XRBranch.LEFT:
                    if not self.left_filter(result.value):
                        print("LEFT, but not a value to retry")
                        return result
                    if attempt == self.retries:
                        print("Left, value to retry, but done trying ... it's enough")
                        return result
                    time.sleep(self.delay)
                    return loop(attempt + 1, f)
                return result

            return loop(0, f)

        return _retried_xef


###### 1 - XEFFECT ################################


class Xeffect[L, R]:
    def __init__(self, f: XEF[L, R]) -> None:
        self._xef = f

    def __call__(self, *args, **kwds):
        return self._xef(*args, **kwds)

    def retried(self, retrier: Retrier) -> XEF[L, R]:
        return Xeffect(retrier.retried_xef(self._xef))
