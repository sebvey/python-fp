from typing import Any, Coroutine, Callable

from xfp import Xresult

# conventions
# L,R -> Left and Right of a Xresult
# R -> result (or right only)
# when composing, the same with suffix 'o' (other)

# UNUSED
type Co[R] = Coroutine[Any, Any, R]
type CoXR[L, R] = Coroutine[Any, Any, Xresult[L, R]]

# USED
type CoFunc[**P, R] = Callable[P, Coroutine[Any, Any, R]]
type CoFuncXR[**P, L, R] = Callable[P, Coroutine[Any, Any, Xresult[L, R]]]
